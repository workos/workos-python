# @oagen-ignore-file
"""FeatureFlagsRuntimeClient: polling, readiness, notifications and shutdown."""

from __future__ import annotations

import json
import logging
import threading
from typing import Any, Callable, List

import pytest

from workos import WorkOSClient, create_public_client
from workos._errors import (
    AuthenticationError,
    AuthorizationError,
    ConfigurationError,
    NotFoundError,
    ServerError,
)
from workos.feature_flags.runtime import _configuration
from workos.feature_flags.runtime import (
    FeatureFlagsConfiguration,
    FeatureFlagsConfigurationError,
    FeatureFlagsRuntimeClient,
    FlagsChangedEvent,
    RuntimeStatus,
)

from tests.feature_flags_runtime.helpers import (
    API_KEY,
    BASE_URL,
    Collector,
    FlagServer,
    SyncBackend,
    eventually,
    flag,
    payload,
    rule,
)

Make = Callable[..., FeatureFlagsRuntimeClient]

ORDERED = payload(
    ordered=flag(
        "ordered",
        default_value=True,
        rules=[
            rule("flag_rule_1", False, "organization", "org_1"),
            rule("flag_rule_2", True, "user", "user_1"),
        ],
    ),
    workspace=flag("workspace", rules=[rule("flag_rule_3", True, "workspace", "ws_1")]),
)
CHANGED = payload(
    ordered=flag("ordered", default_value=False),
    added=flag("added", default_value=True),
)


class TestRequests:
    def test_polls_the_v2_endpoint_with_the_sdk_transport(
        self, server: FlagServer, make_runtime: Make
    ) -> None:
        server.respond(200, ORDERED)
        runtime = make_runtime(request_timeout=7)
        runtime.start()
        runtime.wait_until_ready(timeout=5)

        request = server.requests[0]
        assert request.method == "GET"
        assert request.url == f"{BASE_URL}/sdk/feature-flags?payload_version=2"
        assert request.headers["Authorization"] == f"Bearer {API_KEY}"
        assert "Python SDK/" in request.headers["User-Agent"]
        assert 0 < request.timeout <= 7

    def test_makes_no_request_until_started(
        self, server: FlagServer, make_runtime: Make
    ) -> None:
        runtime = make_runtime()
        assert runtime.is_enabled("ordered") is False
        assert server.requests == []

    def test_start_is_idempotent(
        self, server: FlagServer, make_runtime: Make, fast_polling: List[int]
    ) -> None:
        server.respond(200, ORDERED)
        runtime = make_runtime()
        runtime.start()
        runtime.start()
        server.wait_for_requests(3)
        assert server.max_in_flight == 1


