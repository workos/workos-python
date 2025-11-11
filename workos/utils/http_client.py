import asyncio
import time
from types import TracebackType
from typing import Optional, Type, Union

# Self was added to typing in Python 3.11
from typing_extensions import Self

import httpx

from workos.utils._base_http_client import (
    BaseHTTPClient,
    HeadersType,
    JsonType,
    ParamsType,
    ResponseJson,
    RetryConfig,
)
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
        api_key: str,
        base_url: str,
        client_id: str,
        version: str,
        timeout: Optional[int] = None,
        retry_config: Optional[RetryConfig] = None,
        # If no custom transport is provided, let httpx use the default
        # so we don't overwrite environment configurations like proxies
        transport: Optional[httpx.BaseTransport] = None,
    ) -> None:
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            client_id=client_id,
            version=version,
            timeout=timeout,
            retry_config=retry_config,
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

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.close()

    def request(
        self,
        path: str,
        method: Optional[str] = REQUEST_METHOD_GET,
        params: ParamsType = None,
        json: JsonType = None,
        headers: HeadersType = None,
        exclude_default_auth_headers: bool = False,
        retry_config: Optional[RetryConfig] = None,
    ) -> ResponseJson:
        """Executes a request against the WorkOS API.

        Args:
            path (str): Path for the api request that'd be appended to the base API URL

        Kwargs:
            method (str): One of the supported methods as defined by the REQUEST_METHOD_X constants
            params (ParamsType): Query params to be added to the request
            json (JsonType): Body payload to be added to the request
            retry_config (RetryConfig): Optional retry configuration. If None, no retries.

        Returns:
            ResponseJson: Response from WorkOS
        """
        prepared_request_parameters = self._prepare_request(
            path=path,
            method=method,
            params=params,
            json=json,
            headers=headers,
            exclude_default_auth_headers=exclude_default_auth_headers,
        )

        # If no retry config provided, just make the request without retry logic
        if retry_config is None:
            response = self._client.request(**prepared_request_parameters)
            return self._handle_response(response)

        # Retry logic enabled
        last_exception = None

        for attempt in range(retry_config.max_retries + 1):
            try:
                response = self._client.request(**prepared_request_parameters)

                # Check if we should retry based on status code
                if attempt < retry_config.max_retries and self._is_retryable_error(
                    response
                ):
                    delay = self._get_backoff_delay(attempt, retry_config)
                    time.sleep(delay)
                    continue

                # No retry needed or max retries reached
                return self._handle_response(response)

            except Exception as exc:
                last_exception = exc
                if attempt < retry_config.max_retries and self._is_retryable_exception(exc):
                    delay = self._get_backoff_delay(attempt, retry_config)
                    time.sleep(delay)
                    continue
                raise

        if last_exception is not None:
            raise last_exception

        raise RuntimeError("Unexpected state in retry logic")


class AsyncHttpxClientWrapper(httpx.AsyncClient):
    def __del__(self) -> None:
        try:
            asyncio.get_running_loop().create_task(self.aclose())
        except Exception:
            pass


class AsyncHTTPClient(BaseHTTPClient[httpx.AsyncClient]):
    """Async HTTP Client for a convenient way to access the WorkOS feature set."""

    _client: httpx.AsyncClient

    _api_key: str
    _client_id: str

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        client_id: str,
        version: str,
        timeout: Optional[int] = None,
        retry_config: Optional[RetryConfig] = None,
        # If no custom transport is provided, let httpx use the default
        # so we don't overwrite environment configurations like proxies
        transport: Optional[httpx.AsyncBaseTransport] = None,
    ) -> None:
        super().__init__(
            base_url=base_url,
            api_key=api_key,
            client_id=client_id,
            version=version,
            timeout=timeout,
            retry_config=retry_config,
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

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.close()

    async def request(
        self,
        path: str,
        method: Optional[str] = REQUEST_METHOD_GET,
        params: ParamsType = None,
        json: JsonType = None,
        headers: HeadersType = None,
        exclude_default_auth_headers: bool = False,
        retry_config: Optional[RetryConfig] = None,
    ) -> ResponseJson:
        """Executes a request against the WorkOS API.

        Args:
            path (str): Path for the api request that'd be appended to the base API URL

        Kwargs:
            method (str): One of the supported methods as defined by the REQUEST_METHOD_X constants
            params (ParamsType): Query params to be added to the request
            json (JsonType): Body payload to be added to the request
            retry_config (RetryConfig): Optional retry configuration. If None, no retries.

        Returns:
            ResponseJson: Response from WorkOS
        """
        prepared_request_parameters = self._prepare_request(
            path=path,
            method=method,
            params=params,
            json=json,
            headers=headers,
            exclude_default_auth_headers=exclude_default_auth_headers,
        )

        # If no retry config provided, just make the request without retry logic
        if retry_config is None:
            response = await self._client.request(**prepared_request_parameters)
            return self._handle_response(response)

        # Retry logic enabled
        last_exception = None

        for attempt in range(retry_config.max_retries + 1):
            try:
                response = await self._client.request(**prepared_request_parameters)

                # Check if we should retry based on status code
                if attempt < retry_config.max_retries and self._is_retryable_error(
                    response
                ):
                    delay = self._get_backoff_delay(attempt, retry_config)
                    await asyncio.sleep(delay)
                    continue

                # No retry needed or max retries reached
                return self._handle_response(response)

            except Exception as exc:
                last_exception = exc
                if attempt < retry_config.max_retries and self._is_retryable_exception(exc):
                    delay = self._get_backoff_delay(attempt, retry_config)
                    await asyncio.sleep(delay)
                    continue
                raise

        # Should not reach here, but raise last exception if we do
        if last_exception is not None:
            raise last_exception

        # Fallback: this should never happen
        raise RuntimeError("Unexpected state in retry logic")


HTTPClient = Union[AsyncHTTPClient, SyncHTTPClient]
