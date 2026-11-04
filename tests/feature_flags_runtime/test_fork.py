# @oagen-ignore-file
"""What runtime clients do in a forked child process.

Each scenario runs in a subprocess so a hang or a fork cannot wedge pytest.
"""

from __future__ import annotations

import asyncio
import logging
import os
import subprocess
import sys
import textwrap
import time
import weakref
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import httpx2
import pytest

from workos import AsyncWorkOSClient, HTTPResponse, WorkOSClient
from workos.feature_flags.runtime import (
    AsyncFeatureFlagsRuntimeClient,
    FeatureFlagsConfiguration,
    FeatureFlagsRuntimeClient,
    _async,
    _core,
    _sync,
)

from tests.feature_flags_runtime.helpers import (
    API_KEY,
    FlagServer,
    LocalHTTPServer,
    flag,
    payload,
)

ROOT = Path(__file__).resolve().parents[2]
FORK_BLOCKED = "does not run in forked process"
BOOTSTRAP = payload(f=flag("f", default_value=True))

Make = Callable[..., FeatureFlagsRuntimeClient]
MakeAsync = Callable[..., AsyncFeatureFlagsRuntimeClient]

PRELUDE = """
import asyncio
import os
import time
import warnings

from workos import AsyncWorkOSClient, WorkOSClient
from workos.feature_flags.runtime import _policy
from tests.feature_flags_runtime.helpers import LocalHTTPServer, flag, payload

_policy.next_delay = lambda interval, failures, max_retry_delay: 0.05
server = LocalHTTPServer(payload(f=flag("f", default_value=True)))


def wait_for(predicate, timeout=5.0):
    deadline = time.monotonic() + timeout
    while not predicate():
        if time.monotonic() > deadline:
            raise SystemExit("timed out")
        time.sleep(0.01)


def fork():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        return os.fork()


def finish(pid):
    _, status = os.waitpid(pid, 0)
    raise SystemExit(os.waitstatus_to_exitcode(status))
"""

# The parent and child poll the parent's server with different API keys, so
# the server can tell whose connection each request came on.
DEFAULT_CLIENT = """
workos = WorkOSClient(api_key="sk_parent", base_url=server.base_url)
runtime = workos.create_feature_flags_runtime_client()
runtime.start()
runtime.wait_until_ready(timeout=5)
wait_for(lambda: len(server.ports("Bearer sk_parent")) >= 1 and len(server.requests) >= 3)
pid = fork()
if pid == 0:
    workos._api_key = "sk_child"
    # Reading any property is a use of the client that resumes polling.
    assert runtime.is_ready
    time.sleep(1.0)
    runtime.close()
    os._exit(0)
_, status = os.waitpid(pid, 0)
assert os.waitstatus_to_exitcode(status) == 0
time.sleep(0.2)
runtime.close()
child_requests = [r for r in server.requests if r["headers"].get("Authorization") == "Bearer sk_child"]
parent_ports = server.ports("Bearer sk_parent")
child_ports = server.ports("Bearer sk_child")
assert len(child_requests) >= 2, f"the child sent {len(child_requests)} polls"
assert not parent_ports & child_ports, f"shared connections: {parent_ports & child_ports}"
print(f"parent ports {sorted(parent_ports)}, child ports {sorted(child_ports)}")
"""

CALLER_CLIENT = """
import httpx2
import logging

logging.basicConfig(level=logging.WARNING)
workos = WorkOSClient(api_key="sk_parent", base_url=server.base_url, http_client=httpx2.Client())
runtime = workos.create_feature_flags_runtime_client()
runtime.start()
runtime.wait_until_ready(timeout=5)
pid = fork()
if pid == 0:
    workos._api_key = "sk_child"
    assert runtime.is_enabled("f") is True
    try:
        runtime.refresh()
        os._exit(2)
    except RuntimeError as error:
        assert "caller-supplied HTTP client" in str(error), error
    time.sleep(0.5)
    os._exit(0)
_, status = os.waitpid(pid, 0)
assert os.waitstatus_to_exitcode(status) == 0
runtime.close()
assert server.ports("Bearer sk_child") == set(), "the child polled"
"""