class TestReadiness:
    def test_ready_after_the_first_successful_poll(
        self, server: FlagServer, make_runtime: Make
    ) -> None:
        server.respond(200, ORDERED)
        runtime = make_runtime()
        assert runtime.is_ready is False
        runtime.start()
        runtime.wait_until_ready(timeout=5)

        assert runtime.is_ready
        assert (
            runtime.is_enabled("ordered", {"user": "user_1", "organization": "org_1"})
            is False
        )
        assert runtime.is_enabled("ordered", {"user": "user_1"}) is True
        assert runtime.get_all_flags({"workspace": "ws_1"}) == {
            "ordered": True,
            "workspace": True,
        }
        status = runtime.status
        assert status.flag_count == 2
        assert status.refresh_count == 1
        assert status.last_successful_refresh_at is not None
        assert status.cache_age() is not None

    def test_bootstrap_is_ready_immediately_without_a_request(
        self, server: FlagServer, make_runtime: Make
    ) -> None:
        bootstrap = FeatureFlagsConfiguration.from_dict(ORDERED)
        runtime = make_runtime(bootstrap=bootstrap)
        runtime.wait_until_ready(timeout=0)

        assert runtime.is_enabled("ordered") is True
        assert runtime.status.last_successful_refresh_at is None
        assert runtime.status.cache_age() is None
        assert runtime.configuration is bootstrap
        assert server.requests == []

    def test_wait_times_out_without_a_configuration(self, make_runtime: Make) -> None:
        runtime = make_runtime()
        with pytest.raises(TimeoutError):
            runtime.wait_until_ready(timeout=0.01)

    def test_unready_client_serves_caller_defaults(self, make_runtime: Make) -> None:
        runtime = make_runtime()
        assert runtime.is_enabled("ordered", default=True) is True
        assert runtime.get_all_flags() == {}
        assert runtime.get_flag("ordered") is None

    def test_a_401_before_readiness_fails_the_wait(
        self, server: FlagServer, make_runtime: Make
    ) -> None:
        server.respond(401, {"message": "Unauthorized"})
        runtime = make_runtime()
        runtime.start()
        with pytest.raises(AuthenticationError):
            runtime.wait_until_ready(timeout=5)
        assert runtime.status.polling_stopped
        assert len(server.requests) == 1

    def test_closing_before_readiness_wakes_waiters(self, make_runtime: Make) -> None:
        runtime = make_runtime()
        errors: List[BaseException] = []

        def wait() -> None:
            try:
                runtime.wait_until_ready(timeout=5)
            except BaseException as error:
                errors.append(error)

        waiter = threading.Thread(target=wait)
        waiter.start()
        runtime.close()
        waiter.join(5)
        assert len(errors) == 1 and isinstance(errors[0], RuntimeError)


