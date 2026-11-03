# @oagen-ignore-file
"""The sync client's poll request over a real HTTP connection."""

from __future__ import annotations

import time
from typing import Iterator

import httpx2
import pytest

from workos import WorkOSClient
from workos._errors import WorkOSTimeoutError

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


def test_sends_the_sdk_url_and_headers_and_closes_its_client(
    local: LocalHTTPServer,
) -> None:
    workos = WorkOSClient(api_key=API_KEY, base_url=local.base_url)
    runtime = workos.create_feature_flags_runtime_client()
    runtime.refresh()

    request = local.requests[0]
    assert request["path"] == "/sdk/feature-flags?payload_version=2"
    assert request["headers"]["Authorization"] == f"Bearer {API_KEY}"
    assert request["headers"]["User-Agent"].startswith("WorkOS Python/")
    assert runtime.is_enabled("checkout") is True

    runtime.close()
    assert runtime._transport._owned is None
    workos.close()


def test_a_poll_after_close_opens_no_client(local: LocalHTTPServer) -> None:
    workos = WorkOSClient(api_key=API_KEY, base_url=local.base_url)
    runtime = workos.create_feature_flags_runtime_client()
    runtime.close()

    # As a poll does when close() stopped waiting for it.
    with pytest.raises(RuntimeError, match="closed"):
        runtime._transport.get(time.monotonic() + 5)
    assert runtime._transport._owned is None
    assert local.requests == []
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
