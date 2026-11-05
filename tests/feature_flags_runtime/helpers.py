# @oagen-ignore-file
"""Helpers for the feature flags runtime client tests."""

from __future__ import annotations

import json
import socket
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
        status, body, *extra = reply
        headers = {
            "x-request-id": f"req_{len(self.requests)}",
            **(extra[0] if extra else {}),
        }
        content = (
            body
            if isinstance(body, bytes)
            else b""
            if body is None
            else json.dumps(body).encode()
        )
        return HTTPResponse(
            status_code=status,
            headers=httpx2.Headers(headers),
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


class LocalHTTPServer:
    """A real HTTP/1.1 server on 127.0.0.1 for transport-level tests.

    ``mode`` selects the next responses: ``"ok"`` serves ``payload``,
    ``"stall"`` waits ``stall`` seconds before answering, and ``"drip"`` sends
    the body one byte every ``drip_interval`` seconds. Every request is
    recorded with its headers and the client's TCP port.
    """

    def __init__(self, payload: Dict[str, Any]) -> None:
        import http.server

        self.payload = payload
        self.mode = "ok"
        self.stall = 0.0
        self.drip_interval = 0.1
        self.requests: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        owner = self

        class Handler(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, format: str, *args: Any) -> None:
                pass

            def do_GET(self) -> None:
                owner._handle(self)

        self._server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self._server.daemon_threads = True
        # Without a poll interval the server thread sleeps until a connection
        # arrives, so it can't be waiting for the GIL when a test forks without
        # Python's fork hooks.
        self._thread = threading.Thread(
            target=self._server.serve_forever, args=(None,), daemon=True
        )
        self._thread.start()

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self._server.server_address[1]}"

    def ports(self, authorization: str) -> set:
        with self._lock:
            return {
                request["port"]
                for request in self.requests
                if request["headers"].get("Authorization") == authorization
            }

    def close(self) -> None:
        # The server thread only sees the shutdown once a connection wakes it.
        stopper = threading.Thread(target=self._server.shutdown)
        stopper.start()
        while stopper.is_alive():
            try:
                address = ("127.0.0.1", self._server.server_address[1])
                socket.create_connection(address, timeout=1).close()
            except OSError:
                pass
            stopper.join(0.05)
        self._server.server_close()

    def _handle(self, handler: Any) -> None:
        with self._lock:
            self.requests.append(
                {
                    "path": handler.path,
                    "headers": dict(handler.headers.items()),
                    "port": handler.client_address[1],
                }
            )
            mode, stall, interval = self.mode, self.stall, self.drip_interval
        if mode == "stall":
            time.sleep(stall)
        body = json.dumps(self.payload).encode()
        handler.send_response(200)
        handler.send_header("Content-Type", "application/json")
        handler.send_header("Content-Length", str(len(body)))
        handler.end_headers()
        try:
            if mode == "drip":
                for byte in body:
                    handler.wfile.write(bytes([byte]))
                    handler.wfile.flush()
                    time.sleep(interval)
            else:
                handler.wfile.write(body)
        except OSError:
            pass
