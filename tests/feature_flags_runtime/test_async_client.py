# @oagen-ignore-file
"""AsyncFeatureFlagsRuntimeClient: polling, readiness, notifications and shutdown."""

from __future__ import annotations

import asyncio
import traceback
from typing import Any, Callable, List

import pytest

from workos import AsyncWorkOSClient
from workos._errors import AuthenticationError, NotFoundError, WorkOSTimeoutError
from workos.feature_flags.runtime import (
    AsyncFeatureFlagsRuntimeClient,
    FeatureFlagsConfiguration,
    FeatureFlagsConfigurationError,
    FlagsChangedEvent,
)

from tests.feature_flags_runtime.helpers import (
    API_KEY,
    BASE_URL,
    FlagServer,
    flag,
    payload,
    rule,
)

pytestmark = pytest.mark.asyncio

Make = Callable[..., AsyncFeatureFlagsRuntimeClient]

ORDERED = payload(
    ordered=flag(
        "ordered",
        default_value=True,
        rules=[
            rule("flag_rule_1", False, "organization", "org_1"),
            rule("flag_rule_2", True, "user", "user_1"),
        ],
    )
)
CHANGED = payload(
    ordered=flag("ordered", default_value=False),
    added=flag("added", default_value=True),
)


async def until(predicate: Callable[[], bool], timeout: float = 5.0) -> None:
    async def poll() -> None:
        while not predicate():
            await asyncio.sleep(0.002)

    await asyncio.wait_for(poll(), timeout)


async def test_polls_the_v2_endpoint_and_becomes_ready(
    server: FlagServer, make_async_runtime: Make
) -> None:
    server.respond(200, ORDERED)
    runtime = make_async_runtime(request_timeout=7)
    assert server.requests == []
    await runtime.start()
    await runtime.wait_until_ready(timeout=5)

    request = server.requests[0]
    assert request.url == f"{BASE_URL}/sdk/feature-flags?payload_version=2"
    assert request.headers["Authorization"] == f"Bearer {API_KEY}"
    assert 0 < request.timeout <= 7
    assert (
        runtime.is_enabled("ordered", {"user": "user_1", "organization": "org_1"})
        is False
    )
    assert runtime.is_enabled("ordered", {"user": "user_1"}) is True
    assert runtime.get_all_flags() == {"ordered": True}
    assert runtime.get_flag("ordered") is not None
    assert runtime.status.refresh_count == 1


async def test_bootstrap_is_ready_without_a_request(
    server: FlagServer, make_async_runtime: Make
) -> None:
    runtime = make_async_runtime(bootstrap=FeatureFlagsConfiguration.from_dict(ORDERED))
    await runtime.wait_until_ready(timeout=0)
    assert runtime.is_enabled("ordered") is True
    assert server.requests == []


async def test_wait_times_out_without_a_configuration(make_async_runtime: Make) -> None:
    with pytest.raises(TimeoutError):
        await make_async_runtime().wait_until_ready(timeout=0.01)


async def test_a_wait_timeout_names_the_last_refresh_error(
    server: FlagServer, make_async_runtime: Make
) -> None:
    server.respond(404, {"message": "Not Found"})
    runtime = make_async_runtime()
    with pytest.raises(NotFoundError):
        await runtime.refresh()
    with pytest.raises(
        TimeoutError, match="the last refresh failed: NotFoundError"
    ) as raised:
        await runtime.wait_until_ready(timeout=0.01)
    assert raised.value.__cause__ is runtime.status.last_error


async def test_each_wait_after_a_401_raises_a_fresh_error(
    server: FlagServer, make_async_runtime: Make
) -> None:
    server.respond(401, {"message": "Unauthorized"})
    runtime = make_async_runtime()
    with pytest.raises(AuthenticationError):
        await runtime.refresh()
    errors: List[BaseException] = []
    for _ in range(4):
        try:
            await runtime.wait_until_ready(timeout=1)
        except AuthenticationError as error:
            errors.append(error)
    assert len({id(error) for error in errors}) == 4
    stored = errors[0].__cause__
    assert stored is not None and all(error.__cause__ is stored for error in errors)
    depths = {len(traceback.extract_tb(error.__traceback__)) for error in errors}
    assert len(depths) == 1


