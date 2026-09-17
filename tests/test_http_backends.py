# @oagen-ignore-file

"""HTTP backend protocol, the httpx/httpx2 adapter, resolution, and encoding parity."""

from __future__ import annotations

import json
import subprocess
import sys
from typing import Any, Dict, List, Optional, Union

import httpx
import httpx2
import pytest

from workos import (
    AsyncWorkOSClient,
    HTTPResponse,
    NotFoundError,
    TransportConnectError,
    TransportError,
    TransportTimeout,
    WorkOSClient,
    WorkOSError,
)
from workos import _base_client as base_client_module
from workos._base_client import _BaseWorkOSClient
from workos._errors import WorkOSConnectionError, WorkOSTimeoutError
from workos._http import AsyncHttpxBackend, HttpxBackend
from tests.generated_helpers import load_fixture

API_KEY = "sk_test_123"
BASE = "https://api.workos.com"


def make_response(
    status_code: int = 200,
    body: Any = None,
    headers: Optional[Dict[str, str]] = None,
    method: str = "GET",
    url: str = f"{BASE}/t",
) -> HTTPResponse:
    content = b"" if body is None else json.dumps(body).encode()
    return HTTPResponse(
        status_code=status_code,
        headers=httpx2.Headers(headers or {}),
        content=content,
        request_method=method,
        request_url=url,
    )


class FakeBackend:
    """Minimal HTTPBackend that replays queued responses or exceptions."""

    def __init__(self, *items: Union[HTTPResponse, Exception]) -> None:
        self.items: List[Union[HTTPResponse, Exception]] = list(items)
        self.calls: List[Dict[str, Any]] = []
        self.closed = False

    def _record(
        self,
        method: str,
        url: str,
        headers: Dict[str, str],
        content: Optional[bytes],
        timeout: float,
    ) -> HTTPResponse:
        self.calls.append(
            {
                "method": method,
                "url": url,
                "headers": headers,
                "content": content,
                "timeout": timeout,
            }
        )
        item = self.items.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Dict[str, str],
        content: Optional[bytes],
        timeout: float,
    ) -> HTTPResponse:
        return self._record(method, url, headers, content, timeout)

    def close(self) -> None:
        self.closed = True


class AsyncFakeBackend(FakeBackend):
    """Async twin of FakeBackend."""

    async def request(  # type: ignore[override]
        self,
        method: str,
        url: str,
        *,
        headers: Dict[str, str],
        content: Optional[bytes],
        timeout: float,
    ) -> HTTPResponse:
        return self._record(method, url, headers, content, timeout)

    async def close(self) -> None:  # type: ignore[override]
        self.closed = True


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(base_client_module.time, "sleep", lambda _: None)


class TestProtocolBackend:
    def test_receives_full_url_headers_body_and_timeout(self) -> None:
        backend = FakeBackend(make_response(200, {"ok": True}))
        client = WorkOSClient(api_key=API_KEY, http_client=backend)

        result = client.request(
            "POST",
            ("orgs", "org 1"),
            params={"limit": 10, "enabled": True, "tags": ["a", "b"]},
            body={"name": "Acme"},
            request_options={"timeout": 7},
        )

        assert result == {"ok": True}
        call = backend.calls[0]
        assert call["method"] == "POST"
        assert call["url"] == f"{BASE}/orgs/org%201?limit=10&enabled=true&tags=a&tags=b"
        assert call["content"] == b'{"name":"Acme"}'
        assert call["headers"]["Content-Type"] == "application/json"
        assert call["headers"]["Authorization"] == f"Bearer {API_KEY}"
        assert call["timeout"] == 7.0

    def test_no_params_and_no_body(self) -> None:
        backend = FakeBackend(make_response(204))
        client = WorkOSClient(api_key=API_KEY, http_client=backend)

        assert client.request("GET", ("t",)) is None
        assert backend.calls[0]["url"] == f"{BASE}/t"
        assert backend.calls[0]["content"] is None

    def test_retries_retryable_status_then_succeeds(self) -> None:
        backend = FakeBackend(
            make_response(429, {"message": "slow"}, {"Retry-After": "0"}),
            make_response(200, {"ok": True}),
        )
        client = WorkOSClient(api_key=API_KEY, http_client=backend)

        assert client.request("GET", ("t",)) == {"ok": True}
        assert len(backend.calls) == 2

    def test_client_error_is_raised_not_retried(self) -> None:
        backend = FakeBackend(
            make_response(404, {"message": "missing"}, {"X-Request-Id": "req_1"})
        )
        client = WorkOSClient(api_key=API_KEY, http_client=backend, max_retries=3)

        with pytest.raises(NotFoundError) as exc_info:
            client.request("GET", ("t",))

        assert exc_info.value.request_id == "req_1"
        assert exc_info.value.request_url == f"{BASE}/t"
        assert exc_info.value.request_method == "GET"
        assert len(backend.calls) == 1

    @pytest.mark.parametrize(
        ("transport_error", "sdk_error", "message"),
        [
            (TransportTimeout("slow"), WorkOSTimeoutError, "Request timed out: slow"),
            (
                TransportConnectError("refused"),
                WorkOSConnectionError,
                "Connection failed: refused",
            ),
            (TransportError("broken"), WorkOSError, "Network error: broken"),
        ],
    )
    def test_transport_errors_are_mapped(
        self, transport_error: Exception, sdk_error: type, message: str
    ) -> None:
        backend = FakeBackend(transport_error)
        client = WorkOSClient(api_key=API_KEY, http_client=backend, max_retries=0)

        with pytest.raises(sdk_error) as exc_info:
            client.request("GET", ("t",))

        assert str(exc_info.value) == message
        assert exc_info.value.__cause__ is transport_error

    def test_transport_errors_are_retried(self) -> None:
        backend = FakeBackend(TransportTimeout("slow"), make_response(200, {"ok": 1}))
        client = WorkOSClient(api_key=API_KEY, http_client=backend, max_retries=1)

        assert client.request("GET", ("t",)) == {"ok": 1}
        assert len(backend.calls) == 2

    def test_injected_backend_is_not_closed(self) -> None:
        backend = FakeBackend()
        client = WorkOSClient(api_key=API_KEY, http_client=backend)

        client.close()

        assert backend.closed is False

    def test_default_client_is_closed(self) -> None:
        client = WorkOSClient(api_key=API_KEY)
        backend = client._backend
        assert isinstance(backend, HttpxBackend)

        client.close()

        assert backend._client.is_closed


