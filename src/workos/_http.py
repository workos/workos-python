# @oagen-ignore-file
"""HTTP transport layer for the WorkOS client.

``_base_client`` owns URL building, query and body encoding, retries and error
mapping. Everything that touches a concrete HTTP library lives here, behind the
:class:`HTTPBackend` / :class:`AsyncHTTPBackend` protocols, so a caller can
supply any HTTP client they like via ``http_client=``.
"""

from __future__ import annotations

import importlib
import inspect
import json
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Mapping,
    Optional,
    Protocol,
    Tuple,
    Union,
    cast,
)

import httpx2

if TYPE_CHECKING:
    import httpx


class TransportError(Exception):
    """Network-level failure reported by an HTTP backend.

    Backends raise this family instead of their library's own exceptions so the
    retry loop in ``_base_client`` never depends on a particular HTTP client.
    """


class TransportTimeout(TransportError):
    """The request timed out."""


class TransportConnectError(TransportError):
    """A connection could not be established."""


@dataclass(frozen=True)
class HTTPResponse:
    """Backend-neutral view of an HTTP response.

    ``headers`` must be a case-insensitive mapping (``httpx2.Headers`` and
    ``multidict.CIMultiDictProxy`` both qualify): the SDK reads ``Retry-After``
    and ``x-request-id`` without normalising case.
    """

    status_code: int
    headers: Mapping[str, str]
    content: bytes
    request_method: str
    request_url: str

    @property
    def text(self) -> str:
        """Body decoded as UTF-8, replacing undecodable bytes."""
        return self.content.decode("utf-8", errors="replace")

    def json(self) -> Any:
        """Body parsed as JSON."""
        return json.loads(self.content)


class HTTPBackend(Protocol):
    """Synchronous transport used by :class:`workos.WorkOSClient`.

    The SDK passes a fully built URL (path and query already encoded), the final
    headers, an optional JSON body as bytes, and a timeout in seconds. Raise
    :class:`TransportTimeout`, :class:`TransportConnectError` or
    :class:`TransportError` for network failures so the SDK can retry them.
    """

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Dict[str, str],
        content: Optional[bytes],
        timeout: float,
    ) -> HTTPResponse: ...

    def close(self) -> None: ...


class AsyncHTTPBackend(Protocol):
    """Asynchronous transport used by :class:`workos.AsyncWorkOSClient`.

    Same contract as :class:`HTTPBackend` with coroutine methods.
    """

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: Dict[str, str],
        content: Optional[bytes],
        timeout: float,
    ) -> HTTPResponse: ...

    async def close(self) -> None: ...


if TYPE_CHECKING:
    SyncHTTPClient = Union[httpx2.Client, httpx.Client, HTTPBackend]
    AsyncHTTPClient = Union[httpx2.AsyncClient, httpx.AsyncClient, AsyncHTTPBackend]


# --- httpx family -------------------------------------------------------------

_HTTPX_MODULES = frozenset({"httpx2", "httpx"})


def _httpx_root(obj: object) -> Optional[str]:
    """Return ``"httpx2"`` or ``"httpx"`` if ``obj`` is (a subclass of) a client from that module."""
    for cls in type(obj).__mro__:
        root = cls.__module__.partition(".")[0]
        if root in _HTTPX_MODULES:
            return root
    return None


class _HttpxFamily:
    """Classes from whichever httpx-compatible module a client was built with.

    ``httpx2`` is a fork of ``httpx`` 0.28 with an identical API, so one adapter
    serves both. Only the exception and client classes differ by module.
    """

    def __init__(self, module_name: str) -> None:
        module = importlib.import_module(module_name)
        self.name = module_name
        self.client: type[Any] = module.Client
        self.async_client: type[Any] = module.AsyncClient
        self.timeout_error: type[Exception] = module.TimeoutException
        self.connect_error: type[Exception] = module.ConnectError
        self.http_error: type[Exception] = module.HTTPError


def _wrap_response(response: Union[httpx2.Response, httpx.Response]) -> HTTPResponse:
    request = response.request
    return HTTPResponse(
        status_code=response.status_code,
        headers=response.headers,
        content=response.content,
        request_method=request.method,
        request_url=str(request.url),
    )


class HttpxBackend:
    """Adapter for ``httpx2.Client`` and the API-identical ``httpx.Client``."""

    def __init__(self, client: Union[httpx2.Client, httpx.Client]) -> None:
        self._client = client
        self._family = _HttpxFamily(_httpx_root(client) or "httpx2")

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Dict[str, str],
        content: Optional[bytes],
        timeout: float,
    ) -> HTTPResponse:
        try:
            response = self._client.request(
                method, url, headers=headers, content=content, timeout=timeout
            )
        except self._family.timeout_error as exc:
            raise TransportTimeout(str(exc)) from exc
        except self._family.connect_error as exc:
            raise TransportConnectError(str(exc)) from exc
        except self._family.http_error as exc:
            raise TransportError(str(exc)) from exc
        return _wrap_response(response)

    def close(self) -> None:
        self._client.close()


