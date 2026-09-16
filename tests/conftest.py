# @oagen-ignore-file

from __future__ import annotations

from typing import Any, Dict, Iterator, List, Optional, Union

import httpx2
import pytest
import pytest_asyncio

from workos import WorkOSClient, AsyncWorkOSClient


@pytest.fixture
def workos():
    """Create a WorkOS client for testing with guaranteed cleanup."""
    client = WorkOSClient(
        api_key="sk_test_Sz3IQjepeSWaI4cMS4ms4sMuU", client_id="client_test"
    )
    yield client
    client.close()


@pytest_asyncio.fixture
async def async_workos():
    """Create an AsyncWorkOS client for testing with guaranteed cleanup."""
    client = AsyncWorkOSClient(
        api_key="sk_test_Sz3IQjepeSWaI4cMS4ms4sMuU", client_id="client_test"
    )
    try:
        yield client
    finally:
        await client.close()


class HTTPXMock:
    """Stand-in for the ``pytest-httpx`` fixture of the same name.

    ``pytest-httpx`` pins ``httpx==0.28.*`` and cannot intercept ``httpx2``. The
    oagen-generated test files depend on this fixture's name and on the subset of
    its API implemented here, so the shim is hand-maintained instead of changing
    the emitter. Requests are intercepted the same way ``pytest-httpx`` does, by
    patching the transport classes, so clients constructed directly in a test are
    covered too. Responses are consumed first-in first-out. Like ``pytest-httpx``,
    the fixture fails the test at teardown if any queued response was never
    requested; call ``reset()`` to discard the queue deliberately.
    """

    def __init__(self) -> None:
        self._queue: List[Union[httpx2.Response, Exception]] = []
        self._requests: List[httpx2.Request] = []

    def add_response(
        self,
        *,
        json: Any = None,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
        content: Optional[bytes] = None,
    ) -> None:
        self._queue.append(
            httpx2.Response(status_code, json=json, headers=headers, content=content)
        )

    def add_exception(self, exception: Exception) -> None:
        self._queue.append(exception)

    def get_requests(self) -> List[httpx2.Request]:
        return list(self._requests)

    def get_request(self) -> Optional[httpx2.Request]:
        if len(self._requests) > 1:
            raise AssertionError(
                f"{len(self._requests)} requests were sent; use get_requests()"
            )
        return self._requests[0] if self._requests else None

    def reset(self) -> None:
        self._queue.clear()
        self._requests.clear()

    def unused_responses(self) -> int:
        return len(self._queue)

    def _next(self, request: httpx2.Request) -> httpx2.Response:
        self._requests.append(request)
        if not self._queue:
            raise httpx2.TimeoutException(
                "No response registered for this request", request=request
            )
        item = self._queue.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    def handle_request(self, request: httpx2.Request) -> httpx2.Response:
        request.read()
        return self._next(request)

    async def handle_async_request(self, request: httpx2.Request) -> httpx2.Response:
        await request.aread()
        return self._next(request)


@pytest.fixture
def httpx_mock(monkeypatch: pytest.MonkeyPatch) -> Iterator[HTTPXMock]:
    mock = HTTPXMock()

    def _sync(
        _transport: httpx2.HTTPTransport, request: httpx2.Request
    ) -> httpx2.Response:
        return mock.handle_request(request)

    async def _async(
        _transport: httpx2.AsyncHTTPTransport, request: httpx2.Request
    ) -> httpx2.Response:
        return await mock.handle_async_request(request)

    monkeypatch.setattr(httpx2.HTTPTransport, "handle_request", _sync)
    monkeypatch.setattr(httpx2.AsyncHTTPTransport, "handle_async_request", _async)
    yield mock
    unused = mock.unused_responses()
    if unused:
        pytest.fail(
            f"{unused} httpx_mock response(s) were registered but never requested"
        )