async def test_awaits_coroutine_and_plain_listeners(
    server: FlagServer, make_async_runtime: Make, fast_polling: List[int]
) -> None:
    server.respond(200, ORDERED)
    seen: List[Any] = []

    async def on_change(event: FlagsChangedEvent) -> None:
        await asyncio.sleep(0)
        seen.append(("change", event.changed_flags))

    runtime = make_async_runtime(on_change=on_change)
    runtime.add_status_listener(
        lambda status: seen.append(("status", status.refresh_count))
    )
    await runtime.start()
    await until(lambda: len(seen) >= 2)
    assert seen[:2] == [("status", 1), ("change", frozenset({"ordered"}))]

    server.respond(200, CHANGED)
    await until(
        lambda: any(
            item == ("change", frozenset({"ordered", "added"})) for item in seen
        )
    )


async def test_listeners_can_await_refresh_and_events_stay_in_order(
    server: FlagServer, make_async_runtime: Make
) -> None:
    server.respond(200, ORDERED)
    log: List[str] = []
    holder: List[AsyncFeatureFlagsRuntimeClient] = []

    async def on_change(event: FlagsChangedEvent) -> None:
        label = "first-load" if event.previous is None else "refresh"
        log.append(f"start {label}")
        if event.previous is None:
            server.respond(200, CHANGED)
            await holder[0].refresh()
        log.append(f"end {label}")

    runtime = make_async_runtime(on_change=on_change)
    holder.append(runtime)
    await asyncio.wait_for(runtime.refresh(), 2)

    assert log == ["start first-load", "end first-load", "start refresh", "end refresh"]
    assert runtime.is_enabled("added") is True


@pytest.mark.parametrize(
    "status, body, error_type",
    [
        (404, {"message": "Not Found"}, NotFoundError),
        (200, {"version": 3, "flags": {}}, FeatureFlagsConfigurationError),
    ],
)
async def test_failures_keep_the_last_good_flags_and_recover(
    server: FlagServer,
    make_async_runtime: Make,
    fast_polling: List[int],
    status: int,
    body: Any,
    error_type: type,
) -> None:
    server.respond(200, ORDERED)
    errors: List[Exception] = []
    runtime = make_async_runtime(on_error=errors.append)
    await runtime.start()
    await runtime.wait_until_ready(timeout=5)
    good = runtime.configuration

    server.respond(status, body)
    await until(lambda: len(errors) >= 1)
    assert isinstance(errors[0], error_type)
    assert runtime.configuration is good

    server.respond(200, CHANGED)
    await until(lambda: runtime.is_enabled("added"))
    assert runtime.status.last_error is None


async def test_a_401_stops_polling(
    server: FlagServer, make_async_runtime: Make, fast_polling: List[int]
) -> None:
    server.respond(401, {"message": "Unauthorized"})
    runtime = make_async_runtime()
    await runtime.start()
    with pytest.raises(AuthenticationError):
        await runtime.wait_until_ready(timeout=5)
    await asyncio.sleep(0.05)
    assert len(server.requests) == 1
    assert runtime.status.polling_stopped


async def test_a_401_from_refresh_stops_polling(
    server: FlagServer, make_async_runtime: Make, fast_polling: List[int]
) -> None:
    server.respond(200, ORDERED)
    runtime = make_async_runtime()
    await runtime.start()
    await until(lambda: len(server.requests) >= 2)

    server.respond(401, {"message": "Unauthorized"})
    with pytest.raises(AuthenticationError):
        await runtime.refresh()
    assert runtime.status.polling_stopped
    await until(lambda: runtime._task is not None and runtime._task.done())
    sent = len(server.requests)
    await asyncio.sleep(0.05)
    assert len(server.requests) == sent
    assert runtime.is_enabled("ordered", {"user": "user_1"}) is True