# asyncio refuses to run a loop inherited across fork, so the parent runs its
# loop on a thread (which the child does not inherit) and forks from the main
# thread, as a pre-fork server would.
ASYNC_CLIENT = """
import signal
import threading

loop = asyncio.new_event_loop()
threading.Thread(target=loop.run_forever, daemon=True).start()


def call(coroutine):
    return asyncio.run_coroutine_threadsafe(coroutine, loop).result(10)


workos = AsyncWorkOSClient(api_key="sk_parent", base_url=server.base_url)
runtime = call(_make_runtime(workos))
call(runtime.start())
call(runtime.wait_until_ready(timeout=5))
pid = fork()
if pid == 0:
    workos._api_key = "sk_child"
    assert runtime.is_enabled("f") is True
    for method in ("refresh", "start"):
        try:
            asyncio.run(getattr(runtime, method)())
            os._exit(2)
        except RuntimeError as error:
            assert "was used in the parent" in str(error), error
    # The parent's polling task is on a loop that does not run here, so
    # close() must not wait for it.
    signal.signal(signal.SIGALRM, lambda *args: os._exit(3))
    signal.alarm(5)
    asyncio.run(runtime.close())
    signal.alarm(0)
    time.sleep(0.5)
    os._exit(0)
_, status = os.waitpid(pid, 0)
assert os.waitstatus_to_exitcode(status) == 0
call(runtime.close())
call(workos.close())
assert server.ports("Bearer sk_child") == set(), "the child polled"
"""

MAKE_ASYNC_RUNTIME = """
async def _make_runtime(workos):
    return workos.create_feature_flags_runtime_client()
"""

MACOS_DEFAULT_CLIENT = """
import logging

logging.basicConfig(level=logging.WARNING)
workos = WorkOSClient(api_key="sk_parent", base_url=server.base_url)
runtime = workos.create_feature_flags_runtime_client()
runtime.start()
runtime.wait_until_ready(timeout=5)
pid = fork()
if pid == 0:
    workos._api_key = "sk_child"
    assert runtime.is_enabled("f") is True
    runtime.start()
    try:
        runtime.refresh()
        os._exit(2)
    except RuntimeError as error:
        assert "cannot safely open network connections" in str(error), error
    time.sleep(0.5)
    os._exit(0)
_, status = os.waitpid(pid, 0)
assert os.waitstatus_to_exitcode(status) == 0
runtime.close()
assert server.ports("Bearer sk_child") == set(), "the child polled"
"""

# The app is preloaded and each worker starts the runtime clients, as with
# gunicorn --preload.
MACOS_PRELOADED = """
import logging
import signal

from workos import FeatureFlagsConfiguration

logging.basicConfig(level=logging.WARNING)
bootstrap = FeatureFlagsConfiguration.from_dict(payload(f=flag("f", default_value=True)))
workos = WorkOSClient(api_key="sk_parent", base_url=server.base_url)
bootstrapped = workos.create_feature_flags_runtime_client(bootstrap=bootstrap)
empty = workos.create_feature_flags_runtime_client()
async_workos = AsyncWorkOSClient(api_key="sk_parent", base_url=server.base_url)
async_bootstrapped = async_workos.create_feature_flags_runtime_client(bootstrap=bootstrap)
pid = fork()
if pid == 0:
    workos._api_key = "sk_child"
    async_workos._api_key = "sk_child"
    signal.signal(signal.SIGALRM, lambda *args: os._exit(3))
    signal.alarm(10)
    bootstrapped.start()
    bootstrapped.wait_until_ready()
    assert bootstrapped.is_enabled("f") is True
    empty.start()
    try:
        empty.wait_until_ready()
        os._exit(2)
    except RuntimeError as error:
        assert "does not run in forked process" in str(error), error

    async def serve():
        await async_bootstrapped.start()
        await async_bootstrapped.wait_until_ready()
        assert async_bootstrapped.is_enabled("f") is True

    asyncio.run(serve())
    signal.alarm(0)
    time.sleep(0.5)
    os._exit(0)
_, status = os.waitpid(pid, 0)
assert os.waitstatus_to_exitcode(status) == 0
assert server.ports("Bearer sk_child") == set(), "the child polled"
"""