@pytest.mark.asyncio
class TestAsyncProtocolBackend:
    async def test_retries_and_deserializes(self) -> None:
        backend = AsyncFakeBackend(
            make_response(503, {"message": "down"}, {"Retry-After": "0"}),
            make_response(200, {"ok": True}),
        )
        client = AsyncWorkOSClient(api_key=API_KEY, http_client=backend)

        assert await client.request("GET", ("t",)) == {"ok": True}
        assert len(backend.calls) == 2
        assert backend.calls[0]["url"] == f"{BASE}/t"

    async def test_transport_timeout_is_mapped(self) -> None:
        backend = AsyncFakeBackend(TransportTimeout("slow"))
        client = AsyncWorkOSClient(api_key=API_KEY, http_client=backend, max_retries=0)

        with pytest.raises(WorkOSTimeoutError, match="Request timed out: slow"):
            await client.request("GET", ("t",))

    async def test_client_error_is_raised_not_retried(self) -> None:
        backend = AsyncFakeBackend(make_response(404, {"message": "missing"}))
        client = AsyncWorkOSClient(api_key=API_KEY, http_client=backend)

        with pytest.raises(NotFoundError):
            await client.request("GET", ("t",))

        assert len(backend.calls) == 1

    async def test_injected_backend_is_not_closed(self) -> None:
        backend = AsyncFakeBackend()
        client = AsyncWorkOSClient(api_key=API_KEY, http_client=backend)

        await client.close()

        assert backend.closed is False

    async def test_default_client_is_closed(self) -> None:
        client = AsyncWorkOSClient(api_key=API_KEY)
        backend = client._backend
        assert isinstance(backend, AsyncHttpxBackend)

        await client.close()

        assert backend._client.is_closed


MODULES = [pytest.param(httpx2, id="httpx2"), pytest.param(httpx, id="httpx")]


