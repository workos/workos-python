# @oagen-ignore-file

"""Workload identity federation: conformance cases WIF-01 to WIF-24.

Each case is one scenario function that runs twice, from the same code:
against ``WorkOSClient`` as ``test_WIF_NN_<name>`` and against
``AsyncWorkOSClient`` as ``test_WIF_NN_async_<name>``. The scenario talks to a
``Harness`` that hides whether a call is a function call or a coroutine.

Nothing here touches the network. The token endpoint and the API are mocked at
the httpx2 transport, below the client, so redirects, retries and headers are
the real ones. Time is an injected clock, and backoff is an injected sleeper.

The tests under "the real HTTP stack" are the exception. They leave the
transport in place, to see how a real failure to connect is worded, and open
loopback sockets only.
"""

from __future__ import annotations

import asyncio
import contextvars
import errno
import json
import logging
import os
import re
import socket
import subprocess
import sys
import threading
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, Union
from urllib.parse import parse_qs

import httpx2
import pytest
from cryptography.fernet import Fernet

from tests.generated_helpers import load_fixture
from workos import (
    AsyncWorkOSClient,
    AuthenticationError,
    Credentials,
    CredentialSnapshot,
    IdentityTokenProvider,
    WorkloadIdentityCredentials,
    WorkloadIdentityError,
    WorkOSClient,
    WorkOSError,
    token_env,
    token_file,
)
from workos import workload_identity
from workos._credentials import StaticKeyCredentials, apply_snapshot
from workos._errors import ConfigurationError, WorkOSTimeoutError
from workos.session import seal_data
from workos.sso.models import SSOTokenResponse
from workos.user_management.models import AuthenticateResponse

CLIENT_ID = "client_wif_test"
ENVIRONMENT_ID = "environment_wif_test"
TOKEN_URL = "https://token.test/oauth2/token"
API_URL = "https://api.test"
ELSEWHERE_URL = "https://elsewhere.test/oauth2/token"
# No mock answers this host: a request to it fails the test.
IGNORED_URL = "https://ignored.example.test/oauth2/token"

ENVIRONMENT = (
    "WORKOS_API_KEY",
    "WORKOS_CLIENT_ID",
    "WORKOS_BASE_URL",
)
OAUTH_CODES = (
    "invalid_grant",
    "invalid_target",
    "invalid_client",
    "unauthorized_client",
    "invalid_scope",
    "invalid_request",
)
EXCHANGE_ATTEMPTS = workload_identity.MAX_RETRIES + 1


# --- the mock token endpoint and API ----------------------------------------------


@dataclass
class Reply:
    """A response a mocked host gives."""

    status: int = 200
    json: Any = None
    headers: Dict[str, str] = field(default_factory=lambda: {})
    text: Optional[str] = None

    def response(self) -> httpx2.Response:
        if self.text is not None:
            return httpx2.Response(
                self.status, content=self.text.encode(), headers=self.headers
            )
        return httpx2.Response(self.status, json=self.json, headers=self.headers)


@dataclass
class HeldReply(Reply):
    """A response that is not sent until ``release`` is set."""

    release: threading.Event = field(default_factory=threading.Event)

    def response(self) -> httpx2.Response:
        assert self.release.wait(10), "a held reply was never released"
        return super().response()


def oauth_error(code: str, description: str = "the server said no") -> Reply:
    return Reply(400, {"error": code, "error_description": description})


def unauthorized() -> Reply:
    return Reply(401, {"message": "Unauthorized"})


@dataclass
class Recorded:
    """A request a mocked host received."""

    method: str
    url: str
    headers: Dict[str, str]
    content: bytes
    timeout: Optional[float] = None

    @property
    def form(self) -> Dict[str, str]:
        fields = parse_qs(self.content.decode(), keep_blank_values=True)
        return {name: values[0] for name, values in fields.items()}

    @property
    def bearer(self) -> Optional[str]:
        value = self.headers.get("authorization")
        if value is not None and value.startswith("Bearer "):
            return value[len("Bearer ") :]
        return value


class Endpoint:
    """One mocked host: replays scripted replies, then its default one."""

    def __init__(self) -> None:
        self.requests: List[Recorded] = []
        self.script: List[Union[Reply, Exception]] = []
        self.entered = threading.Event()
        self._gate: Optional[threading.Event] = None
        self._lock = threading.Lock()

    @property
    def count(self) -> int:
        """Requests this host received. A scripted connection failure is not one."""
        return len(self.requests)

    def bearers(self) -> List[Optional[str]]:
        return [request.bearer for request in self.requests]

    def hold(self) -> None:
        """Keep every response back until ``release()``."""
        self._gate = threading.Event()

    def release(self) -> None:
        if self._gate is not None:
            self._gate.set()

    def held(self) -> bool:
        gate = self._gate
        return gate is not None and not gate.is_set()

    def default(self) -> Reply:
        return Reply(200, {"ok": True})

    def take(self, request: httpx2.Request) -> Union[Reply, Exception]:
        with self._lock:
            item = self.script.pop(0) if self.script else self.default()
            if not isinstance(item, Exception):
                self.requests.append(
                    Recorded(
                        method=request.method,
                        url=str(request.url),
                        headers={k.lower(): v for k, v in request.headers.items()},
                        content=request.content,
                        timeout=request.extensions.get("timeout", {}).get("read"),
                    )
                )
        self.entered.set()
        return item


class TokenEndpoint(Endpoint):
    """The token endpoint: by default, one new access token per exchange."""

    def __init__(self) -> None:
        super().__init__()
        self.expires_in: Any = 300
        self.access_token: Optional[str] = None
        self.issued = 0

    def default(self) -> Reply:
        self.issued += 1
        body: Dict[str, Any] = {
            "access_token": self.access_token or f"access-{self.issued}",
            "token_type": "Bearer",
        }
        if self.expires_in is not None:
            body["expires_in"] = self.expires_in
        return Reply(200, body)

    def forms(self) -> List[Dict[str, str]]:
        return [request.form for request in self.requests]


class Network:
    """Routes every httpx2 request, sync or async, to a mocked host."""

    def __init__(self) -> None:
        self.token = TokenEndpoint()
        self.api = Endpoint()
        self.elsewhere = Endpoint()
        self.unexpected: List[str] = []
        self._hosts = {
            "token.test": self.token,
            "api.test": self.api,
            "elsewhere.test": self.elsewhere,
        }

    def _endpoint(self, request: httpx2.Request) -> Endpoint:
        endpoint = self._hosts.get(request.url.host)
        if endpoint is None:
            self.unexpected.append(str(request.url))
            raise httpx2.ConnectError("no mock for this host")
        return endpoint

    def handle(self, request: httpx2.Request) -> httpx2.Response:
        request.read()
        endpoint = self._endpoint(request)
        item = endpoint.take(request)
        deadline = time.monotonic() + 10
        while endpoint.held():
            assert time.monotonic() < deadline, "a held response was never released"
            time.sleep(0.001)
        if isinstance(item, Exception):
            raise item
        return item.response()

    async def handle_async(self, request: httpx2.Request) -> httpx2.Response:
        await request.aread()
        endpoint = self._endpoint(request)
        item = endpoint.take(request)
        deadline = time.monotonic() + 10
        while endpoint.held():
            assert time.monotonic() < deadline, "a held response was never released"
            await asyncio.sleep(0.001)
        if isinstance(item, Exception):
            raise item
        return item.response()


@pytest.fixture
def network(monkeypatch: pytest.MonkeyPatch) -> Iterator[Network]:
    net = Network()
    for name in ENVIRONMENT:
        monkeypatch.delenv(name, raising=False)

    def _sync(
        _transport: httpx2.HTTPTransport, request: httpx2.Request
    ) -> httpx2.Response:
        return net.handle(request)

    async def _async(
        _transport: httpx2.AsyncHTTPTransport, request: httpx2.Request
    ) -> httpx2.Response:
        return await net.handle_async(request)

    monkeypatch.setattr(httpx2.HTTPTransport, "handle_request", _sync)
    monkeypatch.setattr(httpx2.AsyncHTTPTransport, "handle_async_request", _async)
    yield net
    for endpoint in (net.token, net.api, net.elsewhere):
        endpoint.release()
    assert net.unexpected == [], f"requests to unmocked hosts: {net.unexpected}"


# --- providers, clock --------------------------------------------------------------


class Provider:
    """An identity token provider that counts its calls.

    Returns its values in order and then repeats the last one. A value that is
    an exception is raised instead.
    """

    def __init__(self, *values: Union[str, Exception]) -> None:
        self._values: List[Union[str, Exception]] = list(values) or ["assertion-1"]
        self._lock = threading.Lock()
        self.calls = 0
        self.threads: List[int] = []

    def __call__(self) -> str:
        with self._lock:
            value = self._values[min(self.calls, len(self._values) - 1)]
            self.calls += 1
            self.threads.append(threading.get_ident())
        if isinstance(value, Exception):
            raise value
        return value


class Clock:
    def __init__(self) -> None:
        self.time = 0.0

    def now(self) -> float:
        return self.time


class Counter:
    def __init__(self) -> None:
        self.value = 0
        self._lock = threading.Lock()

    def increment(self) -> None:
        with self._lock:
            self.value += 1


# --- the harness: one scenario, both clients ----------------------------------------

Operation = Callable[[], Any]