# The parent never polls, as when an app is preloaded and each worker starts
# the runtime client.
CALLER_CLIENT_UNUSED = """
import httpx2

workos = WorkOSClient(api_key="sk_parent", base_url=server.base_url, http_client=httpx2.Client())
runtime = workos.create_feature_flags_runtime_client()
pid = fork()
if pid == 0:
    workos._api_key = "sk_child"
    runtime.start()
    runtime.wait_until_ready(timeout=5)
    runtime.close()
    os._exit(0)
_, status = os.waitpid(pid, 0)
assert os.waitstatus_to_exitcode(status) == 0
assert server.ports("Bearer sk_child"), "the child never polled"
"""

ASYNC_CLIENT_UNUSED = """
workos = AsyncWorkOSClient(api_key="sk_parent", base_url=server.base_url)
runtime = workos.create_feature_flags_runtime_client()
pid = fork()
if pid == 0:
    workos._api_key = "sk_child"

    async def serve():
        await runtime.start()
        await runtime.wait_until_ready(timeout=5)
        await runtime.close()
        await workos.close()

    asyncio.run(serve())
    os._exit(0)
_, status = os.waitpid(pid, 0)
assert os.waitstatus_to_exitcode(status) == 0
assert server.ports("Bearer sk_child"), "the child never polled"
"""

# The runtime client never polls in the parent, but another SDK call does, on
# the HTTP client the runtime client would poll through.
CALLER_CLIENT_SDK_USED = """
import httpx2

workos = WorkOSClient(api_key="sk_parent", base_url=server.base_url, http_client=httpx2.Client())
try:
    workos.organizations.list_organizations()
except Exception:
    pass
assert server.ports("Bearer sk_parent"), "the parent sent no request"
runtime = workos.create_feature_flags_runtime_client()
pid = fork()
if pid == 0:
    workos._api_key = "sk_child"
    try:
        runtime.start()
        os._exit(2)
    except RuntimeError as error:
        assert "caller-supplied HTTP client" in str(error), error
    os._exit(0)
_, status = os.waitpid(pid, 0)
assert os.waitstatus_to_exitcode(status) == 0
assert server.ports("Bearer sk_child") == set(), "the child polled"
"""

ASYNC_CLIENT_SDK_USED = """
workos = AsyncWorkOSClient(api_key="sk_parent", base_url=server.base_url)


async def call_api():
    try:
        await workos.organizations.list_organizations()
    except Exception:
        pass


asyncio.run(call_api())
assert server.ports("Bearer sk_parent"), "the parent sent no request"
runtime = workos.create_feature_flags_runtime_client()
pid = fork()
if pid == 0:
    workos._api_key = "sk_child"
    try:
        asyncio.run(runtime.start())
        os._exit(2)
    except RuntimeError as error:
        assert "was used in the parent" in str(error), error
    os._exit(0)
_, status = os.waitpid(pid, 0)
assert os.waitstatus_to_exitcode(status) == 0
assert server.ports("Bearer sk_child") == set(), "the child polled"
"""

# Another WorkOS client sends the request, through an HTTP client it shares
# with the one the runtime client would poll through.
CALLER_CLIENT_SHARED_SDK_USED = """
import httpx2

shared = httpx2.Client()
other = WorkOSClient(api_key="sk_parent", base_url=server.base_url, http_client=shared)
try:
    other.organizations.list_organizations()
except Exception:
    pass
assert server.ports("Bearer sk_parent"), "the parent sent no request"
workos = WorkOSClient(api_key="sk_parent", base_url=server.base_url, http_client=shared)
runtime = workos.create_feature_flags_runtime_client()
pid = fork()
if pid == 0:
    workos._api_key = "sk_child"
    try:
        runtime.start()
        os._exit(2)
    except RuntimeError as error:
        assert "caller-supplied HTTP client" in str(error), error
    os._exit(0)
_, status = os.waitpid(pid, 0)
assert os.waitstatus_to_exitcode(status) == 0
assert server.ports("Bearer sk_child") == set(), "the child polled"
"""