class TestChangeNotifications:
    def test_first_load_reports_every_flag(
        self, server: FlagServer, make_runtime: Make
    ) -> None:
        server.respond(200, ORDERED)
        changes = Collector()
        runtime = make_runtime(on_change=changes)
        runtime.start()

        (event,) = changes.wait_for(1)
        assert isinstance(event, FlagsChangedEvent)
        assert event.previous is None
        assert event.changed_flags == {"ordered", "workspace"}
        assert event.current is runtime.configuration

    def test_reports_only_real_changes(
        self, server: FlagServer, make_runtime: Make, fast_polling: List[int]
    ) -> None:
        server.respond(200, ORDERED)
        changes = Collector()
        runtime = make_runtime()
        runtime.add_change_listener(changes)
        runtime.start()
        changes.wait_for(1)
        server.wait_for_requests(4)
        assert len(changes.items) == 1

        server.respond(200, CHANGED)
        events = changes.wait_for(2)
        assert events[1].changed_flags == {"ordered", "workspace", "added"}
        assert events[1].previous is not None
        assert events[1].previous.to_json() == events[0].current.to_json()
        assert runtime.is_enabled("added") is True
        assert runtime.get_flag("workspace") is None

    def test_first_refresh_after_bootstrap_compares_with_the_bootstrap(
        self, server: FlagServer, make_runtime: Make
    ) -> None:
        bootstrap = FeatureFlagsConfiguration.from_dict(ORDERED)
        changes = Collector()
        statuses = Collector()
        server.respond(200, CHANGED)
        runtime = make_runtime(
            bootstrap=bootstrap, on_change=changes, on_status=statuses
        )
        runtime.refresh()

        (event,) = changes.wait_for(1)
        assert event.previous is bootstrap
        assert event.changed_flags == {"ordered", "workspace", "added"}

        runtime.refresh()
        assert len(changes.items) == 1
        assert len(statuses.items) == 2

    def test_an_unchanged_payload_keeps_the_snapshot_without_parsing_it(
        self, server: FlagServer, make_runtime: Make, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        server.respond(200, ORDERED)
        changes = Collector()
        runtime = make_runtime(on_change=changes)
        runtime.refresh()
        snapshot = runtime.configuration
        first_refresh = runtime.status.last_successful_refresh_at
        parses: List[object] = []
        original = _configuration._parse_payload
        monkeypatch.setattr(
            _configuration,
            "_parse_payload",
            lambda payload: parses.append(payload) or original(payload),
        )
        # Same content, different key order.
        server.respond(200, json.loads(json.dumps(ORDERED, sort_keys=True)))
        runtime.refresh()

        assert runtime.configuration is snapshot
        assert parses == []
        assert runtime.status.refresh_count == 2
        assert runtime.status.last_successful_refresh_at != first_refresh
        assert len(changes.items) == 1

        server.respond(200, CHANGED)
        runtime.refresh()
        assert len(parses) == 1
        assert runtime.configuration is not snapshot
        assert len(changes.items) == 2

    def test_an_identical_bootstrap_reports_no_change(
        self, server: FlagServer, make_runtime: Make
    ) -> None:
        server.respond(200, ORDERED)
        changes = Collector()
        runtime = make_runtime(
            bootstrap=FeatureFlagsConfiguration.from_dict(ORDERED), on_change=changes
        )
        runtime.refresh()
        assert changes.items == []

    def test_listener_failures_are_logged_and_do_not_stop_polling(
        self,
        server: FlagServer,
        make_runtime: Make,
        fast_polling: List[int],
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        server.respond(200, ORDERED)
        later = Collector()

        def broken(event: FlagsChangedEvent) -> None:
            raise RuntimeError("listener bug")

        runtime = make_runtime(on_change=broken)
        runtime.add_change_listener(later)
        with caplog.at_level(logging.ERROR, logger="workos.feature_flags.runtime"):
            runtime.start()
            later.wait_for(1)
            server.respond(200, CHANGED)
            later.wait_for(2)
        assert "listener raised" in caplog.text

    def test_removed_listeners_are_not_called(
        self, server: FlagServer, make_runtime: Make
    ) -> None:
        server.respond(200, ORDERED)
        changes = Collector()
        runtime = make_runtime(on_change=changes)
        runtime.remove_change_listener(changes)
        runtime.refresh()
        assert changes.items == []

    def test_async_listeners_are_rejected_with_a_warning(
        self, server: FlagServer, make_runtime: Make, caplog: pytest.LogCaptureFixture
    ) -> None:
        server.respond(200, ORDERED)

        async def listener(event: FlagsChangedEvent) -> None:
            raise AssertionError("never run")

        runtime = make_runtime()
        runtime.add_change_listener(listener)  # type: ignore[arg-type]
        with caplog.at_level(logging.WARNING, logger="workos.feature_flags.runtime"):
            runtime.refresh()
        assert "async listener" in caplog.text


class TestFailures:
    def test_transient_failures_are_retried_inside_one_refresh(
        self, server: FlagServer, make_runtime: Make, fast_polling: List[int]
    ) -> None:
        server.enqueue((503, {"message": "busy"}), (500, None))
        server.respond(200, ORDERED)
        runtime = make_runtime()
        runtime.refresh()

        assert len(server.requests) == 3
        assert runtime.status.refresh_count == 1
        assert runtime.status.failed_refresh_count == 0

    def test_retries_stop_when_the_request_timeout_is_spent(
        self, server: FlagServer, make_runtime: Make
    ) -> None:
        server.respond(503, {"message": "busy"})
        runtime = make_runtime(request_timeout=0.05)
        with pytest.raises(ServerError):
            runtime.refresh()
        # The shortest retry wait (0.25 s) does not fit in a 50 ms budget.
        assert len(server.requests) == 1

    @pytest.mark.parametrize("max_retries, requests", [(0, 1), (1, 2)])
    def test_retries_follow_the_clients_max_retries(
        self,
        server: FlagServer,
        fast_polling: List[int],
        max_retries: int,
        requests: int,
    ) -> None:
        server.respond(503, {"message": "busy"})
        workos = WorkOSClient(
            api_key=API_KEY,
            base_url=BASE_URL,
            http_client=SyncBackend(server),
            max_retries=max_retries,
        )
        runtime = workos.create_feature_flags_runtime_client()
        with pytest.raises(ServerError):
            runtime.refresh()
        assert len(server.requests) == requests
        runtime.close()
        workos.close()

    def test_errors_that_retrying_cannot_fix_are_not_retried(
        self, server: FlagServer, make_runtime: Make, fast_polling: List[int]
    ) -> None:
        server.respond(404, {"message": "Not Found"})
        runtime = make_runtime()
        with pytest.raises(NotFoundError):
            runtime.refresh()
        assert len(server.requests) == 1

    @pytest.mark.parametrize(
        "status, body, error_type",
        [
            (404, {"message": "Not Found"}, NotFoundError),
            (403, {"message": "Forbidden"}, AuthorizationError),
            (500, {"message": "Boom"}, ServerError),
            (200, {"version": 3, "flags": {}}, FeatureFlagsConfigurationError),
            (200, b"not json", FeatureFlagsConfigurationError),
        ],
    )
    def test_background_failures_keep_the_last_good_flags_and_recover(
        self,
        server: FlagServer,
        make_runtime: Make,
        fast_polling: List[int],
        status: int,
        body: Any,
        error_type: type,
    ) -> None:
        server.respond(200, ORDERED)
        errors = Collector()
        changes = Collector()
        runtime = make_runtime(on_error=errors, on_change=changes)
        runtime.start()
        changes.wait_for(1)
        good = runtime.configuration

        server.respond(status, body)
        (error, *_) = errors.wait_for(1)
        assert isinstance(error, error_type)
        assert runtime.configuration is good
        assert runtime.is_enabled("ordered", {"user": "user_1"}) is True
        assert isinstance(runtime.status.last_error, error_type)
        assert runtime.status.failed_refresh_count >= 1

        server.respond(200, CHANGED)
        changes.wait_for(2)
        eventually(lambda: runtime.status.last_error is None)
        assert runtime.status.polling_stopped is False

    def test_failures_back_off_and_reset_after_success(
        self, server: FlagServer, make_runtime: Make, fast_polling: List[int]
    ) -> None:
        server.enqueue(*[(404, {"message": "Not Found"})] * 3)
        server.respond(200, ORDERED)
        runtime = make_runtime()
        runtime.start()
        server.wait_for_requests(5)
        assert fast_polling[:4] == [1, 2, 3, 0]

    def test_a_401_stops_polling_and_keeps_the_last_good_flags(
        self, server: FlagServer, make_runtime: Make, fast_polling: List[int]
    ) -> None:
        server.respond(200, ORDERED)
        errors = Collector()
        statuses = Collector()
        runtime = make_runtime(on_error=errors, on_status=statuses)
        runtime.start()
        runtime.wait_until_ready(timeout=5)

        server.respond(401, {"message": "Unauthorized"})
        (error,) = errors.wait_for(1)
        assert isinstance(error, AuthenticationError)
        eventually(lambda: runtime.status.polling_stopped)
        sent = len(server.requests)
        threading.Event().wait(0.1)
        assert len(server.requests) == sent
        assert runtime.is_enabled("ordered", {"user": "user_1"}) is True
        runtime.wait_until_ready(timeout=0)
        last: RuntimeStatus = statuses.items[-1]
        assert last.polling_stopped and isinstance(last.last_error, AuthenticationError)

    def test_a_401_from_refresh_stops_polling(
        self, server: FlagServer, make_runtime: Make, fast_polling: List[int]
    ) -> None:
        server.respond(200, ORDERED)
        errors = Collector()
        statuses = Collector()
        runtime = make_runtime(on_error=errors, on_status=statuses)
        runtime.start()
        server.wait_for_requests(2)

        server.respond(401, {"message": "Unauthorized"})
        with pytest.raises(AuthenticationError):
            runtime.refresh()
        assert runtime.status.polling_stopped
        sent = len(server.requests)
        threading.Event().wait(0.1)
        assert len(server.requests) == sent
        assert errors.items == []
        assert statuses.items[-1].polling_stopped
        assert runtime.is_enabled("ordered", {"user": "user_1"}) is True

    def test_a_401_from_refresh_before_start_fails_readiness_and_start(
        self, server: FlagServer, make_runtime: Make, caplog: pytest.LogCaptureFixture
    ) -> None:
        server.respond(401, {"message": "Unauthorized"})
        runtime = make_runtime()
        with pytest.raises(AuthenticationError):
            runtime.refresh()
        with pytest.raises(AuthenticationError):
            runtime.wait_until_ready(timeout=1)
        with caplog.at_level(logging.WARNING, logger="workos.feature_flags.runtime"):
            runtime.start()
        assert "Not starting feature flag polling" in caplog.text
        threading.Event().wait(0.05)
        assert len(server.requests) == 1

    def test_failure_logs_carry_the_http_status_of_an_empty_body(
        self,
        server: FlagServer,
        make_runtime: Make,
        fast_polling: List[int],
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        server.respond(500, None)
        with caplog.at_level(logging.WARNING, logger="workos.feature_flags.runtime"):
            runtime = make_runtime()
            runtime.start()
            eventually(lambda: "ServerError: HTTP 500" in caplog.text)
        assert "message=" not in caplog.text

    def test_a_403_keeps_polling(
        self, server: FlagServer, make_runtime: Make, fast_polling: List[int]
    ) -> None:
        server.respond(403, {"message": "Forbidden"})
        runtime = make_runtime()
        runtime.start()
        server.wait_for_requests(3)
        assert runtime.status.polling_stopped is False

    def test_unobserved_failures_are_logged(
        self,
        server: FlagServer,
        make_runtime: Make,
        fast_polling: List[int],
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        server.respond(500, {"message": "Boom"})
        with caplog.at_level(logging.WARNING, logger="workos.feature_flags.runtime"):
            runtime = make_runtime()
            runtime.start()
            eventually(
                lambda: "keeping the last good flags and retrying" in caplog.text
            )


class TestManualRefresh:
    def test_works_without_polling(
        self, server: FlagServer, make_runtime: Make
    ) -> None:
        server.respond(200, ORDERED)
        runtime = make_runtime()
        runtime.refresh()
        assert runtime.is_ready
        assert len(server.requests) == 1

    def test_raises_without_notifying_error_listeners(
        self, server: FlagServer, make_runtime: Make
    ) -> None:
        server.respond(404, {"message": "Not Found"})
        errors = Collector()
        runtime = make_runtime(on_error=errors)
        with pytest.raises(NotFoundError):
            runtime.refresh()
        assert errors.items == []
        assert runtime.status.failed_refresh_count == 1

    def test_is_serialized_with_polling(
        self, server: FlagServer, make_runtime: Make, fast_polling: List[int]
    ) -> None:
        server.respond(200, ORDERED)
        runtime = make_runtime()
        runtime.start()
        refreshers = [threading.Thread(target=runtime.refresh) for _ in range(4)]
        for refresher in refreshers:
            refresher.start()
        for refresher in refreshers:
            refresher.join(5)
        assert server.max_in_flight == 1


class TestClose:
    def test_stops_polling_and_keeps_serving_the_last_flags(
        self, server: FlagServer, make_runtime: Make, fast_polling: List[int]
    ) -> None:
        server.respond(200, ORDERED)
        runtime = make_runtime()
        runtime.start()
        server.wait_for_requests(2)
        runtime.close()
        sent = len(server.requests)
        threading.Event().wait(0.1)

        assert len(server.requests) == sent
        assert runtime.is_closed
        assert runtime.is_enabled("ordered", {"user": "user_1"}) is True
        with pytest.raises(RuntimeError):
            runtime.start()
        with pytest.raises(RuntimeError):
            runtime.refresh()
        runtime.close()

    def test_discards_a_refresh_in_flight(
        self, server: FlagServer, make_runtime: Make
    ) -> None:
        server.enqueue(FlagServer.BLOCK)
        changes = Collector()
        runtime = make_runtime(on_change=changes)
        runtime.start()
        server.wait_for_requests(1)
        closer = threading.Thread(target=runtime.close)
        closer.start()
        eventually(lambda: runtime.is_closed)
        server.release()
        closer.join(5)

        assert not closer.is_alive()
        assert runtime.is_ready is False
        assert changes.items == []

    def test_can_be_called_from_a_listener(
        self, server: FlagServer, make_runtime: Make
    ) -> None:
        server.respond(200, ORDERED)
        closed = threading.Event()
        holder: List[FeatureFlagsRuntimeClient] = []

        def close_on_change(event: FlagsChangedEvent) -> None:
            holder[0].close()
            closed.set()

        runtime = make_runtime(on_change=close_on_change)
        holder.append(runtime)
        runtime.start()
        assert closed.wait(5)
        assert runtime.is_closed

    def test_context_manager_starts_and_closes(
        self, server: FlagServer, client: WorkOSClient
    ) -> None:
        server.respond(200, ORDERED)
        with client.create_feature_flags_runtime_client() as runtime:
            runtime.wait_until_ready(timeout=5)
        assert runtime.is_closed


class TestConcurrency:
    def test_readers_always_see_one_complete_snapshot(
        self, server: FlagServer, make_runtime: Make, fast_polling: List[int]
    ) -> None:
        # Every snapshot holds flags a and b with equal values, alternating
        # between all-true and all-false; a torn read would mix them.
        def snapshot(value: bool) -> dict:
            return payload(
                a=flag("a", default_value=value), b=flag("b", default_value=value)
            )

        server.respond(200, snapshot(True))
        runtime = make_runtime()
        runtime.refresh()
        runtime.start()
        torn: List[dict] = []
        stop = threading.Event()

        def read() -> None:
            while not stop.is_set():
                flags = runtime.get_all_flags()
                if len(set(flags.values())) != 1:
                    torn.append(flags)

        readers = [threading.Thread(target=read) for _ in range(4)]
        for reader in readers:
            reader.start()
        for index in range(20):
            server.respond(200, snapshot(index % 2 == 0))
            server.wait_for_requests(len(server.requests) + 1)
        stop.set()
        for reader in readers:
            reader.join(5)
        assert torn == []


class TestConfiguration:
    def test_rejects_a_client_without_an_api_key(self) -> None:
        public = create_public_client(client_id="client_123")
        with pytest.raises(ConfigurationError):
            FeatureFlagsRuntimeClient(public)  # type: ignore[arg-type]
        public.close()

    def test_rejects_an_unparsed_bootstrap(self, client: WorkOSClient) -> None:
        with pytest.raises(TypeError, match="from_json"):
            client.create_feature_flags_runtime_client(bootstrap=ORDERED)  # type: ignore[arg-type]

    def test_clamps_the_polling_interval(self, make_runtime: Make) -> None:
        assert make_runtime(polling_interval=1)._polling_interval == 5.0

    @pytest.mark.parametrize("value", [0, -1, float("nan"), float("inf")])
    def test_rejects_unusable_durations(
        self, client: WorkOSClient, value: float
    ) -> None:
        with pytest.raises(ValueError):
            client.create_feature_flags_runtime_client(request_timeout=value)

    def test_constructs_directly(self, server: FlagServer) -> None:
        workos = WorkOSClient(api_key=API_KEY, base_url=BASE_URL)
        runtime = FeatureFlagsRuntimeClient(workos, polling_interval=60)
        assert runtime._polling_interval == 60.0
        runtime.close()
        workos.close()
