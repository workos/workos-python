# @oagen-ignore-file
"""The sync client's poll request over a real HTTP connection."""

from __future__ import annotations

import copy
import time
from types import SimpleNamespace
from typing import Callable, Dict, Iterator, List, Optional

import httpx2
import pytest

from workos import WorkOSClient
from workos._errors import WorkOSTimeoutError
from workos.feature_flags.runtime import _transport

from tests.feature_flags_runtime.helpers import (
    API_KEY,
    LocalHTTPServer,
    flag,
    payload,
)

PAYLOAD = payload(checkout=flag("checkout", default_value=True))


@pytest.fixture
def local() -> Iterator[LocalHTTPServer]:
    server = LocalHTTPServer(PAYLOAD)
    yield server
    server.close()


def test_sends_the_sdk_url_and_headers(local: LocalHTTPServer) -> None:
    workos = WorkOSClient(api_key=API_KEY, base_url=local.base_url)
    runtime = workos.create_feature_flags_runtime_client()
    runtime.refresh()

    request = local.requests[0]
    assert request["path"] == "/sdk/feature-flags?payload_version=2"
    assert request["headers"]["Authorization"] == f"Bearer {API_KEY}"
    assert request["headers"]["User-Agent"].startswith("WorkOS Python/")
    assert runtime.is_enabled("checkout") is True

    runtime.close()
    workos.close()


def test_uses_a_caller_supplied_httpx_client(local: LocalHTTPServer) -> None:
    http_client = httpx2.Client(headers={"X-Caller-Client": "yes"})
    workos = WorkOSClient(
        api_key=API_KEY, base_url=local.base_url, http_client=http_client
    )
    runtime = workos.create_feature_flags_runtime_client()
    runtime.refresh()

    assert local.requests[0]["headers"]["X-Caller-Client"] == "yes"
    runtime.close()
    assert not http_client.is_closed
    http_client.close()


@pytest.mark.parametrize(
    "mode, setting",
    [
        # Headers arrive late: each phase only gets the time left.
        ("stall", 3.0),
        # Every read succeeds well within its own timeout, but the body as a
        # whole would take several seconds.
        ("drip", 0.1),
    ],
)
def test_a_refresh_is_bounded_by_its_request_timeout(
    local: LocalHTTPServer, mode: str, setting: float
) -> None:
    local.mode = mode
    local.stall = setting
    local.drip_interval = setting
    workos = WorkOSClient(api_key=API_KEY, base_url=local.base_url, max_retries=0)
    runtime = workos.create_feature_flags_runtime_client(request_timeout=0.5)

    started = time.monotonic()
    with pytest.raises(WorkOSTimeoutError):
        runtime.refresh()
    elapsed = time.monotonic() - started

    # The documented bound is request_timeout plus at most one read.
    assert elapsed < 1.2
    runtime.close()
    workos.close()


Timeouts = Dict[str, Optional[float]]


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    """The poll transport's monotonic clock, moved by setting ``now``."""
    clock = SimpleNamespace(now=100.0)
    monkeypatch.setattr(
        _transport, "time", SimpleNamespace(monotonic=lambda: clock.now)
    )
    return clock


def stored(timeouts: Timeouts) -> List[Optional[float]]:
    # dict.get reads the stored values, bypassing any override.
    return [dict.get(timeouts, phase) for phase in _transport._PHASES]


COPIES: Dict[str, Callable[[Timeouts], List[Optional[float]]]] = {
    "dict(t)": lambda t: stored(dict(t)),
    "{**t}": lambda t: stored({**t}),
    "t.copy()": lambda t: stored(t.copy()),
    "copy.copy(t)": lambda t: stored(copy.copy(t)),
    "dict(t.items())": lambda t: stored(dict(t.items())),
    "list(t.values())": lambda t: list(t.values()),
}


@pytest.mark.parametrize("copy_phases", COPIES.values(), ids=list(COPIES))
def test_a_copy_of_the_timeouts_gets_the_time_left(
    clock: SimpleNamespace, copy_phases: Callable[[Timeouts], List[Optional[float]]]
) -> None:
    # A custom transport, or a later httpcore, may copy the timeouts instead of
    # reading each phase as it starts.
    timeouts = _transport._DeadlineTimeouts(deadline=110.0)

    assert copy_phases(timeouts) == [10.0] * 4
    clock.now = 106.0
    assert copy_phases(timeouts) == [4.0] * 4
    clock.now = 120.0
    assert copy_phases(timeouts) == [_transport._MINIMUM_WAIT] * 4


def test_the_stored_timeouts_are_the_budget_left_when_built(
    clock: SimpleNamespace,
) -> None:
    timeouts = _transport._DeadlineTimeouts(deadline=110.0)
    clock.now = 106.0

    assert stored(timeouts) == [10.0] * 4