class AsyncHttpxBackend:
    """Adapter for ``httpx2.AsyncClient`` and the API-identical ``httpx.AsyncClient``."""

    def __init__(self, client: Union[httpx2.AsyncClient, httpx.AsyncClient]) -> None:
        self._client = client
        self._family = _HttpxFamily(_httpx_root(client) or "httpx2")

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: Dict[str, str],
        content: Optional[bytes],
        timeout: float,
    ) -> HTTPResponse:
        try:
            response = await self._client.request(
                method, url, headers=headers, content=content, timeout=timeout
            )
        except self._family.timeout_error as exc:
            raise TransportTimeout(str(exc)) from exc
        except self._family.connect_error as exc:
            raise TransportConnectError(str(exc)) from exc
        except self._family.http_error as exc:
            raise TransportError(str(exc)) from exc
        return _wrap_response(response)

    async def close(self) -> None:
        await self._client.aclose()


# --- resolution -----------------------------------------------------------------


def _describe(obj: object) -> str:
    return f"{type(obj).__module__}.{type(obj).__qualname__}"


def _is_backend_like(obj: object) -> bool:
    return callable(getattr(obj, "request", None)) and callable(
        getattr(obj, "close", None)
    )


def _has_async_request(obj: object) -> bool:
    return inspect.iscoroutinefunction(getattr(obj, "request", None))


_UNSUPPORTED = (
    "Unsupported http_client {desc}: pass an httpx2 client, an httpx client, or an "
    "object implementing workos.{protocol} (request() and close())."
)


def resolve_sync_backend(
    http_client: Optional[SyncHTTPClient], timeout: float
) -> Tuple[HTTPBackend, bool]:
    """Return ``(backend, owned)`` for :class:`workos.WorkOSClient`.

    ``owned`` is True only for the default client the SDK creates itself. The
    SDK never closes a client the caller passed in.
    """
    if http_client is None:
        client = httpx2.Client(timeout=timeout, follow_redirects=True)
        return HttpxBackend(client), True
    root = _httpx_root(http_client)
    if root is not None:
        family = _HttpxFamily(root)
        if isinstance(http_client, family.client):
            return HttpxBackend(cast(httpx2.Client, http_client)), False
        if isinstance(http_client, family.async_client):
            raise TypeError(
                f"WorkOSClient needs a synchronous HTTP client but got "
                f"{root}.AsyncClient; pass {root}.Client, or use AsyncWorkOSClient."
            )
    if _is_backend_like(http_client):
        if _has_async_request(http_client):
            raise TypeError(
                "WorkOSClient needs an HTTPBackend with a synchronous request(); "
                f"{_describe(http_client)}.request is a coroutine function. "
                "Use AsyncWorkOSClient."
            )
        return cast(HTTPBackend, http_client), False
    raise TypeError(
        _UNSUPPORTED.format(desc=_describe(http_client), protocol="HTTPBackend")
    )


def resolve_async_backend(
    http_client: Optional[AsyncHTTPClient], timeout: float
) -> Tuple[AsyncHTTPBackend, bool]:
    """Return ``(backend, owned)`` for :class:`workos.AsyncWorkOSClient`.

    ``owned`` is True only for the default client the SDK creates itself. The
    SDK never closes a client the caller passed in.
    """
    if http_client is None:
        client = httpx2.AsyncClient(timeout=timeout, follow_redirects=True)
        return AsyncHttpxBackend(client), True
    root = _httpx_root(http_client)
    if root is not None:
        family = _HttpxFamily(root)
        if isinstance(http_client, family.async_client):
            return AsyncHttpxBackend(cast(httpx2.AsyncClient, http_client)), False
        if isinstance(http_client, family.client):
            raise TypeError(
                f"AsyncWorkOSClient needs an asynchronous HTTP client but got "
                f"{root}.Client; pass {root}.AsyncClient, or use WorkOSClient."
            )
    if _is_backend_like(http_client):
        if not _has_async_request(http_client):
            raise TypeError(
                "AsyncWorkOSClient needs an AsyncHTTPBackend whose request() is a "
                f"coroutine function; {_describe(http_client)}.request is not. "
                "Use WorkOSClient."
            )
        return cast(AsyncHTTPBackend, http_client), False
    raise TypeError(
        _UNSUPPORTED.format(desc=_describe(http_client), protocol="AsyncHTTPBackend")
    )