@pytest.mark.parametrize("mod", MODULES)
class TestHttpxAdapter:
    def test_wraps_response(self, mod: Any) -> None:
        seen: Dict[str, Any] = {}

        def handler(request: Any) -> Any:
            seen["timeout"] = request.extensions.get("timeout")
            seen["content"] = request.content
            return mod.Response(200, json={"a": 1}, headers={"X-Request-Id": "req_1"})

        backend = HttpxBackend(mod.Client(transport=mod.MockTransport(handler)))
        response = backend.request(
            "POST", "https://x/p?q=1", headers={"H": "v"}, content=b"{}", timeout=5.0
        )

        assert isinstance(response, HTTPResponse)
        assert response.status_code == 200
        assert response.json() == {"a": 1}
        assert response.headers.get("x-request-id") == "req_1"
        assert response.request_method == "POST"
        assert response.request_url == "https://x/p?q=1"
        assert seen["content"] == b"{}"
        assert seen["timeout"] == {
            "connect": 5.0,
            "read": 5.0,
            "write": 5.0,
            "pool": 5.0,
        }

    @pytest.mark.parametrize(
        ("raised", "expected"),
        [
            ("TimeoutException", TransportTimeout),
            ("ConnectError", TransportConnectError),
            ("RemoteProtocolError", TransportError),
        ],
    )
    def test_maps_exceptions(self, mod: Any, raised: str, expected: type) -> None:
        exc_cls = getattr(mod, raised)

        def handler(request: Any) -> Any:
            raise exc_cls("boom")

        backend = HttpxBackend(mod.Client(transport=mod.MockTransport(handler)))

        with pytest.raises(expected) as exc_info:
            backend.request("GET", "https://x/p", headers={}, content=None, timeout=1.0)

        assert isinstance(exc_info.value.__cause__, exc_cls)

    def test_end_to_end_through_client(self, mod: Any) -> None:
        def handler(request: Any) -> Any:
            return mod.Response(404, json={"message": "nope"})

        http_client = mod.Client(transport=mod.MockTransport(handler))
        client = WorkOSClient(api_key=API_KEY, http_client=http_client)

        with pytest.raises(NotFoundError):
            client.request("GET", ("t",))
        client.close()

        assert not http_client.is_closed
        http_client.close()

    @pytest.mark.asyncio
    async def test_async_end_to_end_through_client(self, mod: Any) -> None:
        def handler(request: Any) -> Any:
            return mod.Response(200, json={"ok": True})

        http_client = mod.AsyncClient(transport=mod.MockTransport(handler))
        client = AsyncWorkOSClient(api_key=API_KEY, http_client=http_client)

        assert await client.request("GET", ("t",)) == {"ok": True}
        await client.close()

        assert not http_client.is_closed
        await http_client.aclose()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
    async def test_client_query_defaults_preserve_filters_and_pagination(
        self, mod: Any, asynchronous: bool
    ) -> None:
        requests: List[Any] = []
        first_page = load_fixture("list_user.json")
        first_page["list_metadata"]["after"] = "cursor/after"

        def handler(request: Any) -> Any:
            requests.append(request)
            body = (
                first_page if len(requests) == 1 else {"data": [], "list_metadata": {}}
            )
            return mod.Response(200, json=body)

        defaults = {"limit": 100, "order": "asc", "organization_id": "org_default"}
        http_cls = mod.AsyncClient if asynchronous else mod.Client
        http_client = http_cls(params=defaults, transport=mod.MockTransport(handler))
        try:
            if asynchronous:
                client = AsyncWorkOSClient(api_key=API_KEY, http_client=http_client)
                page = await client.user_management.list_users(
                    email="alice@example.com", limit=7
                )
                users = [user async for user in page]
            else:
                sync_client = WorkOSClient(api_key=API_KEY, http_client=http_client)
                sync_page = sync_client.user_management.list_users(
                    email="alice@example.com", limit=7
                )
                users = list(sync_page)
        finally:
            if asynchronous:
                await http_client.aclose()
            else:
                http_client.close()

        expected = {
            "limit": "7",
            "order": "desc",
            "organization_id": "org_default",
            "email": "alice@example.com",
        }
        assert len(users) == 1
        assert len(requests) == 2
        assert dict(requests[0].url.params) == expected
        assert dict(requests[1].url.params) == {**expected, "after": "cursor/after"}
        assert http_client.params == mod.QueryParams(defaults)

    @pytest.mark.asyncio
    async def test_async_adapter_maps_timeout(self, mod: Any) -> None:
        def handler(request: Any) -> Any:
            raise mod.TimeoutException("slow")

        backend = AsyncHttpxBackend(
            mod.AsyncClient(transport=mod.MockTransport(handler))
        )

        with pytest.raises(TransportTimeout):
            await backend.request(
                "GET", "https://x/p", headers={}, content=None, timeout=1.0
            )


