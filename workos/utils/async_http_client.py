import asyncio
from typing_extensions import Self

import httpx

from workos.utils._base_http_client import BaseHTTPClient
from workos.utils.request import REQUEST_METHOD_GET


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
        timeout: int = None,
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
        )

    def is_closed(self) -> bool:
        return self._client.is_closed

    async def close(self) -> None:
        """Close the underlying HTTPX client.

        The client will *not* be usable after this.
        """
        await self._client.aclose()

    async def __aenter__(self) -> Self:
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
        method: str = REQUEST_METHOD_GET,
        params: dict = None,
        headers: dict = None,
        token: str = None,
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
        url, headers, params, request_fn = self._prepare_request(
            path=path, method=method, params=params, headers=headers, token=token
        )

        if method == REQUEST_METHOD_GET:
            response = await request_fn(
                url, headers=headers, params=params, timeout=self.timeout
            )
        else:
            response = await request_fn(
                url, headers=headers, json=params, timeout=self.timeout
            )

        return self._handle_response(response)