ASYNC_CLIENT_SHARED_SDK_USED = """
import httpx2

shared = httpx2.AsyncClient()
other = AsyncWorkOSClient(api_key="sk_parent", base_url=server.base_url, http_client=shared)


async def call_api():
    try:
        await other.organizations.list_organizations()
    except Exception:
        pass


asyncio.run(call_api())
assert server.ports("Bearer sk_parent"), "the parent sent no request"
workos = AsyncWorkOSClient(api_key="sk_parent", base_url=server.base_url, http_client=shared)
runtime = workos.create_feature_flags_runtime_client()
pid = fork()
if pid == 0:
    workos._api_key = "sk_child"
    try:
        asyncio.run(runtime.start())
        os._exit(2)
    except RuntimeError as error:
        assert "was used in the parent" in str(error), error
    os._exit(0)
_, status = os.waitpid(pid, 0)
assert os.waitstatus_to_exitcode(status) == 0
assert server.ports("Bearer sk_child") == set(), "the child polled"
"""

# On macOS a forked child never polls, so to check what runs elsewhere, this
# pretends the platform is fork-safe. The scenarios reach the server by IP over
# plain HTTP, and NO_PROXY keeps httpx2 from reading macOS proxy settings, so
# the child opens connections without the system libraries that crash there.
FORCE_FORK_SAFE = """
from workos.feature_flags.runtime import _core

_core.FORK_SAFE_PLATFORM = True
"""


def run(*scenario: str) -> subprocess.CompletedProcess:
    script = "".join(textwrap.dedent(part) for part in (PRELUDE, *scenario))
    return subprocess.run(
        [sys.executable, "-c", script],
        cwd=ROOT,
        env={**os.environ, "NO_PROXY": "*"},
        capture_output=True,
        text=True,
        timeout=60,
    )


pytestmark = pytest.mark.skipif(not hasattr(os, "fork"), reason="requires os.fork")


def test_a_child_polls_on_its_own_connections_once_used() -> None:
    result = run(FORCE_FORK_SAFE, DEFAULT_CLIENT)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.skipif(sys.platform != "darwin", reason="macOS behavior")
def test_on_macos_a_child_does_not_poll() -> None:
    result = run(MACOS_DEFAULT_CLIENT)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "cannot safely open network connections" in result.stderr
    assert result.stderr.count(FORK_BLOCKED) == 1, result.stderr


@pytest.mark.skipif(sys.platform != "darwin", reason="macOS behavior")
def test_on_macos_a_preloaded_client_serves_its_bootstrap_in_a_child() -> None:
    result = run(MACOS_PRELOADED)
    assert result.returncode == 0, result.stdout + result.stderr
    # One warning from each start().
    assert result.stderr.count(FORK_BLOCKED) == 3, result.stderr


def test_a_child_does_not_poll_through_a_caller_supplied_client() -> None:
    result = run(FORCE_FORK_SAFE, CALLER_CLIENT)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "does not run in forked process" in result.stderr


def test_an_async_client_stops_polling_in_a_child() -> None:
    result = run(FORCE_FORK_SAFE, MAKE_ASYNC_RUNTIME, ASYNC_CLIENT)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    "scenario",
    [CALLER_CLIENT_UNUSED, ASYNC_CLIENT_UNUSED],
    ids=["sync-caller-supplied-client", "async"],
)
def test_a_client_that_never_polled_starts_in_a_child(scenario: str) -> None:
    result = run(FORCE_FORK_SAFE, scenario)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize(
    "scenario",
    [
        CALLER_CLIENT_SDK_USED,
        ASYNC_CLIENT_SDK_USED,
        CALLER_CLIENT_SHARED_SDK_USED,
        ASYNC_CLIENT_SHARED_SDK_USED,
    ],
    ids=[
        "sync-caller-supplied-client",
        "async",
        "sync-client-shared-with-another-workos-client",
        "async-client-shared-with-another-workos-client",
    ],
)
def test_a_child_does_not_poll_once_another_call_used_the_http_client(
    scenario: str,
) -> None:
    result = run(FORCE_FORK_SAFE, scenario)
    assert result.returncode == 0, result.stdout + result.stderr


def fork_warnings(caplog: pytest.LogCaptureFixture) -> List[str]:
    return [r.getMessage() for r in caplog.records if FORK_BLOCKED in r.getMessage()]