class TestResolution:
    @pytest.mark.parametrize(
        "httpx_installed", [False, True], ids=["without-httpx", "with-httpx"]
    )
    def test_public_client_annotations_resolve_at_runtime(
        self, httpx_installed: bool
    ) -> None:
        script = """
import sys
from typing import get_args, get_type_hints

if sys.argv[1] == "False":
    sys.modules["httpx"] = None

import httpx2
from workos import (
    AsyncHTTPBackend, AsyncWorkOSClient, HTTPBackend, WorkOSClient, create_public_client,
)

for factory, client_type, protocol in (
    (WorkOSClient.__init__, httpx2.Client, HTTPBackend),
    (AsyncWorkOSClient.__init__, httpx2.AsyncClient, AsyncHTTPBackend),
    (create_public_client, httpx2.Client, HTTPBackend),
):
    client_types = get_args(get_type_hints(factory)["http_client"])
    assert client_type in client_types
    assert protocol in client_types
    assert type(None) in client_types
    if sys.argv[1] == "True":
        import httpx
        assert getattr(httpx, client_type.__name__) in client_types

assert get_type_hints(create_public_client)["return"] is WorkOSClient
"""
        result = subprocess.run(
            [sys.executable, "-c", script, str(httpx_installed)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr

    def test_default_backend_settings(self) -> None:
        client = WorkOSClient(api_key=API_KEY, request_timeout=9)
        backend = client._backend
        assert isinstance(backend, HttpxBackend)
        assert isinstance(backend._client, httpx2.Client)
        assert backend._client.follow_redirects is True
        assert backend._client.timeout == httpx2.Timeout(9)
        client.close()

    def test_httpx_client_subclass_is_detected(self) -> None:
        class MyClient(httpx2.Client):
            pass

        http_client = MyClient()
        client = WorkOSClient(api_key=API_KEY, http_client=http_client)
        assert isinstance(client._backend, HttpxBackend)
        http_client.close()

    def test_sync_client_rejects_async_httpx_client(self) -> None:
        with pytest.raises(TypeError, match="use AsyncWorkOSClient"):
            WorkOSClient(api_key=API_KEY, http_client=httpx2.AsyncClient())  # type: ignore[arg-type]

    def test_async_client_rejects_sync_httpx_client(self) -> None:
        with pytest.raises(TypeError, match="use WorkOSClient"):
            AsyncWorkOSClient(api_key=API_KEY, http_client=httpx2.Client())  # type: ignore[arg-type]

    def test_sync_client_rejects_async_backend(self) -> None:
        with pytest.raises(TypeError, match="coroutine"):
            WorkOSClient(api_key=API_KEY, http_client=AsyncFakeBackend())  # type: ignore[arg-type]

    def test_async_client_rejects_sync_backend(self) -> None:
        with pytest.raises(TypeError, match="coroutine"):
            AsyncWorkOSClient(api_key=API_KEY, http_client=FakeBackend())  # type: ignore[arg-type]

    def test_rejects_unrelated_object(self) -> None:
        with pytest.raises(TypeError, match="HTTPBackend"):
            WorkOSClient(api_key=API_KEY, http_client=object())  # type: ignore[arg-type]


class TestEncodingParity:
    @pytest.mark.parametrize(
        "params",
        [
            {"limit": 10},
            {"enabled": True, "archived": False},
            {"after": None},
            {"domains": ["a.com", "b.com"]},
            {"order": ("asc", "desc")},
            {"search": "héllo wörld & co=1"},
            {"empty": ""},
            {"ratio": 1.5},
            {},
            None,
        ],
    )
    def test_query_matches_httpx(self, params: Optional[Dict[str, Any]]) -> None:
        encoded = _BaseWorkOSClient._encode_query(params)
        ours = httpx2.URL(f"{BASE}/p?{encoded}" if encoded else f"{BASE}/p")
        theirs = httpx2.Request("GET", f"{BASE}/p", params=params).url

        assert ours.params == theirs.params
        assert str(ours) == str(theirs)
        with httpx2.Client(
            transport=httpx2.MockTransport(lambda _: httpx2.Response(200))
        ) as client:
            response = HttpxBackend(client).request(
                "GET", str(ours), headers={}, content=None, timeout=1.0
            )
        assert response.request_url == str(theirs)

    def test_query_string_shape(self) -> None:
        params = {"a": True, "b": None, "c": ["x", "y"], "d": 5}
        assert _BaseWorkOSClient._encode_query(params) == "a=true&b=&c=x&c=y&d=5"

    def test_body_matches_httpx(self) -> None:
        body = {"a": 1, "b": [1, 2], "s": "é", "nested": {"k": None}}
        assert (
            _BaseWorkOSClient._encode_body(body)
            == httpx2.Request("POST", BASE, json=body).content
        )
        assert _BaseWorkOSClient._encode_body(None) is None
        assert _BaseWorkOSClient._encode_body({}) == b"{}"

    def test_recorded_request_exposes_decoded_params(
        self, workos: WorkOSClient, httpx_mock: Any
    ) -> None:
        httpx_mock.add_response(json={})

        workos.request(
            "GET", ("t",), params={"enabled": True, "limit": 5, "ids": ["a", "b"]}
        )

        request = httpx_mock.get_request()
        assert request.url.params["enabled"] == "true"
        assert request.url.params["limit"] == "5"
        assert request.url.params.get_list("ids") == ["a", "b"]