async def test_a_429_retry_after_delays_the_next_poll(
    server: FlagServer, make_async_runtime: Make, fast_polling: List[int]
) -> None:
    server.enqueue((429, {"message": "slow down"}, {"Retry-After": "30"}))
    server.respond(200, ORDERED)
    runtime = make_async_runtime(request_timeout=1)
    await runtime.start()
    await until(lambda: len(server.requests) == 1)
    await asyncio.sleep(0.3)
    assert len(server.requests) == 1
    assert runtime.status.failed_refresh_count == 1


async def test_a_403_keeps_polling(
    server: FlagServer, make_async_runtime: Make, fast_polling: List[int]
) -> None:
    server.respond(403, {"message": "Forbidden"})
    runtime = make_async_runtime()
    await runtime.start()
    await until(lambda: len(server.requests) >= 3)
    assert runtime.status.polling_stopped is False


async def test_a_refresh_is_bounded_by_its_request_timeout(
    server: FlagServer, make_async_runtime: Make
) -> None:
    server.enqueue(FlagServer.BLOCK)
    runtime = make_async_runtime(request_timeout=0.05)
    with pytest.raises(WorkOSTimeoutError, match="request timeout"):
        await runtime.refresh()
    server.release()
    assert isinstance(runtime.status.last_error, WorkOSTimeoutError)
    assert runtime.status.failed_refresh_count == 1


async def test_manual_refreshes_are_serialized(
    server: FlagServer, make_async_runtime: Make
) -> None:
    server.respond(200, ORDERED)
    runtime = make_async_runtime()
    await asyncio.gather(*(runtime.refresh() for _ in range(5)))
    assert server.max_in_flight == 1
    assert runtime.status.refresh_count == 5


async def test_close_stops_polling_and_keeps_the_last_flags(
    server: FlagServer, make_async_runtime: Make, fast_polling: List[int]
) -> None:
    server.respond(200, ORDERED)
    runtime = make_async_runtime()
    await runtime.start()
    await until(lambda: len(server.requests) >= 2)
    await runtime.close()
    sent = len(server.requests)
    await asyncio.sleep(0.05)

    assert len(server.requests) == sent
    assert runtime.is_enabled("ordered", {"user": "user_1"}) is True
    with pytest.raises(RuntimeError):
        await runtime.start()
    with pytest.raises(RuntimeError):
        await runtime.refresh()
    await runtime.close()


async def test_close_cancels_a_refresh_in_flight(
    server: FlagServer, make_async_runtime: Make
) -> None:
    server.enqueue(FlagServer.BLOCK)
    runtime = make_async_runtime()
    await runtime.start()
    await until(lambda: len(server.requests) == 1)
    await asyncio.wait_for(runtime.close(), 1)
    server.release()
    assert runtime.is_ready is False


async def test_close_can_be_called_from_a_listener(
    server: FlagServer, make_async_runtime: Make
) -> None:
    server.respond(200, ORDERED)
    holder: List[AsyncFeatureFlagsRuntimeClient] = []
    closed = asyncio.Event()

    async def close_on_change(event: FlagsChangedEvent) -> None:
        await holder[0].close()
        closed.set()

    runtime = make_async_runtime(on_change=close_on_change)
    holder.append(runtime)
    await runtime.start()
    await asyncio.wait_for(closed.wait(), 5)
    await until(lambda: runtime._task is not None and runtime._task.done())


async def test_context_manager_starts_and_closes(
    server: FlagServer, async_client: AsyncWorkOSClient
) -> None:
    server.respond(200, ORDERED)
    async with async_client.create_feature_flags_runtime_client() as runtime:
        await runtime.wait_until_ready(timeout=5)
    assert runtime.is_closed