@pytest.mark.parametrize(
    "was_polling", [False, True], ids=["never-polled", "was-polling"]
)
def test_on_macos_start_warns_once_and_does_not_poll(
    was_polling: bool,
    server: FlagServer,
    make_runtime: Make,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setattr(_core, "FORK_SAFE_PLATFORM", False)
    runtime = make_runtime()
    if was_polling:
        runtime.start()
        runtime.wait_until_ready(timeout=5)
    sent = len(server.requests)

    # What the at-fork hook runs in a child, without forking pytest.
    runtime._reinitialize_after_fork()
    with caplog.at_level(logging.WARNING):
        if not was_polling:
            runtime.is_enabled("f")
            assert fork_warnings(caplog) == []
        runtime.start()
        runtime.start()
        runtime.is_enabled("f")

    [warning] = fork_warnings(caplog)
    assert "Create the WorkOSClient and the runtime client after forking" in warning
    assert "post_fork" in warning
    assert runtime._thread is None
    assert len(server.requests) == sent


def test_on_macos_a_child_serves_its_bootstrap_and_cannot_refresh(
    server: FlagServer, make_runtime: Make, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(_core, "FORK_SAFE_PLATFORM", False)
    bootstrapped = make_runtime(
        bootstrap=FeatureFlagsConfiguration.from_dict(BOOTSTRAP)
    )
    empty = make_runtime()
    for runtime in (bootstrapped, empty):
        runtime._reinitialize_after_fork()
        runtime.start()
        with pytest.raises(RuntimeError, match=FORK_BLOCKED):
            runtime.refresh()

    bootstrapped.wait_until_ready(timeout=5)
    assert bootstrapped.is_enabled("f") is True
    started = time.monotonic()
    with pytest.raises(RuntimeError, match=FORK_BLOCKED):
        empty.wait_until_ready(timeout=5)
    assert time.monotonic() - started < 1
    assert empty.is_enabled("f") is False
    assert server.requests == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "was_polling", [False, True], ids=["never-polled", "was-polling"]
)
async def test_on_macos_async_start_warns_once_and_does_not_poll(
    was_polling: bool,
    server: FlagServer,
    make_async_runtime: MakeAsync,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setattr(_core, "FORK_SAFE_PLATFORM", False)
    runtime = make_async_runtime()
    if was_polling:
        await runtime.start()
        await runtime.wait_until_ready(timeout=5)
    parent_task = runtime._task
    sent = len(server.requests)

    # What the at-fork hook runs in a child, without forking pytest.
    runtime._reinitialize_after_fork()
    with caplog.at_level(logging.WARNING):
        if not was_polling:
            runtime.is_enabled("f")
            assert fork_warnings(caplog) == []
        await runtime.start()
        await runtime.start()
        runtime.is_enabled("f")

    [warning] = fork_warnings(caplog)
    assert (
        "Create the AsyncWorkOSClient and the runtime client after forking" in warning
    )
    assert "post_fork" in warning
    assert runtime._task is None
    assert len(server.requests) == sent
    if parent_task is not None:
        # The parent's polling task, which a forked child would not run.
        parent_task.cancel()
        await asyncio.wait({parent_task})


@pytest.mark.asyncio
async def test_on_macos_an_async_child_serves_its_bootstrap_and_cannot_refresh(
    server: FlagServer, make_async_runtime: MakeAsync, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(_core, "FORK_SAFE_PLATFORM", False)
    bootstrapped = make_async_runtime(
        bootstrap=FeatureFlagsConfiguration.from_dict(BOOTSTRAP)
    )
    empty = make_async_runtime()
    for runtime in (bootstrapped, empty):
        runtime._reinitialize_after_fork()
        await runtime.start()
        with pytest.raises(RuntimeError, match=FORK_BLOCKED):
            await runtime.refresh()

    await bootstrapped.wait_until_ready()
    assert bootstrapped.is_enabled("f") is True
    with pytest.raises(RuntimeError, match=FORK_BLOCKED):
        await asyncio.wait_for(empty.wait_until_ready(), 1)
    assert empty.is_enabled("f") is False
    assert server.requests == []


def test_a_child_raises_from_start_and_wait_once_the_parent_used_the_http_client(
    make_runtime: Make, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(_core, "FORK_SAFE_PLATFORM", True)
    # Another runtime client polls through the caller-supplied HTTP client.
    make_runtime().refresh()
    runtime = make_runtime()

    # What the at-fork hook runs in a child, without forking pytest.
    runtime._reinitialize_after_fork()
    with pytest.raises(RuntimeError, match="caller-supplied HTTP client"):
        runtime.start()
    started = time.monotonic()
    with pytest.raises(RuntimeError, match="caller-supplied HTTP client"):
        runtime.wait_until_ready(timeout=5)
    assert time.monotonic() - started < 1


@pytest.mark.asyncio
async def test_an_async_child_raises_from_start_and_wait_once_the_parent_used_it(
    make_async_runtime: MakeAsync, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(_core, "FORK_SAFE_PLATFORM", True)
    await make_async_runtime().refresh()
    runtime = make_async_runtime()

    # What the at-fork hook runs in a child, without forking pytest.
    runtime._reinitialize_after_fork()
    with pytest.raises(RuntimeError, match="was used in the parent"):
        await runtime.start()
    with pytest.raises(RuntimeError, match="was used in the parent"):
        await asyncio.wait_for(runtime.wait_until_ready(), 1)


@pytest.mark.parametrize(
    "read", ["is_ready", "configuration", "is_closed", "status", "get_all_flags"]
)
def test_every_read_resumes_polling_after_a_fork(
    read: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(_core, "FORK_SAFE_PLATFORM", True)
    server = LocalHTTPServer(payload(f=flag("f", default_value=True)))
    workos = WorkOSClient(api_key="sk_test", base_url=server.base_url)
    runtime = workos.create_feature_flags_runtime_client()
    runtime.start()
    runtime.wait_until_ready(timeout=5)
    first_poller = runtime._thread

    # What the at-fork hook runs in a child, without forking pytest.
    runtime._reinitialize_after_fork()
    assert runtime._fork_restart_pending
    value = getattr(runtime, read)
    if callable(value):
        value()

    assert runtime._thread is not None and runtime._thread is not first_poller
    assert runtime._thread.is_alive()
    runtime.close()
    workos.close()
    server.close()


@dataclass
class UnhashableBackend:
    """An HTTPBackend that, like any dataclass with eq=True, can't be hashed."""

    requests: List[str] = field(default_factory=list)

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Dict[str, str],
        content: Optional[bytes],
        timeout: float,
    ) -> HTTPResponse:
        self.requests.append(url)
        return HTTPResponse(
            status_code=200,
            headers=httpx2.Headers(),
            content=b'{"version": 2, "flags": {}}',
            request_method=method,
            request_url=url,
        )

    def close(self) -> None:
        pass


def test_an_unhashable_custom_backend_survives_the_fork_hook(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(_core, "FORK_SAFE_PLATFORM", True)
    backend = UnhashableBackend()
    workos = WorkOSClient(api_key=API_KEY, http_client=backend)
    unused = workos.create_feature_flags_runtime_client()

    # What the at-fork hook runs in a child, without forking pytest.
    unused._reinitialize_after_fork()
    unused.refresh()
    assert backend.requests

    # Another WorkOSClient on the same backend sees that request too.
    sharing = WorkOSClient(api_key=API_KEY, http_client=backend)
    blocked = sharing.create_feature_flags_runtime_client()
    blocked._reinitialize_after_fork()
    with pytest.raises(RuntimeError, match="caller-supplied HTTP client"):
        blocked.start()
    unused.close()
    blocked.close()


@pytest.mark.parametrize("module", [_sync, _async], ids=["sync", "async"])
def test_one_client_failing_to_reinitialize_does_not_stop_the_others(
    module: Any, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    workos = WorkOSClient if module is _sync else AsyncWorkOSClient
    runtimes = [
        workos(api_key=API_KEY).create_feature_flags_runtime_client() for _ in range(2)
    ]
    attempts: List[int] = []

    def fail() -> None:
        attempts.append(1)
        raise RuntimeError("could not rebuild")

    for runtime in runtimes:
        monkeypatch.setattr(runtime, "_reinitialize_after_fork", fail)
    monkeypatch.setattr(module, "_clients", weakref.WeakSet(runtimes))

    with caplog.at_level(logging.ERROR):
        module._reinitialize_clients_after_fork()

    assert len(attempts) == 2
    assert len([r for r in caplog.records if r.levelno == logging.ERROR]) == 2
