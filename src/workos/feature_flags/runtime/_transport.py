# @oagen-ignore-file
# This file is hand-maintained. The sync runtime client's poll request, sent
# with a total time budget.
# pyright: strict, reportPrivateUsage=false

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any, Dict, Iterator, Optional
from urllib.parse import urlsplit

from ..._errors import WorkOSConnectionError, WorkOSError, WorkOSTimeoutError
from ..._http import (
    HTTPResponse,
    HttpxBackend,
    TransportConnectError,
    TransportError,
    TransportTimeout,
    _HttpxFamily,
)
from . import _policy

if TYPE_CHECKING:
    from _collections_abc import dict_items, dict_values

    from ..._base_client import WorkOSClient

_PHASES = ("connect", "read", "write", "pool")
_MINIMUM_WAIT = 0.001


class _DeadlineTimeouts(Dict[str, Optional[float]]):
    """httpx timeouts that shrink to the time left before a deadline.

    httpcore reads each phase's timeout when the phase starts, so connecting,
    sending and waiting for the response each get only what is left of the
    budget instead of the whole budget every time. Those reads are the
    ``timeouts.get(<phase>, None)`` calls in httpcore's ``connection_pool``
    (pool), ``connection``, ``http_proxy`` and ``socks_proxy`` (connect), and
    ``http11`` and ``http2`` (read and write).

    A consumer that copies the dict still gets a bounded wait: a copy holds the
    time left when it is made.
    """

    def __init__(self, deadline: float) -> None:
        self._deadline = deadline
        # Anything that reads the stored values directly gets the whole budget.
        super().__init__(dict.fromkeys(_PHASES, self.remaining()))

    def remaining(self) -> float:
        return max(self._deadline - time.monotonic(), _MINIMUM_WAIT)

    def get(self, key: str, default: Optional[float] = None) -> Optional[float]:  # type: ignore[override]
        return self.remaining() if key in _PHASES else super().get(key, default)

    def __getitem__(self, key: str) -> Optional[float]:
        return self.remaining() if key in _PHASES else super().__getitem__(key)

    # With __iter__ overridden, dict(), {**...} and dict.update() copy through
    # keys() and __getitem__ instead of reading the stored values, and
    # copy.copy() rebuilds the dict from items().
    def __iter__(self) -> Iterator[str]:
        return super().__iter__()

    def items(self) -> dict_items[str, Optional[float]]:
        return {key: self[key] for key in self}.items()

    def values(self) -> dict_values[str, Optional[float]]:
        return {key: self[key] for key in self}.values()

    def copy(self) -> _DeadlineTimeouts:
        return _DeadlineTimeouts(self._deadline)


class PollTransport:
    """Sends ``GET /sdk/feature-flags`` for the sync runtime client.

    The request carries the same URL, headers and User-Agent as any other
    request from the ``WorkOSClient``, goes through its HTTP client, and maps
    responses and failures to the same errors. Unlike other requests, a refresh
    has a total budget. The body is streamed, every network wait is limited to
    the time left, and the response is abandoned once the deadline passes, so a
    refresh ends within ``request_timeout`` plus at most one read of a stalling
    response body. A caller-supplied ``HTTPBackend`` that is not an httpx client
    cannot stream; it gets the remaining budget as its per-request timeout.
    """

    def __init__(self, workos: WorkOSClient) -> None:
        self._workos = workos
        backend = workos._backend
        self._shared_httpx: Any = None
        self._family = _HttpxFamily("httpx2")
        if isinstance(backend, HttpxBackend):
            self._shared_httpx = backend._client
            self._family = backend._family

    def get(self, deadline: float) -> Any:
        """Send one poll request and return the decoded body."""
        workos = self._workos
        url = workos._build_request_url(_policy.POLL_PATH, _policy.POLL_PARAMS, None)
        headers = workos._build_headers("get", None, None)
        try:
            response = self._send(url, headers, deadline)
        except TransportTimeout as error:
            raise WorkOSTimeoutError(f"Request timed out: {error}") from error
        except TransportConnectError as error:
            raise WorkOSConnectionError(f"Connection failed: {error}") from error
        except TransportError as error:
            raise WorkOSError(f"Network error: {error}") from error
        if response.status_code >= 400:
            workos._raise_error(response)
        return workos._deserialize_response(response, None)

    def _send(self, url: str, headers: Dict[str, str], deadline: float) -> HTTPResponse:
        if deadline - time.monotonic() <= 0:
            raise TransportTimeout("no time was left in the request timeout")
        client = self._shared_httpx
        if client is None:
            return self._workos._backend.request(
                "GET",
                url,
                headers=headers,
                content=None,
                timeout=max(deadline - time.monotonic(), _MINIMUM_WAIT),
            )
        try:
            return self._stream(client, url, headers, deadline)
        except self._family.timeout_error as error:
            raise TransportTimeout(str(error)) from error
        except self._family.connect_error as error:
            raise TransportConnectError(str(error)) from error
        except self._family.http_error as error:
            raise TransportError(str(error)) from error

    def _stream(
        self, client: Any, url: str, headers: Dict[str, str], deadline: float
    ) -> HTTPResponse:
        request = client.build_request(
            "GET",
            url,
            # Explicit params merge client defaults, as HttpxBackend does.
            params=urlsplit(url).query or None,
            headers=headers,
            extensions={"timeout": _DeadlineTimeouts(deadline)},
        )
        response = client.send(request, stream=True)
        try:
            chunks: list[bytes] = []
            for chunk in response.iter_bytes():
                chunks.append(chunk)
                if time.monotonic() > deadline:
                    raise TransportTimeout(
                        "the response body did not finish within the request timeout"
                    )
            content = b"".join(chunks)
        finally:
            response.close()
        return HTTPResponse(
            status_code=response.status_code,
            headers=response.headers,
            content=content,
            request_method="GET",
            request_url=str(response.request.url),
        )
