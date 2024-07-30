import asyncio
from typing import Mapping, Optional

import httpx

from workos.utils._base_http_client import BaseHTTPClient
from workos.utils.request_helper import REQUEST_METHOD_GET


class SyncHttpxClientWrapper(httpx.Client):
    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass


class SyncHTTPClient(BaseHTTPClient[httpx.Client]):
    """Sync HTTP Client for a convenient way to access the WorkOS feature set."""

    _client: httpx.Client

    def __init__(
        self,
        *,
        base_url: str,
        version: str,
        timeout: Optional[int] = None,
        transport: Optional[httpx.BaseTransport] = httpx.HTTPTransport(),
    ) -> None:
        super().__init__(
            base_url=base_url,
            version=version,
            timeout=timeout,
        )
        self._client = SyncHttpxClientWrapper(
            base_url=base_url,
            timeout=timeout,
            follow_redirects=True,
            transport=transport,
        )

    def is_closed(self) -> bool:
        return self._client.is_closed

    def close(self) -> None:
        """Close the underlying HTTPX client.

        The client will *not* be usable after this.
        """
        # If an error is thrown while constructing a client, self._client
        # may not be present
        if hasattr(self, "_client"):
            self._client.close()

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc,
        exc_tb,
    ) -> None:
        self.close()

    def request(
        self,
        path: str,
        method: Optional[str] = REQUEST_METHOD_GET,
        params: Optional[Mapping] = None,
        headers: Optional[dict] = None,
        token: Optional[str] = None,
    ) -> dict:
        """Executes a request against the WorkOS API.

        Args:
            path (str): Path for the api request that'd be appended to the base API URL

        Kwargs:
            method (str): One of the supported methods as defined by the REQUEST_METHOD_X constants
            params (dict): Query params or body payload to be added to the request
            token (str): Bearer token

        Returns:
            dict: Response from WorkOS
        """
        prepared_request_params = self._prepare_request(
            path=path, method=method, params=params, headers=headers, token=token
        )
        response = self._client.request(**prepared_request_params)
        return self._handle_response(response)


class AsyncHttpxClientWrapper(httpx.AsyncClient):
    def __del__(self) -> None:
        try:
            asyncio.get_running_loop().create_task(self.aclose())
        except Exception:
            pass


class AsyncHTTPClient(BaseHTTPClient[httpx.AsyncClient]):
    """Async HTTP Client for a convenient way to access the WorkOS feature set."""

    _client: httpx.AsyncClient

    def __init__(
        self,
        *,
        base_url: str,
        version: str,
        timeout: Optional[int] = None,
        transport: Optional[httpx.AsyncBaseTransport] = httpx.AsyncHTTPTransport(),
    ) -> None:
        super().__init__(
            base_url=base_url,
            version=version,
            timeout=timeout,
        )
        self._client = AsyncHttpxClientWrapper(
            base_url=base_url,
            timeout=timeout,
            follow_redirects=True,
            transport=transport,
        )

    def is_closed(self) -> bool:
        return self._client.is_closed

    async def close(self) -> None:
        """Close the underlying HTTPX client.

        The client will *not* be usable after this.
        """
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type,
        exc,
        exc_tb,
    ) -> None:
        await self.close()

    async def request(
        self,
        path: str,
        method: Optional[str] = REQUEST_METHOD_GET,
        params: Optional[Mapping] = None,
        headers: Optional[dict] = None,
        token: Optional[str] = None,
    ) -> dict:
        """Executes a request against the WorkOS API.

        Args:
            path (str): Path for the api request that'd be appended to the base API URL

        Kwargs:
            method (str): One of the supported methods as defined by the REQUEST_METHOD_X constants
            params (dict): Query params or body payload to be added to the request
            token (str): Bearer token

        Returns:
            dict: Response from WorkOS
        """
        prepared_request_parameters = self._prepare_request(
            path=path, method=method, params=params, headers=headers, token=token
        )
        response = await self._client.request(**prepared_request_parameters)
        return self._handle_response(response)