class Harness:
    """What a scenario needs, for ``WorkOSClient``. ``AsyncHarness`` overrides the rest."""

    gave_up_error: type = WorkOSTimeoutError

    def __init__(
        self,
        network: Network,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        self.network = network
        self.token = network.token
        self.api = network.api
        self.monkeypatch = monkeypatch
        self.tmp_path = tmp_path
        self.caplog = caplog
        self.clock = Clock()
        self.sleeps: List[float] = []
        self._clients: List[Any] = []

    # credentials

    def instrument(
        self, credentials: WorkloadIdentityCredentials
    ) -> WorkloadIdentityCredentials:
        """Give the credentials the fake clock and a sleeper that only records."""
        credentials._clock = self.clock.now
        credentials._sleep = self.sleeps.append
        return credentials

    def credentials(
        self, provider: Optional[IdentityTokenProvider] = None, **settings: Any
    ) -> WorkloadIdentityCredentials:
        settings.setdefault("client_id", CLIENT_ID)
        settings.setdefault("token_url", TOKEN_URL)
        settings.setdefault("environment_id", ENVIRONMENT_ID)
        return self.bare_credentials(provider or Provider(), **settings)

    def bare_credentials(
        self, provider: IdentityTokenProvider, **settings: Any
    ) -> WorkloadIdentityCredentials:
        return self.instrument(
            WorkloadIdentityCredentials(identity_token_provider=provider, **settings)
        )

    def watch_joins(self, credentials: WorkloadIdentityCredentials) -> Counter:
        """Count the callers that joined (or started) a shared exchange."""
        joins = Counter()
        original = credentials._join_or_start

        def joined(loop: Optional[asyncio.AbstractEventLoop]) -> Any:
            exchange = original(loop)
            joins.increment()
            return exchange

        setattr(credentials, "_join_or_start", joined)
        return joins

    # clients

    def new_client(self, **kwargs: Any) -> Any:
        return WorkOSClient(**kwargs)

    def client(self, credentials: Optional[Credentials] = None, **kwargs: Any) -> Any:
        kwargs.setdefault("base_url", API_URL)
        if credentials is not None:
            kwargs["credentials"] = credentials
        client = self.new_client(**kwargs)
        self._clients.append(client)
        return client

    # operations: built once, run by whichever client this harness drives

    def op_request(
        self,
        client: Any,
        method: str = "GET",
        path: Any = ("organizations",),
        **kwargs: Any,
    ) -> Operation:
        return lambda: client.request(method, path, **kwargs)

    def op_resolve(
        self, credentials: Credentials, timeout: Optional[float] = None
    ) -> Operation:
        return lambda: credentials.resolve(timeout=timeout)

    def run(self, operation: Operation) -> Any:
        return operation()

    def start(self, operation: Operation) -> Any:
        """Start an operation without waiting for it. See ``outcome``."""
        caller = _ThreadCaller(operation)
        caller.thread.start()
        return caller

    def outcome(self, caller: Any) -> Any:
        """The started operation's result, or the exception it raised."""
        caller.thread.join(10)
        assert not caller.thread.is_alive(), "a caller never finished"
        return caller.outcome

    def wait_until(self, condition: Callable[[], bool]) -> None:
        deadline = time.monotonic() + 10
        while not condition():
            assert time.monotonic() < deadline, "timed out waiting for a condition"
            time.sleep(0.001)

    def start_impatient(self, client: Any) -> Any:
        """Start a request whose caller will give up while the exchange is held.

        A synchronous caller gives up through its request timeout.
        """
        return self.start(self.op_request(client, request_options={"timeout": 0.25}))

    def give_up(self, caller: Any) -> Any:
        return self.outcome(caller)

    # conveniences

    def get(self, client: Any, **kwargs: Any) -> Any:
        return self.run(self.op_request(client, **kwargs))

    def resolve(
        self, credentials: Credentials, timeout: Optional[float] = None
    ) -> CredentialSnapshot:
        return self.run(self.op_resolve(credentials, timeout))

    def failure(self, operation: Operation) -> BaseException:
        """Run an operation that must fail, and return what it raised."""
        with pytest.raises(Exception) as caught:
            self.run(operation)
        return caught.value

    def close(self) -> None:
        for client in self._clients:
            client.close()


class _ThreadCaller:
    def __init__(self, operation: Operation) -> None:
        self.outcome: Any = None
        self._operation = operation
        self.thread = threading.Thread(target=self._work, daemon=True)

    def _work(self) -> None:
        try:
            self.outcome = self._operation()
        except BaseException as error:
            self.outcome = error


class AsyncHarness(Harness):
    """The same scenarios against ``AsyncWorkOSClient``, on a loop the harness owns."""

    gave_up_error = asyncio.CancelledError

    def __init__(self, *args: Any) -> None:
        super().__init__(*args)
        self.loop = asyncio.new_event_loop()

    def new_client(self, **kwargs: Any) -> Any:
        return AsyncWorkOSClient(**kwargs)

    def op_resolve(
        self, credentials: Credentials, timeout: Optional[float] = None
    ) -> Operation:
        return lambda: credentials.aresolve(timeout=timeout)

    def run(self, operation: Operation) -> Any:
        return self.loop.run_until_complete(operation())

    def start(self, operation: Operation) -> Any:
        return self.loop.create_task(operation())

    def outcome(self, caller: Any) -> Any:
        async def settle() -> Any:
            return (await asyncio.gather(caller, return_exceptions=True))[0]

        return self.loop.run_until_complete(asyncio.wait_for(settle(), 10))

    def wait_until(self, condition: Callable[[], bool]) -> None:
        async def poll() -> None:
            while not condition():
                await asyncio.sleep(0.001)

        self.loop.run_until_complete(asyncio.wait_for(poll(), 10))

    def start_impatient(self, client: Any) -> Any:
        """An asynchronous caller gives up by having its task canceled."""
        return self.start(self.op_request(client))

    def give_up(self, caller: Any) -> Any:
        caller.cancel()
        return self.outcome(caller)

    def close(self) -> None:
        async def shut_down() -> None:
            for client in self._clients:
                await client.close()
            pending = [
                task
                for task in asyncio.all_tasks()
                if task is not asyncio.current_task()
            ]
            for task in pending:
                task.cancel()
            await asyncio.gather(*pending, return_exceptions=True)

        try:
            self.loop.run_until_complete(shut_down())
            self.loop.run_until_complete(self.loop.shutdown_default_executor())
        finally:
            self.loop.close()


@pytest.fixture
def sync_harness(
    network: Network,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> Iterator[Harness]:
    harness = Harness(network, monkeypatch, tmp_path, caplog)
    yield harness
    harness.close()


@pytest.fixture
def async_harness(
    network: Network,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> Iterator[Harness]:
    harness = AsyncHarness(network, monkeypatch, tmp_path, caplog)
    yield harness
    harness.close()


_CASE_NAME = re.compile(r"^(WIF_\d+)_(.+)$")


def scenario(function: Callable[[Harness], None]) -> Callable[[Harness], None]:
    """Register a scenario as two tests, one per client.

    ``WIF_01_foo`` becomes ``test_WIF_01_foo`` and ``test_WIF_01_async_foo``, so
    the case ID is in both names. A scenario with no case ID becomes
    ``test_foo`` and ``test_async_foo``.
    """
    case = _CASE_NAME.match(function.__name__)
    if case is not None:
        sync_name = f"test_{case.group(1)}_{case.group(2)}"
        async_name = f"test_{case.group(1)}_async_{case.group(2)}"
    else:
        sync_name = f"test_{function.__name__}"
        async_name = f"test_async_{function.__name__}"

    def run_sync(sync_harness: Harness) -> None:
        function(sync_harness)

    def run_async(async_harness: Harness) -> None:
        function(async_harness)

    for name, test in ((sync_name, run_sync), (async_name, run_async)):
        test.__name__ = test.__qualname__ = name
        test.__doc__ = function.__doc__
        assert name not in function.__globals__, f"duplicate test name: {name}"
        function.__globals__[name] = test
    return function


def secrets_in(error: BaseException, *secrets: str) -> List[str]:
    """Every place a secret shows up in an error, its causes, or their tracebacks."""
    found: List[str] = []
    seen: List[BaseException] = []
    current: Optional[BaseException] = error
    while current is not None and current not in seen:
        seen.append(current)
        rendered = {
            "str": str(current),
            "repr": repr(current),
            "message": str(getattr(current, "message", "")),
            "traceback": "".join(
                traceback.format_exception(
                    type(current), current, current.__traceback__
                )
            ),
        }
        for where, text in rendered.items():
            found.extend(
                f"{type(current).__name__}.{where}: {secret}"
                for secret in secrets
                if secret in text
            )
        current = current.__cause__ or current.__context__
    return found


def locals_showing(error: BaseException, *secrets: str) -> List[str]:
    """Every local variable, in the frames of an error's tracebacks, that shows a secret.

    This is what a tool that records the local variables of a traceback sees,
    such as an error reporter.
    """
    found: List[str] = []
    seen: List[BaseException] = []
    current: Optional[BaseException] = error
    while current is not None and current not in seen:
        seen.append(current)
        frames = [frame for frame, _ in traceback.walk_tb(current.__traceback__)]
        found.extend(
            f"{type(current).__name__} {frame.f_code.co_name}() {name}: {secret}"
            for frame in frames
            for name, value in frame.f_locals.items()
            for secret in secrets
            if secret in repr(value)
        )
        current = current.__cause__ or current.__context__
    return found


def unreachable(reason: str, host: str = "token.test") -> str:
    """The whole description of a token request that got no HTTP response."""
    return f"The request to the token endpoint at {host} failed: {reason}."


# --- conformance cases ---------------------------------------------------------------


@scenario
def WIF_01_first_request_triggers_one_exchange_post(h: Harness) -> None:
    provider = Provider("assertion-1")
    h.get(h.client(h.credentials(provider)))

    assert h.token.count == 1
    post = h.token.requests[0]
    assert post.method == "POST"
    assert post.url == TOKEN_URL
    assert post.headers["content-type"] == "application/x-www-form-urlencoded"
    assert post.headers["accept"] == "application/json"
    assert "authorization" not in post.headers
    assert post.form == {
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": "assertion-1",
        "client_id": "client_wif_test",
        "resource": "https://api.workos.com",
    }
    assert "scope" not in post.form
    assert "client_secret" not in post.form

    # Again on a new instance, with a scope.
    h.get(h.client(h.credentials(Provider("assertion-1"), scope="orgs:write")))

    assert h.token.count == 2
    scoped = h.token.requests[1]
    assert scoped.form["scope"] == "orgs:write"
    assert "client_secret" not in scoped.form
    assert "authorization" not in scoped.headers


@scenario
def WIF_02_api_request_carries_the_access_token_and_environment_header(
    h: Harness,
) -> None:
    # (a) With an environment ID set, the header names it.
    # No API key and no client ID: the credentials alone are enough to build a client.
    h.get(h.client(h.credentials()))

    assert h.api.count == 1
    request = h.api.requests[0]
    assert request.headers["authorization"] == "Bearer access-1"
    assert request.headers["x-url-environment-id"] == "environment_wif_test"


@scenario
def WIF_02_no_environment_id_sends_no_environment_header(h: Harness) -> None:
    # (b) No environment ID in code: the credentials are still built, and the
    # header is left off. The variable is set to show that the SDK does not
    # read it.
    h.monkeypatch.setenv("WORKOS_ENVIRONMENT_ID", "environment_env")
    credentials = h.bare_credentials(
        Provider(), client_id=CLIENT_ID, token_url=TOKEN_URL
    )
    assert credentials.environment_id is None

    h.get(h.client(credentials))

    assert h.api.count == 1
    request = h.api.requests[0]
    assert request.headers["authorization"] == "Bearer access-1"
    assert "x-url-environment-id" not in request.headers


@scenario
def WIF_03_second_request_reuses_the_cached_token(h: Harness) -> None:
    client = h.client(h.credentials())

    h.get(client)
    h.get(client)

    assert h.token.count == 1
    assert h.api.bearers() == ["access-1", "access-1"]


@scenario
def WIF_04_token_is_refreshed_when_less_than_60_seconds_remain(h: Harness) -> None:
    h.token.expires_in = 300
    client = h.client(h.credentials())

    h.get(client)
    h.clock.time = 239
    h.get(client)
    assert h.token.count == 1

    h.clock.time = 241
    h.get(client)
    assert h.token.count == 2
    assert h.api.bearers() == ["access-1", "access-1", "access-2"]


@scenario
def WIF_05_refresh_threshold_is_20_percent_of_a_short_lifetime(h: Harness) -> None:
    h.token.expires_in = 100
    client = h.client(h.credentials())

    h.get(client)
    h.clock.time = 79
    h.get(client)
    assert h.token.count == 1

    h.clock.time = 81
    h.get(client)
    assert h.token.count == 2


@scenario
def WIF_06_missing_expires_in_is_treated_as_300_seconds(h: Harness) -> None:
    h.token.expires_in = None
    client = h.client(h.credentials())

    h.get(client)
    h.clock.time = 239
    h.get(client)
    assert h.token.count == 1

    h.clock.time = 241
    h.get(client)
    assert h.token.count == 2


@scenario
def WIF_07_two_instances_never_share_a_cached_token(h: Harness) -> None:
    first = h.client(h.credentials())
    second = h.client(h.credentials())

    h.get(first)
    h.get(second)

    assert h.token.count == 2
    assert h.api.bearers() == ["access-1", "access-2"]


@scenario
def WIF_08_concurrent_first_requests_produce_exactly_one_exchange(h: Harness) -> None:
    provider = Provider()
    credentials = h.credentials(provider)
    joins = h.watch_joins(credentials)
    client = h.client(credentials)
    h.token.hold()

    callers = [h.start(h.op_request(client)) for _ in range(20)]
    # The token endpoint answers only once all 20 callers wait on the exchange.
    h.wait_until(lambda: joins.value == 20 and h.token.entered.is_set())
    h.token.release()
    outcomes = [h.outcome(caller) for caller in callers]

    assert [o for o in outcomes if isinstance(o, BaseException)] == []
    assert h.token.count == 1
    assert provider.calls == 1
    assert h.api.bearers() == ["access-1"] * 20


@scenario
def WIF_09_a_401_invalidates_the_token_exchanges_again_and_retries_once(
    h: Harness,
) -> None:
    client = h.client(h.credentials())
    h.api.script.append(unauthorized())

    assert h.get(client) == {"ok": True}

    assert h.token.count == 2
    assert h.api.bearers() == ["access-1", "access-2"]


@scenario
def WIF_10_a_second_401_after_recovery_is_returned_to_the_caller(h: Harness) -> None:
    client = h.client(h.credentials())
    h.api.script.extend(unauthorized() for _ in range(10))

    error = h.failure(h.op_request(client))

    assert isinstance(error, AuthenticationError)
    assert h.token.count == 2
    assert h.api.count == 2
    assert h.api.bearers() == ["access-1", "access-2"]


@scenario
def WIF_11_a_late_401_for_an_old_generation_keeps_the_newer_token(h: Harness) -> None:
    credentials = h.credentials()
    client = h.client(credentials)

    first = h.resolve(credentials)
    assert first.headers["Authorization"] == "Bearer access-1"
    credentials.invalidate(first.generation)
    second = h.resolve(credentials)
    assert second.headers["Authorization"] == "Bearer access-2"
    assert second.generation > first.generation

    # A 401 for the first token arrives late.
    credentials.invalidate(first.generation)
    h.get(client)

    assert h.resolve(credentials).generation == second.generation
    assert h.token.count == 2
    assert h.api.bearers() == ["access-2"]


@scenario
def WIF_12_transport_retries_do_not_reset_the_401_recovery_allowance(
    h: Harness,
) -> None:
    client = h.client(h.credentials())
    h.api.script.extend(
        [
            unauthorized(),
            Reply(503, {"message": "Unavailable"}, {"Retry-After": "0"}),
            unauthorized(),
            Reply(200, {"ok": True}),
        ]
    )

    error = h.failure(h.op_request(client))

    assert isinstance(error, AuthenticationError)
    assert h.token.count == 2
    # Exactly three attempts: the 200 that would have come fourth is never asked for.
    assert h.api.count == 3
    assert len(h.api.script) == 1


@scenario
def WIF_13_the_401_retry_sends_the_same_body_and_idempotency_key(h: Harness) -> None:
    client = h.client(h.credentials())
    h.api.script.append(unauthorized())

    h.run(h.op_request(client, method="POST", body={"name": "Acme", "n": 1}))

    assert h.api.count == 2
    first, second = h.api.requests
    assert json.loads(first.content) == {"name": "Acme", "n": 1}
    assert first.content == second.content
    assert first.headers["idempotency-key"]
    assert first.headers["idempotency-key"] == second.headers["idempotency-key"]
    assert [first.bearer, second.bearer] == ["access-1", "access-2"]


@scenario
def WIF_14_exchange_is_retried_on_503_and_429_honoring_retry_after(
    h: Harness,
) -> None:
    provider = Provider()
    h.token.script.extend(
        [
            Reply(503, {"message": "Unavailable"}),
            Reply(429, {"message": "Slow down"}, {"Retry-After": "0"}),
        ]
    )

    h.get(h.client(h.credentials(provider)))

    assert h.token.count == 3
    assert provider.calls == 3
    assert h.api.bearers() == ["access-1"]
    # The 429's Retry-After: 0 is what the second backoff waited.
    assert h.sleeps[1] == 0


@scenario
def WIF_14_exchange_is_retried_on_a_connection_failure(h: Harness) -> None:
    provider = Provider()
    h.token.script.append(httpx2.ConnectError("connection refused"))

    h.get(h.client(h.credentials(provider)))

    assert provider.calls == 2
    assert h.token.count == 1
    assert h.api.bearers() == ["access-1"]


@scenario
def WIF_14_exchange_is_retried_on_a_timeout(h: Harness) -> None:
    provider = Provider()
    h.token.script.append(httpx2.ReadTimeout("the token endpoint did not answer"))

    h.get(h.client(h.credentials(provider)))

    assert provider.calls == 2
    assert h.api.bearers() == ["access-1"]
    # An attempt gets a share of the 30-second deadline, not all of it, so
    # that a timeout leaves time to try again.
    retry = h.token.requests[0]
    assert retry.timeout is not None
    assert 0 < retry.timeout <= workload_identity.EXCHANGE_DEADLINE_SECONDS / 3


@scenario
def WIF_14_provider_is_invoked_again_after_it_raises(h: Harness) -> None:
    provider = Provider(
        RuntimeError("the metadata server is warming up"), "assertion-2"
    )

    h.get(h.client(h.credentials(provider)))

    assert provider.calls == 2
    assert h.token.count == 1
    assert h.token.forms()[0]["assertion"] == "assertion-2"
    assert h.api.bearers() == ["access-1"]


@scenario
def WIF_14_retry_after_is_what_the_sleeper_is_asked_to_wait(h: Harness) -> None:
    h.token.script.append(Reply(429, {"message": "Slow down"}, {"Retry-After": "1"}))

    h.get(h.client(h.credentials()))

    assert h.token.count == 2
    assert len(h.sleeps) == 1
    assert h.sleeps[0] >= 1


@scenario
def WIF_15_an_oauth_error_is_not_retried_and_carries_its_code(h: Harness) -> None:
    for code in OAUTH_CODES:
        before = h.token.count
        provider = Provider()
        h.token.script.append(oauth_error(code, f"{code} from the server"))

        error = h.failure(h.op_request(h.client(h.credentials(provider))))

        assert isinstance(error, WorkloadIdentityError), code
        assert isinstance(error, WorkOSError)
        assert error.code == code
        assert error.description == f"{code} from the server"
        assert error.hint
        assert str(error) == f"{code}: {error.hint} {code} from the server"
        assert h.token.count - before == 1
        assert provider.calls == 1
    assert h.api.count == 0
    assert h.sleeps == []


@scenario
def WIF_16_after_a_failed_exchange_the_next_request_exchanges_afresh(
    h: Harness,
) -> None:
    client = h.client(h.credentials())
    h.token.script.append(oauth_error("invalid_grant"))

    error = h.failure(h.op_request(client))
    assert isinstance(error, WorkloadIdentityError)

    h.get(client)

    assert h.token.count == 2
    assert h.api.bearers() == ["access-1"]


@scenario
def WIF_17_tokens_never_appear_in_errors_or_logs(h: Harness) -> None:
    assertion = "SECRET-ASSERTION-VALUE"
    access_token = "SECRET-ACCESS-VALUE"
    h.caplog.set_level(logging.DEBUG)
    h.token.access_token = access_token
    errors: List[BaseException] = []

    def fail_with(provider: IdentityTokenProvider) -> None:
        client = h.client(h.credentials(provider))
        errors.append(h.failure(h.op_request(client)))

    # An invalid_grant exchange.
    h.token.script.append(oauth_error("invalid_grant"))
    fail_with(Provider(assertion))
    # A 500 from the token endpoint until the retries run out.
    h.token.script.extend(
        Reply(500, {"message": "boom"}) for _ in range(EXCHANGE_ATTEMPTS)
    )
    fail_with(Provider(assertion))
    # A provider that raises.
    fail_with(Provider(RuntimeError("the provider broke")))
    # A second 401 from the API, after the access token was issued and sent.
    h.api.script.extend(unauthorized() for _ in range(2))
    fail_with(Provider(assertion))
    # An OAuth error in which the token endpoint repeats the assertion.
    repeated = {
        "error": "invalid_grant",
        "error_description": f"JWT {assertion} failed validation",
    }
    h.token.script.append(Reply(400, repeated))
    fail_with(Provider(assertion))
    # The same body on a 503, until the retries run out.
    h.token.script.extend(Reply(503, repeated) for _ in range(EXCHANGE_ATTEMPTS))
    fail_with(Provider(assertion))

    assert [type(error).__name__ for error in errors] == [
        "WorkloadIdentityError",
        "WorkloadIdentityError",
        "WorkloadIdentityError",
        "AuthenticationError",
        "WorkloadIdentityError",
        "WorkloadIdentityError",
    ]
    assert h.api.bearers() == [access_token, access_token]
    for error in errors[4:]:
        assert isinstance(error, WorkloadIdentityError)
        assert error.code == "invalid_grant"
        assert error.description == "JWT [redacted] failed validation"
    for error in errors:
        assert secrets_in(error, assertion, access_token) == []
        # Nor in a local variable of any frame the error's traceback holds.
        assert locals_showing(error, assertion, access_token) == []
    for record in h.caplog.records:
        logged = f"{record.getMessage()} {record.__dict__!r}"
        assert assertion not in logged
        assert access_token not in logged
    assert assertion not in h.caplog.text
    assert access_token not in h.caplog.text


@scenario
def WIF_18_the_exchange_does_not_follow_redirects(h: Harness) -> None:
    h.token.script.append(Reply(307, None, {"Location": ELSEWHERE_URL}))

    error = h.failure(h.op_request(h.client(h.credentials())))

    assert isinstance(error, WorkloadIdentityError)
    assert error.code == "exchange_failed"
    assert h.network.elsewhere.count == 0
    assert h.token.count == 1
    assert h.api.count == 0


@scenario
def WIF_19_api_key_together_with_credentials_is_a_configuration_error(
    h: Harness,
) -> None:
    credentials = h.credentials()

    with pytest.raises(ValueError, match="api_key or credentials, not both"):
        h.client(credentials, api_key="sk_test_explicit")

    assert h.token.count == 0
    assert h.api.count == 0


@scenario
def WIF_20_explicit_credentials_win_over_the_environment_api_key(h: Harness) -> None:
    h.monkeypatch.setenv("WORKOS_API_KEY", "sk_test_env")

    # (a) Valid credentials are used; the environment key is ignored.
    client = h.client(h.credentials())
    h.get(client)
    assert h.api.bearers() == ["access-1"]
    assert client._api_key is None

    # (b) Credentials with no token URL cannot be built.
    with pytest.raises(WorkloadIdentityError) as missing:
        h.bare_credentials(
            Provider(), client_id=CLIENT_ID, environment_id=ENVIRONMENT_ID
        )
    assert missing.value.code == "invalid_configuration"
    assert missing.value.description == "token_url is required"

    # (c) A failing exchange is an error, never a fall back to the key.
    h.token.script.append(oauth_error("invalid_client"))
    error = h.failure(h.op_request(h.client(h.credentials())))
    assert isinstance(error, WorkloadIdentityError)
    assert error.code == "invalid_client"

    sent = [*h.api.requests, *h.token.requests]
    assert all("sk_test_env" not in str(request.headers) for request in sent)
    assert all(b"sk_test_env" not in request.content for request in sent)
    assert h.api.count == 1


@scenario
def WIF_21_token_file_is_read_again_on_every_exchange(h: Harness) -> None:
    path = h.tmp_path / "identity-token"
    path.write_text("assertion-1\n")
    client = h.client(h.credentials(token_file(path)))

    h.get(client)
    path.write_text("  assertion-2\n\n")
    h.clock.time = 241
    h.get(client)

    assert [form["assertion"] for form in h.token.forms()] == [
        "assertion-1",
        "assertion-2",
    ]


@scenario
def WIF_22_env_and_callback_providers_and_environment_defaults(h: Harness) -> None:
    # (a) token_env reads the variable.
    h.monkeypatch.setenv("MY_JWT", "assertion-env")
    h.get(h.client(h.credentials(token_env("MY_JWT"))))
    assert h.token.forms()[-1]["assertion"] == "assertion-env"

    # (b) A callback is any callable; no wrapper is needed.
    h.get(h.client(h.credentials(lambda: "assertion-cb")))
    assert h.token.forms()[-1]["assertion"] == "assertion-cb"

    # (c) Only client_id defaults from the environment. The token URL and
    # scope variables are set to show that the SDK does not read them.
    h.monkeypatch.setenv("WORKOS_CLIENT_ID", "client_env")
    h.monkeypatch.setenv("WORKOS_WIF_TOKEN_URL", IGNORED_URL)
    h.monkeypatch.setenv("WORKOS_WIF_SCOPE", "scope_env")
    before = h.token.count
    h.get(h.client(h.bare_credentials(Provider(), token_url=TOKEN_URL)))
    assert h.token.count == before + 1
    assert h.token.requests[-1].url == TOKEN_URL
    assert h.token.forms()[-1]["client_id"] == "client_env"
    assert "scope" not in h.token.forms()[-1]

    # (d) An explicit client_id wins over the environment.
    h.get(
        h.client(
            h.bare_credentials(
                Provider(), client_id="client_explicit", token_url=TOKEN_URL
            )
        )
    )
    assert h.token.forms()[-1]["client_id"] == "client_explicit"

    # (e) With no token URL in code, the credentials cannot be built.
    with pytest.raises(WorkloadIdentityError) as missing:
        h.bare_credentials(Provider())
    assert missing.value.code == "invalid_configuration"
    assert missing.value.description == "token_url is required"
    assert h.token.count == before + 2


@scenario
def WIF_23_canceling_one_waiter_does_not_cancel_the_shared_exchange(
    h: Harness,
) -> None:
    provider = Provider()
    credentials = h.credentials(provider)
    joins = h.watch_joins(credentials)
    client = h.client(credentials)
    h.token.hold()

    caller_a = h.start_impatient(client)
    caller_b = h.start(h.op_request(client))
    h.wait_until(lambda: joins.value == 2 and h.token.entered.is_set())

    # A gives up while the token endpoint still holds its response.
    gave_up = h.give_up(caller_a)
    assert isinstance(gave_up, h.gave_up_error)
    assert h.token.held()

    h.token.release()
    assert h.outcome(caller_b) == {"ok": True}
    assert h.token.count == 1
    assert provider.calls == 1
    assert h.api.bearers() == ["access-1"]


@scenario
def WIF_24_static_api_key_clients_are_unchanged(h: Harness) -> None:
    client = h.client(api_key="sk_test_static")

    h.get(client)
    request = h.api.requests[0]
    assert request.headers["authorization"] == "Bearer sk_test_static"
    assert "x-url-environment-id" not in request.headers

    h.api.script.extend([unauthorized(), Reply(200, {"ok": True})])
    error = h.failure(h.op_request(client))

    assert isinstance(error, AuthenticationError)
    # One attempt for the 401: the 200 scripted after it is never asked for.
    assert h.api.count == 2
    assert len(h.api.script) == 1
    assert h.token.count == 0


# --- beyond the numbered cases --------------------------------------------------------


@scenario
def invalid_token_responses_are_terminal(h: Harness) -> None:
    replies = [
        (Reply(200, text="<html>not json</html>"), "invalid_response"),
        (Reply(200, ["access-1"]), "invalid_response"),
        (Reply(200, {"token_type": "Bearer"}), "invalid_response"),
        (Reply(200, {"access_token": ""}), "invalid_response"),
        (Reply(200, {"access_token": 7}), "invalid_response"),
        (Reply(404, text="not found"), "invalid_response"),
        (Reply(403, {"error": "access_denied"}), "access_denied"),
        (Reply(302, {"error": "temporarily_unavailable"}), "temporarily_unavailable"),
    ]
    for reply, code in replies:
        before = h.token.count
        h.token.script.append(reply)

        error = h.failure(h.op_request(h.client(h.credentials())))

        assert isinstance(error, WorkloadIdentityError)
        assert error.code == code
        assert error.hint
        assert h.token.count - before == 1
    assert h.sleeps == []
    assert h.api.count == 0


@scenario
def exhausted_exchange_retries_report_the_last_failure(h: Harness) -> None:
    # A 5xx is retried even when its body carries an OAuth error, and that code
    # is reported once the retries run out.
    h.token.script.extend(
        Reply(503, {"error": "temporarily_unavailable", "error_description": "busy"})
        for _ in range(EXCHANGE_ATTEMPTS)
    )
    error = h.failure(h.op_request(h.client(h.credentials())))
    assert isinstance(error, WorkloadIdentityError)
    assert (error.code, error.description) == ("temporarily_unavailable", "busy")
    assert h.token.count == EXCHANGE_ATTEMPTS
    assert len(h.sleeps) == EXCHANGE_ATTEMPTS - 1

    # Any 5xx counts, not only the statuses the API retry loop lists.
    h.token.script.extend(Reply(501, text="nope") for _ in range(EXCHANGE_ATTEMPTS))
    error = h.failure(h.op_request(h.client(h.credentials())))
    assert isinstance(error, WorkloadIdentityError)
    assert error.code == "exchange_failed"
    assert h.token.count == 2 * EXCHANGE_ATTEMPTS

    # Connection failures.
    h.token.script.extend(
        httpx2.ConnectError("connection refused") for _ in range(EXCHANGE_ATTEMPTS)
    )
    error = h.failure(h.op_request(h.client(h.credentials())))
    assert isinstance(error, WorkloadIdentityError)
    assert error.code == "exchange_failed"

    # A provider that always raises: its error is the cause, and its message is kept.
    broken = Provider(RuntimeError("Add `permissions: id-token: write`"))
    error = h.failure(h.op_request(h.client(h.credentials(broken))))
    assert isinstance(error, WorkloadIdentityError)
    assert error.code == "provider_failed"
    assert "permissions: id-token: write" in str(error)
    assert isinstance(error.__cause__, RuntimeError)
    assert broken.calls == EXCHANGE_ATTEMPTS
    assert h.api.count == 0


@scenario
def empty_or_non_string_assertions_are_provider_failures(h: Harness) -> None:
    for provider in (Provider(""), lambda: None, lambda: 12345):
        credentials = h.credentials(provider)  # type: ignore[arg-type]
        error = h.failure(h.op_resolve(credentials))
        assert isinstance(error, WorkloadIdentityError)
        assert error.code == "provider_failed"
    assert h.token.count == 0


@scenario
def unusable_expires_in_values_fall_back_to_300_seconds(h: Harness) -> None:
    for expires_in in ("300", 0, -5, True, None):
        h.token.expires_in = expires_in
        h.clock.time = 0
        credentials = h.credentials()
        client = h.client(credentials)
        before = h.token.count

        h.get(client)
        h.clock.time = 239
        h.get(client)
        assert h.token.count == before + 1, expires_in
        h.clock.time = 241
        h.get(client)
        assert h.token.count == before + 2, expires_in


@scenario
def an_assertion_echoed_by_the_server_is_redacted(h: Harness) -> None:
    assertion = "SECRET-ASSERTION-VALUE"
    h.token.script.append(
        oauth_error(f"bad_{assertion}", f"assertion {assertion} was rejected")
    )

    error = h.failure(h.op_resolve(h.credentials(Provider(assertion))))

    assert isinstance(error, WorkloadIdentityError)
    assert error.code == "bad_[redacted]"
    assert error.description == "assertion [redacted] was rejected"
    assert secrets_in(error, assertion) == []
    assert locals_showing(error, assertion) == []


@scenario
def an_unreachable_token_endpoint_is_described_by_its_host_and_the_reason(
    h: Harness,
) -> None:
    refused = "[Errno 111] Connection refused"
    untrusted = (
        "[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: "
        "unable to get local issuer certificate (_ssl.c:1006)"
    )
    # The error httpx2 raises, its text, and the reason the description gives.
    failures = [
        (httpx2.ConnectError, "[Errno -2] Name or service not known", None),
        (httpx2.ConnectError, refused, None),
        (httpx2.ConnectError, "All connection attempts failed", None),
        (httpx2.ConnectError, untrusted, None),
        (httpx2.ConnectTimeout, "timed out", None),
        (httpx2.ReadTimeout, "The read operation timed out", None),
        # A timeout with no text.
        (httpx2.ConnectTimeout, "", "timed out"),
        (httpx2.ReadTimeout, "", "timed out"),
        (httpx2.ReadError, "", "unknown network error"),
        (httpx2.ReadError, "[Errno 104] Connection reset by peer", None),
    ]

    for kind, text, reason in failures:
        h.token.script.extend(kind(text) for _ in range(EXCHANGE_ATTEMPTS))
        error = h.failure(h.op_resolve(h.credentials()))

        assert isinstance(error, WorkloadIdentityError)
        assert error.code == "exchange_failed"
        assert error.description == unreachable(reason or text)
        # The sentence for the code comes first, as for every other failure.
        assert str(error) == (
            "exchange_failed: The token endpoint could not be reached or kept "
            f"failing. Check the token URL and try again. {error.description}"
        )
        # Not chained: the transport error's request holds the assertion.
        assert error.__cause__ is None


@scenario
def an_unreachable_token_endpoint_shows_only_the_host_and_port_of_its_url(
    h: Harness,
) -> None:
    token_url = "https://url-user:url-password@token.test:8443/url-path?url-query=1"
    h.token.script.extend(
        httpx2.ConnectError("[Errno 111] Connection refused")
        for _ in range(EXCHANGE_ATTEMPTS)
    )

    error = h.failure(h.op_resolve(h.credentials(token_url=token_url)))

    assert isinstance(error, WorkloadIdentityError)
    assert error.description == unreachable(
        "[Errno 111] Connection refused", host="token.test:8443"
    )
    assert secrets_in(error, "url-user", "url-password", "url-path", "url-query") == []


@scenario
def a_malformed_token_response_is_not_quoted(h: Harness) -> None:
    # The HTTP parser quotes the line it could not read. When the framing is
    # broken, that line is the body, which holds the access token.
    access_token = "SECRET-ACCESS-VALUE"
    body = '{"access_token":"' + access_token + '"}'
    quoted = f"illegal chunk header: bytearray(b'{body}\\r\\n')"
    h.token.script.extend(
        httpx2.RemoteProtocolError(quoted) for _ in range(EXCHANGE_ATTEMPTS)
    )

    error = h.failure(h.op_resolve(h.credentials()))

    assert isinstance(error, WorkloadIdentityError)
    assert error.code == "exchange_failed"
    assert error.description == unreachable(
        "the server did not send a valid HTTP response"
    )
    assert secrets_in(error, access_token) == []


@scenario
def an_assertion_in_a_transport_error_is_redacted(h: Harness) -> None:
    assertion = "SECRET-ASSERTION-VALUE"
    h.token.script.extend(
        httpx2.ReadError(f"could not send {assertion}")
        for _ in range(EXCHANGE_ATTEMPTS)
    )

    error = h.failure(h.op_resolve(h.credentials(Provider(assertion))))

    assert isinstance(error, WorkloadIdentityError)
    assert error.description == unreachable("could not send [redacted]")
    assert secrets_in(error, assertion) == []
    assert locals_showing(error, assertion) == []


@scenario
def a_repeated_assertion_is_replaced_before_the_description_is_cut(
    h: Harness,
) -> None:
    assertion = "SECRET-ASSERTION-VALUE"
    # Cut first, the 500 characters would end with the start of the assertion.
    h.token.script.append(oauth_error("invalid_grant", "x" * 495 + assertion))

    error = h.failure(h.op_resolve(h.credentials(Provider(assertion))))

    assert isinstance(error, WorkloadIdentityError)
    assert error.description == "x" * 495 + "[reda"
    assert "SECRE" not in str(error)


@scenario
def a_long_error_description_is_cut_to_500_characters(h: Harness) -> None:
    h.token.script.append(oauth_error("invalid_grant", "x" * 2000))

    error = h.failure(h.op_resolve(h.credentials()))

    assert isinstance(error, WorkloadIdentityError)
    assert error.description == "x" * 500


@scenario
def a_per_request_authorization_header_wins_over_a_static_key_only(
    h: Harness,
) -> None:
    # With an API key the per-request header wins, as it always has.
    static = h.client(api_key="sk_test_static")
    h.get(
        static,
        request_options={"extra_headers": {"Authorization": "Bearer per-request"}},
    )
    assert h.api.requests[-1].bearer == "per-request"

    # With credentials, the snapshot overwrites it, whatever its case, and the
    # request is recovered from a 401 like any other.
    client = h.client(h.credentials())
    for name in ("Authorization", "authorization"):
        h.get(client, request_options={"extra_headers": {name: "Bearer per-request"}})
        assert h.api.requests[-1].headers["authorization"] == "Bearer access-1"
        assert h.api.requests[-1].headers["x-url-environment-id"] == ENVIRONMENT_ID
    h.api.script.append(unauthorized())
    h.get(
        client,
        request_options={"extra_headers": {"Authorization": "Bearer per-request"}},
    )
    assert h.api.bearers()[-2:] == ["access-1", "access-2"]
    assert h.token.count == 2


@scenario
def an_exchange_that_outruns_its_deadline_is_given_up(h: Harness) -> None:
    h.monkeypatch.setattr(workload_identity, "EXCHANGE_DEADLINE_SECONDS", 0.05)
    h.monkeypatch.setattr(workload_identity, "_DEADLINE_GRACE_SECONDS", 0.01)
    stuck = threading.Event()
    calls = Counter()

    def provider() -> str:
        calls.increment()
        if calls.value == 1:
            # Never returns in time. A thread cannot be interrupted.
            stuck.wait(10)
        return "assertion-1"

    credentials = h.credentials(provider)
    try:
        error = h.failure(h.op_resolve(credentials))
        assert isinstance(error, WorkloadIdentityError)
        assert error.code == "exchange_failed"
        assert "did not finish" in error.description

        # The stuck exchange does not block the next one.
        assert h.resolve(credentials).headers["Authorization"] == "Bearer access-1"
        assert calls.value == 2
    finally:
        stuck.set()


@scenario
def a_provider_reads_the_context_of_the_caller_that_started_the_exchange(
    h: Harness,
) -> None:
    # Set by the caller, as a web framework does per request. The exchange
    # runs on another thread, in a copy of the caller's context.
    assertion: contextvars.ContextVar[str] = contextvars.ContextVar("assertion")
    reset = assertion.set("assertion-from-the-context")
    try:
        h.get(h.client(h.credentials(assertion.get)))
    finally:
        assertion.reset(reset)

    assert h.token.forms()[0]["assertion"] == "assertion-from-the-context"
    assert h.token.count == 1
    assert h.sleeps == []


@scenario
def the_thread_of_an_exchange_ends_with_the_exchange(h: Harness) -> None:
    credentials = h.credentials()
    before = threading.enumerate()
    h.token.hold()

    waiter = h.start(h.op_resolve(credentials))
    h.wait_until(h.token.entered.is_set)
    started = [thread for thread in threading.enumerate() if thread not in before]
    exchanging = [
        thread
        for thread in started
        if thread.name == "workos-workload-identity-exchange"
    ]
    assert len(exchanging) == 1
    # A daemon: an exchange in flight does not keep the interpreter alive.
    assert exchanging[0].daemon
    h.token.release()
    snapshot = h.outcome(waiter)

    assert snapshot.headers["Authorization"] == "Bearer access-1"
    exchanging[0].join(10)
    assert not exchanging[0].is_alive()
    assert credentials._inflight is None


@scenario
def credentials_can_be_resolved_without_a_client(h: Harness) -> None:
    credentials = h.credentials()

    snapshot = h.resolve(credentials)

    assert dict(snapshot.headers) == {
        "Authorization": "Bearer access-1",
        "x-url-environment-id": ENVIRONMENT_ID,
    }
    assert snapshot.recoverable is True
    assert snapshot.generation == 1
    assert "access-1" not in repr(snapshot)
    assert h.resolve(credentials) == snapshot


@scenario
def a_workload_identity_client_cannot_start_the_feature_flags_runtime(
    h: Harness,
) -> None:
    # The runtime client polls outside the request path, with the API key. It
    # refuses a client that has none instead of polling unauthenticated.
    client = h.client(h.credentials())

    with pytest.raises(ConfigurationError):
        client.create_feature_flags_runtime_client()


# --- the API key as the client secret -------------------------------------------------
#
# The sign-in calls, the SSO code exchange and session refresh send the API key
# in the request body, as ``client_secret``. They read it through
# ``_client_secret``.

COOKIE_PASSWORD = Fernet.generate_key().decode("utf-8")


def client_secret_error(method: str) -> str:
    return (
        f"{method} needs an API key: this request sends it as the client secret. "
        "A client that authenticates with workload identity has no API key, so "
        "use a client built with one for this call."
    )


def load_session(client: Any) -> Any:
    """A session of ``client`` whose sealed cookie holds a refresh token."""
    sealed = seal_data(
        {"refresh_token": "rt_old", "user": {"id": "user_01"}}, COOKIE_PASSWORD
    )
    return client.user_management.load_sealed_session(
        session_data=sealed, cookie_password=COOKIE_PASSWORD
    )


@scenario
def the_client_secret_is_the_api_key_of_a_client_that_has_one(h: Harness) -> None:
    client = h.client(api_key="sk_test_static", client_id=CLIENT_ID)

    assert client._client_secret("authenticate_with_password") == "sk_test_static"


@scenario
def a_client_with_no_api_key_and_no_credentials_leaves_the_client_secret_out(
    h: Harness,
) -> None:
    # A public client in a PKCE flow. None tells the caller to send no field.
    for client in (
        h.client(client_id=CLIENT_ID),
        h.client(client_id=CLIENT_ID, is_public=True),
    ):
        assert client._client_secret("authenticate_with_code") is None


@scenario
def a_workload_identity_client_has_no_client_secret_to_send(h: Harness) -> None:
    provider = Provider()
    client = h.client(h.credentials(provider))

    with pytest.raises(ConfigurationError) as caught:
        client._client_secret("authenticate_with_password")

    assert str(caught.value) == client_secret_error("authenticate_with_password")
    assert provider.calls == 0
    assert h.token.count == 0
    assert h.api.count == 0


@scenario
def a_workload_identity_client_cannot_refresh_a_session(h: Harness) -> None:
    provider = Provider()
    client = h.client(h.credentials(provider), client_id=CLIENT_ID)
    session = load_session(client)

    # Raised, not returned as a failed refresh, and before anything is sent.
    error = h.failure(lambda: session.refresh())

    assert isinstance(error, ConfigurationError)
    assert str(error) == client_secret_error("refresh")
    assert provider.calls == 0
    assert h.token.count == 0
    assert h.api.count == 0


@scenario
def session_refresh_is_unchanged_for_a_client_without_credentials(h: Harness) -> None:
    with_key = h.client(api_key="sk_test_static", client_id=CLIENT_ID)
    h.run(lambda: load_session(with_key).refresh())
    body = json.loads(h.api.requests[-1].content)
    assert body["client_secret"] == "sk_test_static"
    assert body["refresh_token"] == "rt_old"

    public = h.client(client_id=CLIENT_ID, is_public=True)
    h.run(lambda: load_session(public).refresh())
    body = json.loads(h.api.requests[-1].content)
    assert body.get("client_secret") is None
    assert body["refresh_token"] == "rt_old"
    assert "authorization" not in h.api.requests[-1].headers

    assert h.api.count == 2
    assert h.token.count == 0


@scenario
def a_public_client_still_exchanges_a_code_with_pkce(h: Harness) -> None:
    client = h.client(client_id=CLIENT_ID, is_public=True)
    h.api.script.append(Reply(200, load_fixture("authenticate_response.json")))
    h.api.script.append(Reply(200, load_fixture("sso_token_response.json")))

    authenticated = h.run(
        lambda: client.user_management.authenticate_with_code_pkce(
            code="code-1", code_verifier="verifier-1"
        )
    )
    profile = h.run(
        lambda: client.sso.get_profile_and_token_pkce(
            code="code-2", code_verifier="verifier-2"
        )
    )

    assert isinstance(authenticated, AuthenticateResponse)
    assert isinstance(profile, SSOTokenResponse)
    assert [json.loads(request.content) for request in h.api.requests] == [
        {
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "code": "code-1",
            "code_verifier": "verifier-1",
        },
        {
            "client_id": CLIENT_ID,
            "code": "code-2",
            "grant_type": "authorization_code",
            "code_verifier": "verifier-2",
        },
    ]
    assert h.api.bearers() == [None, None]
    assert h.token.count == 0


# --- one client only -----------------------------------------------------------------


def test_sync_client_rejects_an_asynchronous_provider(sync_harness: Harness) -> None:
    h = sync_harness
    calls = Counter()

    async def provider() -> str:
        calls.increment()
        return "assertion-1"

    error = h.failure(h.op_resolve(h.credentials(provider)))

    assert isinstance(error, WorkloadIdentityError)
    assert error.code == "provider_failed"
    assert "AsyncWorkOSClient" in error.description
    # Not retried: calling it again cannot help.
    assert calls.value == 0 and h.sleeps == []
    assert h.token.count == 0


def test_sync_waiter_times_out_without_failing_the_exchange(
    sync_harness: Harness,
) -> None:
    h = sync_harness
    credentials = h.credentials()
    h.token.hold()

    with pytest.raises(WorkOSTimeoutError):
        credentials.resolve(timeout=0.05)

    h.token.release()
    assert credentials.resolve().headers["Authorization"] == "Bearer access-1"
    assert h.token.count == 1


def test_an_exchange_given_up_at_its_deadline_does_not_publish_a_late_token(
    sync_harness: Harness,
) -> None:
    h = sync_harness
    usual_deadline = workload_identity.EXCHANGE_DEADLINE_SECONDS
    h.monkeypatch.setattr(workload_identity, "EXCHANGE_DEADLINE_SECONDS", 0.3)
    h.monkeypatch.setattr(workload_identity, "_DEADLINE_GRACE_SECONDS", 0.01)
    late = HeldReply(
        200, {"access_token": "access-late", "token_type": "Bearer", "expires_in": 300}
    )
    h.token.script.append(late)
    credentials = h.credentials()
    before = threading.enumerate()

    try:
        # The first exchange is still waiting for its response at the deadline.
        waiter = h.start(h.op_resolve(credentials))
        h.wait_until(h.token.entered.is_set)
        abandoned = [t for t in threading.enumerate() if t not in before]
        error = h.outcome(waiter)
        assert isinstance(error, WorkloadIdentityError)
        assert "did not finish" in error.description

        # The next one succeeds and stores its token.
        h.monkeypatch.setattr(
            workload_identity, "EXCHANGE_DEADLINE_SECONDS", usual_deadline
        )
        current = h.resolve(credentials)
        assert current.headers["Authorization"] == "Bearer access-1"
    finally:
        late.release.set()
    # The first exchange now gets its response. It failed at the deadline, so
    # the token it comes back with replaces nothing.
    for thread in abandoned:
        thread.join(10)
        assert not thread.is_alive()

    assert h.resolve(credentials) == current
    assert h.token.count == 2


def test_async_client_awaits_a_coroutine_provider(async_harness: Harness) -> None:
    h = async_harness
    threads: List[int] = []

    async def provider() -> str:
        threads.append(threading.get_ident())
        await asyncio.sleep(0)
        return "assertion-async"

    h.get(h.client(h.credentials(provider)))

    assert h.token.forms()[0]["assertion"] == "assertion-async"
    # Awaited on the event loop, not sent to a worker thread.
    assert threads == [threading.get_ident()]


def test_an_awaited_provider_reads_the_context_of_the_caller_too(
    async_harness: Harness,
) -> None:
    h = async_harness
    assertion: contextvars.ContextVar[str] = contextvars.ContextVar("assertion")

    async def provider() -> str:
        await asyncio.sleep(0)
        return assertion.get()

    reset = assertion.set("assertion-from-the-context")
    try:
        h.get(h.client(h.credentials(provider)))
    finally:
        assertion.reset(reset)

    assert h.token.forms()[0]["assertion"] == "assertion-from-the-context"
    assert h.token.count == 1
    assert h.sleeps == []


def test_async_client_awaits_a_callable_object_with_an_async_call(
    async_harness: Harness,
) -> None:
    h = async_harness

    class AsyncProvider:
        async def __call__(self) -> str:
            return "assertion-object"

    h.get(h.client(h.credentials(AsyncProvider())))

    assert h.token.forms()[0]["assertion"] == "assertion-object"


def test_async_client_runs_a_blocking_provider_off_the_event_loop(
    async_harness: Harness,
) -> None:
    h = async_harness
    provider = Provider()

    h.get(h.client(h.credentials(provider)))

    assert provider.calls == 1
    assert provider.threads != [threading.get_ident()]


def test_async_client_awaits_an_awaitable_from_a_plain_callable(
    async_harness: Harness,
) -> None:
    h = async_harness

    async def fetch() -> str:
        return "assertion-lambda"

    h.get(h.client(h.credentials(lambda: fetch())))

    assert h.token.forms()[0]["assertion"] == "assertion-lambda"


def test_async_waiter_times_out_without_failing_the_exchange(
    async_harness: Harness,
) -> None:
    h = async_harness
    credentials = h.credentials()
    h.token.hold()

    error = h.failure(h.op_resolve(credentials, timeout=0.05))
    assert isinstance(error, WorkOSTimeoutError)

    h.token.release()
    assert h.resolve(credentials).headers["Authorization"] == "Bearer access-1"
    assert h.token.count == 1


def test_an_exchange_outlives_the_caller_that_started_it(
    async_harness: AsyncHarness,
) -> None:
    h = async_harness
    credentials = h.credentials()
    h.token.hold()

    async def start_an_exchange_and_be_canceled() -> Any:
        starter = h.loop.create_task(credentials.aresolve())
        while not h.token.entered.is_set():
            await asyncio.sleep(0.001)
        starter.cancel()
        return (await asyncio.gather(starter, return_exceptions=True))[0]

    gave_up = h.loop.run_until_complete(
        asyncio.wait_for(start_an_exchange_and_be_canceled(), 10)
    )
    assert isinstance(gave_up, asyncio.CancelledError)

    # The exchange it started is still the one in flight, and serves the next.
    h.token.release()
    assert h.resolve(credentials).headers["Authorization"] == "Bearer access-1"
    assert h.token.count == 1


def test_an_exchange_does_not_need_the_event_loop_that_started_it(
    network: Network,
) -> None:
    provider = Provider()
    credentials = WorkloadIdentityCredentials(
        identity_token_provider=provider, client_id=CLIENT_ID, token_url=TOKEN_URL
    )
    network.token.hold()

    async def give_up() -> None:
        with pytest.raises(WorkOSTimeoutError):
            await credentials.aresolve(timeout=0.05)

    # The loop that started the exchange is closed while the exchange waits
    # for its response.
    asyncio.run(give_up())
    assert network.token.entered.is_set()
    network.token.release()

    assert credentials.resolve().headers["Authorization"] == "Bearer access-1"
    assert asyncio.run(credentials.aresolve()).generation == 1
    assert network.token.count == 1
    assert provider.calls == 1


def test_one_credentials_instance_serves_both_kinds_of_client(
    sync_harness: Harness, async_harness: Harness
) -> None:
    credentials = sync_harness.credentials()
    async_harness.instrument(credentials)
    sync_client = sync_harness.client(credentials)
    async_client = async_harness.client(credentials)

    sync_harness.get(sync_client)
    async_harness.get(async_client)
    assert sync_harness.token.count == 1

    # Past the refresh threshold, whichever client asks first exchanges.
    async_harness.clock.time = 241
    async_harness.get(async_client)
    sync_harness.get(sync_client)

    assert sync_harness.token.count == 2
    assert sync_harness.api.bearers() == [
        "access-1",
        "access-1",
        "access-2",
        "access-2",
    ]


def beside_an_async_exchange(
    h: AsyncHarness, client: Any, joins: Counter, second: Operation
) -> List[Any]:
    """Run ``second`` on a thread while ``client``'s exchange is held back.

    The event loop keeps running throughout, as it does in an application.
    Returns the outcome of the asynchronous request, then that of ``second``.
    """

    async def scene() -> List[Any]:
        first = h.loop.create_task(client.request("GET", ("organizations",)))
        while not h.token.entered.is_set():
            await asyncio.sleep(0.001)
        other = _ThreadCaller(second)
        other.thread.start()
        while joins.value < 2:
            await asyncio.sleep(0.001)
        h.token.release()
        outcome = (await asyncio.gather(first, return_exceptions=True))[0]
        while other.thread.is_alive():
            await asyncio.sleep(0.001)
        return [outcome, other.outcome]

    return h.loop.run_until_complete(asyncio.wait_for(scene(), 10))


def test_a_coroutine_joins_the_exchange_a_synchronous_caller_started(
    sync_harness: Harness, async_harness: Harness
) -> None:
    provider = Provider()
    credentials = sync_harness.credentials(provider)
    joins = sync_harness.watch_joins(credentials)
    sync_client = sync_harness.client(credentials)
    async_client = async_harness.client(credentials)
    token = sync_harness.token
    token.hold()

    blocking = sync_harness.start(sync_harness.op_request(sync_client))
    sync_harness.wait_until(token.entered.is_set)
    awaiting = async_harness.start(async_harness.op_request(async_client))
    async_harness.wait_until(lambda: joins.value == 2)
    token.release()

    assert async_harness.outcome(awaiting) == {"ok": True}
    assert sync_harness.outcome(blocking) == {"ok": True}
    assert token.count == 1
    assert provider.calls == 1
    assert sync_harness.api.bearers() == ["access-1", "access-1"]


def test_a_thread_joins_the_exchange_a_coroutine_started(
    sync_harness: Harness, async_harness: AsyncHarness
) -> None:
    provider = Provider()
    credentials = async_harness.credentials(provider)
    joins = async_harness.watch_joins(credentials)
    sync_client = sync_harness.client(credentials)
    async_client = async_harness.client(credentials)
    async_harness.token.hold()

    outcomes = beside_an_async_exchange(
        async_harness, async_client, joins, sync_harness.op_request(sync_client)
    )

    assert outcomes == [{"ok": True}, {"ok": True}]
    assert async_harness.token.count == 1
    assert provider.calls == 1
    assert async_harness.api.bearers() == ["access-1", "access-1"]


def test_a_coroutine_on_another_event_loop_joins_the_exchange(
    async_harness: AsyncHarness,
) -> None:
    h = async_harness
    provider = Provider()
    credentials = h.credentials(provider)
    joins = h.watch_joins(credentials)
    client = h.client(credentials)
    h.token.hold()

    def on_another_loop() -> Any:
        async def request() -> Any:
            async with AsyncWorkOSClient(
                base_url=API_URL, credentials=credentials
            ) as other:
                return await other.request("GET", ("organizations",))

        return asyncio.run(request())

    outcomes = beside_an_async_exchange(h, client, joins, on_another_loop)

    assert outcomes == [{"ok": True}, {"ok": True}]
    assert h.token.count == 1
    assert provider.calls == 1
    assert h.api.bearers() == ["access-1", "access-1"]


def test_a_blocking_call_on_the_event_loop_joins_the_exchange_a_coroutine_started(
    sync_harness: Harness, async_harness: AsyncHarness
) -> None:
    # A synchronous client called from a coroutine blocks the event loop. The
    # exchange runs on a thread of its own, so it finishes all the same, and
    # the blocking call gets its token.
    provider = Provider()
    credentials = async_harness.credentials(provider)
    sync_client = sync_harness.client(credentials)
    async_client = async_harness.client(credentials)
    token = async_harness.token
    token.hold()

    async def scene() -> List[Any]:
        first = async_harness.loop.create_task(
            async_client.request("GET", ("organizations",))
        )
        while not token.entered.is_set():
            await asyncio.sleep(0.001)
        # Nothing on this loop runs during the blocking call, so a timer on a
        # thread of its own lets the token endpoint answer.
        threading.Timer(0.05, token.release).start()
        blocked = sync_client.request("GET", ("organizations",))
        return [blocked, await first]

    outcomes = async_harness.loop.run_until_complete(asyncio.wait_for(scene(), 10))

    assert outcomes == [{"ok": True}, {"ok": True}]
    assert token.count == 1
    assert provider.calls == 1
    assert async_harness.api.bearers() == ["access-1", "access-1"]


def test_a_blocking_call_with_an_asynchronous_provider_fails_at_once(
    sync_harness: Harness, async_harness: AsyncHarness
) -> None:
    # The provider is awaited on the event loop, which the blocking call
    # blocks. It is refused before it can wait for an exchange that needs
    # that loop.
    calls = Counter()

    async def provider() -> str:
        calls.increment()
        return "assertion-1"

    credentials = async_harness.credentials(provider)
    sync_client = sync_harness.client(credentials)
    async_client = async_harness.client(credentials)
    token = async_harness.token
    token.hold()

    async def scene() -> List[Any]:
        first = async_harness.loop.create_task(
            async_client.request("GET", ("organizations",))
        )
        while not token.entered.is_set():
            await asyncio.sleep(0.001)
        with pytest.raises(WorkloadIdentityError) as refused:
            sync_client.request("GET", ("organizations",))
        token.release()
        return [refused.value, await first]

    refused, outcome = async_harness.loop.run_until_complete(
        asyncio.wait_for(scene(), 10)
    )

    assert refused.code == "provider_failed"
    assert "AsyncWorkOSClient" in refused.description
    assert outcome == {"ok": True}
    assert token.count == 1
    assert calls.value == 1


def test_a_blocking_call_ends_at_the_deadline_when_the_provider_needs_the_loop_it_blocks(
    sync_harness: Harness, async_harness: AsyncHarness
) -> None:
    # A plain callable that returns an awaitable is known to be asynchronous
    # only once it is called. A blocking call that joins such an exchange
    # blocks the loop the awaitable needs. The exchange gives the provider
    # until its deadline, then fails for everyone. No second one is started.
    h = async_harness
    h.monkeypatch.setattr(workload_identity, "EXCHANGE_DEADLINE_SECONDS", 0.3)
    h.monkeypatch.setattr(workload_identity, "_DEADLINE_GRACE_SECONDS", 0.05)
    entered = threading.Event()
    calls = Counter()

    async def fetch() -> str:
        entered.set()
        await asyncio.Event().wait()
        return "assertion-1"

    def provider() -> Any:
        calls.increment()
        return fetch()

    credentials = h.credentials(provider)
    sync_client = sync_harness.client(credentials)
    async_client = h.client(credentials)

    async def scene() -> List[Any]:
        first = h.loop.create_task(async_client.request("GET", ("organizations",)))
        while not entered.is_set():
            await asyncio.sleep(0.001)
        started = time.monotonic()
        with pytest.raises(WorkloadIdentityError) as blocked:
            sync_client.request("GET", ("organizations",))
        waited = time.monotonic() - started
        outcome = (await asyncio.gather(first, return_exceptions=True))[0]
        return [blocked.value, waited, outcome]

    blocked, waited, outcome = h.loop.run_until_complete(asyncio.wait_for(scene(), 10))

    assert blocked.code == "provider_failed"
    assert "did not return before the exchange's deadline" in blocked.description
    assert waited < 5
    # The asynchronous caller waited for the same exchange.
    assert outcome is blocked
    assert calls.value == 1
    assert h.token.count == 0


def test_an_exchange_in_flight_does_not_keep_the_interpreter_alive() -> None:
    script = """
import threading

from workos import WorkloadIdentityCredentials
from workos._errors import WorkOSTimeoutError


def provider() -> str:
    threading.Event().wait()  # never returns
    return ""


credentials = WorkloadIdentityCredentials(
    identity_token_provider=provider,
    client_id="client_wif_test",
    token_url="https://token.invalid/oauth2/token",
)
try:
    credentials.resolve(timeout=0.05)
except WorkOSTimeoutError:
    print("gave up with the exchange in flight")
"""
    # The interpreter does not wait for the exchange's thread.
    finished = subprocess.run(
        [sys.executable, "-c", script], capture_output=True, text=True, timeout=30
    )

    assert finished.returncode == 0, finished.stderr
    assert finished.stdout.strip() == "gave up with the exchange in flight"


# --- the real HTTP stack ---------------------------------------------------------------

both_clients = pytest.mark.parametrize(
    "asynchronous", [False, True], ids=["sync", "async"]
)


def real_failure(token_url: str, asynchronous: bool) -> WorkloadIdentityError:
    """Exchange at ``token_url`` with nothing mocked, and return the error raised."""
    credentials = WorkloadIdentityCredentials(
        client_id=CLIENT_ID, token_url=token_url, identity_token_provider=Provider()
    )
    credentials._sleep = lambda seconds: None
    with pytest.raises(WorkloadIdentityError) as raised:
        if asynchronous:
            asyncio.run(credentials.aresolve())
        else:
            credentials.resolve()
    assert raised.value.code == "exchange_failed"
    assert raised.value.__cause__ is None
    return raised.value


@both_clients
def test_a_token_host_that_does_not_resolve_names_the_reason(
    asynchronous: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    asked: List[object] = []

    def no_such_name(host: object, *args: object, **kwargs: object) -> None:
        asked.append(host.decode() if isinstance(host, bytes) else host)
        raise socket.gaierror(-2, "Name or service not known")

    monkeypatch.setattr(socket, "getaddrinfo", no_such_name)

    error = real_failure("https://token.invalid:8443/oauth2/token", asynchronous)

    assert error.description == unreachable(
        "[Errno -2] Name or service not known", host="token.invalid:8443"
    )
    assert asked == ["token.invalid"] * EXCHANGE_ATTEMPTS


@both_clients
def test_a_token_endpoint_that_refuses_the_connection_names_the_reason(
    asynchronous: bool,
) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as closed:
        closed.bind(("127.0.0.1", 0))
        host = f"127.0.0.1:{closed.getsockname()[1]}"

    error = real_failure(f"https://{host}/oauth2/token", asynchronous)

    # The number differs by platform: 111 on Linux, 61 on macOS.
    refused = f"[Errno {errno.ECONNREFUSED}] {os.strerror(errno.ECONNREFUSED)}"
    assert refused.endswith("Connection refused")
    # Both clients name the operating system's error: the exchange is sent
    # the same way for both.
    assert error.description == unreachable(refused, host=host)


@both_clients
def test_a_token_endpoint_that_does_not_answer_names_the_reason(
    asynchronous: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    # One short attempt: its timeout is a quarter of the deadline, and the
    # backoff that would follow is longer than what is left.
    monkeypatch.setattr(workload_identity, "EXCHANGE_DEADLINE_SECONDS", 0.6)
    # A listener that never accepts: the connection opens through its backlog
    # and the TLS handshake gets no answer.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as silent:
        silent.bind(("127.0.0.1", 0))
        silent.listen(1)
        host = f"127.0.0.1:{silent.getsockname()[1]}"

        error = real_failure(f"https://{host}/oauth2/token", asynchronous)

    # The interpreter's words, such as "The handshake operation timed out".
    said = error.description
    assert said.startswith(f"The request to the token endpoint at {host} failed: ")
    assert said.endswith("timed out.")


# --- configuration -------------------------------------------------------------------


@pytest.mark.parametrize(
    ("settings", "description"),
    [
        ({"token_url": TOKEN_URL}, "client_id is required (or set WORKOS_CLIENT_ID)"),
        ({"client_id": CLIENT_ID}, "token_url is required"),
        ({"client_id": CLIENT_ID, "token_url": ""}, "token_url is required"),
    ],
)
def test_a_missing_required_setting_fails_at_construction(
    network: Network, settings: Dict[str, str], description: str
) -> None:
    with pytest.raises(WorkloadIdentityError) as caught:
        WorkloadIdentityCredentials(identity_token_provider=Provider(), **settings)

    assert caught.value.code == "invalid_configuration"
    assert caught.value.description == description
    assert caught.value.hint == (
        "Workload identity credentials are missing a required setting."
    )
    assert network.token.count == 0


@pytest.mark.parametrize(
    "token_url",
    [
        "http://example.com/oauth2/token",
        # Loopback hosts are no exception.
        "http://localhost:8080/oauth2/token",
        "http://127.0.0.1/oauth2/token",
        "http://[::1]/oauth2/token",
        # No host.
        "https:///oauth2/token",
        "https://:8443/oauth2/token",
        "https:token.test/oauth2/token",
        # No scheme.
        "token.test/oauth2/token",
        "//token.test/oauth2/token",
        "/oauth2/token",
        # Another scheme.
        "ftp://token.test/oauth2/token",
        # Not a URL the HTTP client can read.
        " https://token.test/oauth2/token",
        "\thttps://token.test/oauth2/token",
        "https://token.test:port/oauth2/token",
    ],
)
def test_a_token_url_that_is_not_absolute_https_fails_at_construction(
    network: Network, token_url: str
) -> None:
    with pytest.raises(WorkloadIdentityError) as caught:
        WorkloadIdentityCredentials(
            identity_token_provider=Provider(),
            client_id=CLIENT_ID,
            token_url=token_url,
        )

    assert caught.value.code == "invalid_configuration"
    assert caught.value.description == "token_url must be an absolute https URL"
    assert str(caught.value) == (
        "invalid_configuration: Workload identity credentials are missing a "
        "required setting. token_url must be an absolute https URL"
    )
    assert caught.value.__cause__ is None
    assert network.token.count == 0


def test_the_token_url_scheme_is_not_case_sensitive(network: Network) -> None:
    token_url = "HTTPS://token.test/oauth2/token"
    credentials = WorkloadIdentityCredentials(
        identity_token_provider=Provider(),
        client_id=CLIENT_ID,
        token_url=token_url,
    )
    assert credentials.token_url == token_url

    with WorkOSClient(base_url=API_URL, credentials=credentials) as client:
        client.request("GET", ("organizations",))

    assert network.token.requests[0].url == TOKEN_URL
    assert network.api.bearers() == ["access-1"]


@pytest.mark.parametrize("environment_id", ["", None])
def test_an_empty_environment_id_counts_as_not_set(
    network: Network, environment_id: Optional[str]
) -> None:
    credentials = WorkloadIdentityCredentials(
        identity_token_provider=Provider(),
        client_id=CLIENT_ID,
        token_url=TOKEN_URL,
        environment_id=environment_id,
    )
    assert credentials.environment_id is None

    with WorkOSClient(base_url=API_URL, credentials=credentials) as client:
        client.request("GET", ("organizations",))

    assert network.api.bearers() == ["access-1"]
    assert "x-url-environment-id" not in network.api.requests[0].headers


@pytest.mark.parametrize("scope", ["", None])
def test_an_empty_scope_counts_as_not_set(
    network: Network, scope: Optional[str]
) -> None:
    credentials = WorkloadIdentityCredentials(
        identity_token_provider=Provider(),
        client_id=CLIENT_ID,
        token_url=TOKEN_URL,
        scope=scope,
    )
    assert credentials.scope is None

    with WorkOSClient(base_url=API_URL, credentials=credentials) as client:
        client.request("GET", ("organizations",))

    assert "scope" not in network.token.forms()[0]


def test_a_provider_that_is_not_callable_fails_at_construction(
    network: Network,
) -> None:
    with pytest.raises(WorkloadIdentityError) as caught:
        WorkloadIdentityCredentials(
            identity_token_provider="assertion-1",  # type: ignore[arg-type]
            client_id=CLIENT_ID,
            token_url=TOKEN_URL,
            environment_id=ENVIRONMENT_ID,
        )

    assert caught.value.code == "invalid_configuration"


def test_settings_are_read_only(network: Network) -> None:
    credentials = WorkloadIdentityCredentials(
        identity_token_provider=Provider(),
        client_id=CLIENT_ID,
        token_url=TOKEN_URL,
        environment_id=ENVIRONMENT_ID,
    )

    assert credentials.client_id == CLIENT_ID
    assert credentials.token_url == TOKEN_URL
    assert credentials.environment_id == ENVIRONMENT_ID
    assert credentials.resource == "https://api.workos.com"
    assert credentials.scope is None
    with pytest.raises(AttributeError):
        credentials.token_url = "https://elsewhere.test"  # type: ignore[misc]
    assert "access" not in repr(credentials)


def test_the_environment_alone_never_turns_workload_identity_on(
    network: Network, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("WORKOS_CLIENT_ID", "client_env")
    monkeypatch.setenv("WORKOS_API_KEY", "sk_test_env")

    with WorkOSClient(base_url=API_URL) as client:
        client.request("GET", ("organizations",))

    assert network.token.count == 0
    assert network.api.bearers() == ["sk_test_env"]
    assert "x-url-environment-id" not in network.api.requests[0].headers


def test_an_empty_api_key_is_not_a_conflict(network: Network) -> None:
    credentials = WorkloadIdentityCredentials(
        identity_token_provider=Provider(),
        client_id=CLIENT_ID,
        token_url=TOKEN_URL,
        environment_id=ENVIRONMENT_ID,
    )

    with WorkOSClient(api_key="", credentials=credentials) as client:
        assert client._api_key is None


def test_a_public_client_cannot_take_credentials(network: Network) -> None:
    credentials = WorkloadIdentityCredentials(
        identity_token_provider=Provider(),
        client_id=CLIENT_ID,
        token_url=TOKEN_URL,
        environment_id=ENVIRONMENT_ID,
    )

    with pytest.raises(ValueError, match="public client"):
        WorkOSClient(client_id="client_123", is_public=True, credentials=credentials)


def test_token_file_and_token_env_fail_without_a_token(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with pytest.raises(FileNotFoundError):
        token_file(tmp_path / "missing")()

    empty = tmp_path / "empty"
    empty.write_text(" \n")
    with pytest.raises(ValueError, match="empty"):
        token_file(str(empty))()

    monkeypatch.delenv("MY_JWT", raising=False)
    with pytest.raises(ValueError, match="MY_JWT"):
        token_env("MY_JWT")()
    monkeypatch.setenv("MY_JWT", "")
    with pytest.raises(ValueError, match="MY_JWT"):
        token_env("MY_JWT")()


def test_token_env_reads_the_variable_on_every_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = token_env("MY_JWT")
    monkeypatch.setenv("MY_JWT", "assertion-1")
    assert provider() == "assertion-1"
    monkeypatch.setenv("MY_JWT", "assertion-2")
    assert provider() == "assertion-2"


# --- the static key and the header overlay ---------------------------------------------


def test_static_key_credentials_never_change() -> None:
    credentials = StaticKeyCredentials("sk_test_static")

    snapshot = credentials.resolve()

    assert dict(snapshot.headers) == {"Authorization": "Bearer sk_test_static"}
    assert (snapshot.generation, snapshot.recoverable) == (0, False)
    credentials.invalidate(0)
    assert credentials.resolve() is snapshot
    assert asyncio.run(credentials.aresolve()) is snapshot
    assert "sk_test_static" not in repr(snapshot)
    assert dict(StaticKeyCredentials(None).resolve().headers) == {}


def test_a_static_key_snapshot_leaves_the_request_headers_as_they_were() -> None:
    client = WorkOSClient(api_key="sk_test_static")
    headers = client._build_headers("post", "idem-1", None)
    snapshot = client._request_credentials(None).resolve()

    applied = apply_snapshot(headers, snapshot)

    assert list(applied.items()) == list(headers.items())
    assert list(applied) == [
        "Content-Type",
        "User-Agent",
        "Authorization",
        "Idempotency-Key",
    ]
    client.close()


def test_the_static_snapshot_follows_the_clients_current_key() -> None:
    client = WorkOSClient(api_key="sk_test_before")
    client._api_key = "sk_test_after"

    snapshot = client._request_credentials(None).resolve()

    assert snapshot.headers["Authorization"] == "Bearer sk_test_after"
    client.close()


def test_snapshot_headers_replace_a_header_of_any_case() -> None:
    snapshot = CredentialSnapshot(
        headers={
            "Authorization": "Bearer new",
            "x-url-environment-id": "environment_1",
        },
        generation=3,
        recoverable=True,
    )
    headers = {
        "authorization": "Bearer old",
        "AUTHORIZATION": "Bearer older",
        "X-Other": "1",
    }

    applied = apply_snapshot(headers, snapshot)

    assert applied == {
        "X-Other": "1",
        "Authorization": "Bearer new",
        "x-url-environment-id": "environment_1",
    }
    # The caller's dict is not modified; it is reused for the next attempt.
    assert headers["authorization"] == "Bearer old"


def test_every_error_code_has_a_hint() -> None:
    for code in (
        *OAUTH_CODES,
        "exchange_failed",
        "invalid_response",
        "provider_failed",
        "invalid_configuration",
    ):
        error = WorkloadIdentityError(code)
        assert error.hint and error.hint != "The token endpoint rejected the exchange."
        assert str(error) == f"{code}: {error.hint}"
    assert WorkloadIdentityError("some_new_code").hint == (
        "The token endpoint rejected the exchange."
    )
