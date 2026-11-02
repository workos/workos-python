# @oagen-ignore-file
"""Helpers for the feature flags runtime client tests."""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import httpx2

from workos import HTTPResponse

FIXTURES = Path(__file__).parent / "fixtures"
API_KEY = "sk_test_runtime"
BASE_URL = "https://api.workos.test"


def load_fixture(name: str) -> Dict[str, Any]:
    return json.loads((FIXTURES / name).read_text())


def payload(**flags: Dict[str, Any]) -> Dict[str, Any]:
    return {"version": 2, "flags": flags}


def flag(
    slug: str = "flag",
    *,
    enabled: bool = True,
    default_value: Any = False,
    off_value: Any = False,
    rules: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    return {
        "slug": slug,
        "enabled": enabled,
        "default_value": default_value,
        "off_value": off_value,
        "rules": rules or [],
    }


def rule(
    rule_id: str, value: Any, target_type: str, *ids: str, kind: str = "conditions"
) -> Dict[str, Any]:
    return {
        "id": rule_id,
        "kind": kind,
        "value": value,
        "conditions": [
            {"target_type": target_type, "operator": "one_of", "values": list(ids)}
        ],
    }


@dataclass
class RecordedRequest:
    method: str
    url: str
    headers: Dict[str, str]
    timeout: float


Reply = Union[tuple, Exception, Callable[[], Any]]


class FlagServer:
    """Scripted stand-in for the API behind an HTTPBackend.

    Replies queued with ``enqueue`` are used once, in order; otherwise every
    request gets the ``respond`` reply. A reply is ``(status, body)``, an
    exception to raise, or ``BLOCK`` to hold the request until ``release()``.
    """

    BLOCK = object()

    def __init__(self) -> None:
        self._condition = threading.Condition()
        self._queue: List[Any] = []
        self._default: Any = (200, payload())
        self._released = threading.Event()
        self.requests: List[RecordedRequest] = []
        self.in_flight = 0
        self.max_in_flight = 0

    def respond(self, status: int, body: Any = None) -> None:
        with self._condition:
            self._default = (status, body)

    def enqueue(self, *replies: Any) -> None:
        with self._condition:
            self._queue.extend(replies)

    def release(self) -> None:
        self._released.set()

    def wait_for_requests(self, count: int, timeout: float = 5.0) -> None:
        with self._condition:
            if not self._condition.wait_for(
                lambda: len(self.requests) >= count, timeout
            ):
                raise AssertionError(
                    f"expected {count} requests, saw {len(self.requests)}"
                )

    def _next(
        self, method: str, url: str, headers: Dict[str, str], timeout: float
    ) -> Any:
        with self._condition:
            self.requests.append(RecordedRequest(method, url, dict(headers), timeout))
            self.in_flight += 1
            self.max_in_flight = max(self.max_in_flight, self.in_flight)
            reply = self._queue.pop(0) if self._queue else self._default
            self._condition.notify_all()
        return reply

    def _finish(self) -> None:
        with self._condition:
            self.in_flight -= 1

    def _response(self, reply: Any, method: str, url: str) -> HTTPResponse:
        if isinstance(reply, Exception):
            raise reply
        status, body = reply
        content = (
            body
            if isinstance(body, bytes)
            else b""
            if body is None
            else json.dumps(body).encode()
        )
        return HTTPResponse(
            status_code=status,
            headers=httpx2.Headers({"x-request-id": f"req_{len(self.requests)}"}),
            content=content,
            request_method=method,
            request_url=url,
        )


class SyncBackend:
    def __init__(self, server: FlagServer) -> None:
        self.server = server

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Dict[str, str],
        content: Optional[bytes],
        timeout: float,
    ) -> HTTPResponse:
        reply = self.server._next(method, url, headers, timeout)
        try:
            if reply is FlagServer.BLOCK:
                self.server._released.wait(10)
                reply = (200, payload())
            return self.server._response(reply, method, url)
        finally:
            self.server._finish()

    def close(self) -> None:
        pass


class AsyncBackend:
    def __init__(self, server: FlagServer) -> None:
        self.server = server

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: Dict[str, str],
        content: Optional[bytes],
        timeout: float,
    ) -> HTTPResponse:
        import asyncio

        reply = self.server._next(method, url, headers, timeout)
        try:
            if reply is FlagServer.BLOCK:
                while not self.server._released.is_set():
                    await asyncio.sleep(0.005)
                reply = (200, payload())
            return self.server._response(reply, method, url)
        finally:
            self.server._finish()

    async def close(self) -> None:
        pass


class Collector:
    """Thread-safe list of listener calls with a blocking wait."""

    def __init__(self) -> None:
        self._condition = threading.Condition()
        self.items: List[Any] = []

    def __call__(self, item: Any) -> None:
        with self._condition:
            self.items.append(item)
            self._condition.notify_all()

    def wait_for(self, count: int, timeout: float = 5.0) -> List[Any]:
        with self._condition:
            if not self._condition.wait_for(lambda: len(self.items) >= count, timeout):
                raise AssertionError(
                    f"expected {count} calls, saw {len(self.items)}: {self.items}"
                )
            return list(self.items)


def eventually(predicate: Callable[[], bool], timeout: float = 5.0) -> None:
    deadline = time.monotonic() + timeout
    while not predicate():
        if time.monotonic() > deadline:
            raise AssertionError("condition was not met in time")
        time.sleep(0.002)
