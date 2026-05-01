# @oagen-ignore-file
from __future__ import annotations

import asyncio
import os
import platform
import time
import uuid
import random
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Dict, Optional, Type, cast, overload

import httpx

from ._errors import (
    APIError,
    WorkOSError,
    ConfigurationError,
    RateLimitExceededError,
    ServerError,
    WorkOSConnectionError,
    WorkOSTimeoutError,
    STATUS_CODE_TO_ERROR,
    _AUTH_CODE_TO_ERROR,
)
from ._pagination import AsyncPage, ListMetadata, SyncPage
from ._types import D, Deserializable, RequestOptions

try:
    from importlib.metadata import version as _pkg_version

    VERSION = _pkg_version("workos")
except Exception:
    VERSION = "0.0.0"

RETRY_STATUS_CODES = {429, 500, 502, 503, 504}
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1
MAX_RETRY_DELAY = 30
RETRY_MULTIPLIER = 2


class _BaseWorkOSClient:
    """Shared WorkOS client implementation."""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        client_id: Optional[str] = None,
        base_url: Optional[str] = None,
        request_timeout: Optional[int] = None,
        jwt_leeway: float = 0.0,
        max_retries: int = MAX_RETRIES,
    ) -> None:
        self._api_key = api_key or os.environ.get("WORKOS_API_KEY")
        self.client_id = client_id or os.environ.get("WORKOS_CLIENT_ID")
        if not self._api_key and not self.client_id:
            raise ValueError(
                "WorkOS requires either an API key or a client ID. "
                "Provide api_key / WORKOS_API_KEY for authenticated server-side usage, "
                "or client_id / WORKOS_CLIENT_ID for flows that require a client ID."
            )
        resolved_base_url = base_url or os.environ.get(
            "WORKOS_BASE_URL", "https://api.workos.com"
        )
        # Ensure base_url has a trailing slash for backward compatibility
        self._base_url = resolved_base_url.rstrip("/") + "/"
        self._request_timeout = (
            request_timeout
            if request_timeout is not None
            else int(os.environ.get("WORKOS_REQUEST_TIMEOUT", "60"))
        )
        self._max_retries = max_retries
        self._jwt_leeway = jwt_leeway

    @property
    def base_url(self) -> str:
        """The base URL for API requests."""
        return self._base_url

    def build_url(self, path: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Build a full URL with query parameters for redirect/authorization endpoints."""
        from urllib.parse import urlencode

        base = self._base_url.rstrip("/")
        url = f"{base}/{path}"
        if params:
            url = f"{url}?{urlencode(params)}"
        return url

    @staticmethod
    def _parse_retry_after(retry_after: Optional[str]) -> Optional[float]:
        """Parse Retry-After as seconds or an HTTP-date."""
        if not retry_after:
            return None
        value = retry_after.strip()
        if not value:
            return None
        try:
            return max(float(value), 0.0)
        except ValueError:
            pass
        try:
            retry_at = parsedate_to_datetime(value)
        except (TypeError, ValueError, IndexError, OverflowError):
            return None
        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=timezone.utc)
        return max((retry_at - datetime.now(timezone.utc)).total_seconds(), 0.0)

    @staticmethod
    def _calculate_retry_delay(
        attempt: int, retry_after: Optional[str] = None
    ) -> float:
        """Calculate retry delay with exponential backoff and jitter."""
        parsed_retry_after = _BaseWorkOSClient._parse_retry_after(retry_after)
        if parsed_retry_after is not None:
            return parsed_retry_after
        delay = min(INITIAL_RETRY_DELAY * (RETRY_MULTIPLIER**attempt), MAX_RETRY_DELAY)
        return delay * (0.5 + random.random())

    def _resolve_base_url(self, request_options: Optional[RequestOptions]) -> str:
        if request_options:
            base_url = request_options.get("base_url")
            if base_url:
                return str(base_url).rstrip("/")
        return self._base_url.rstrip("/")

    def _resolve_timeout(self, request_options: Optional[RequestOptions]) -> float:
        timeout = self._request_timeout
        if request_options:
            t = request_options.get("timeout")
            if isinstance(t, (int, float)):
                timeout = float(t)
        return timeout

    def _resolve_max_retries(self, request_options: Optional[RequestOptions]) -> int:
        if request_options:
            retries = request_options.get("max_retries")
            if isinstance(retries, int):
                return retries
        return self._max_retries

    def _require_api_key(self) -> str:
        if not self._api_key:
            raise ConfigurationError(
                "This operation requires a WorkOS API key. Provide api_key when instantiating the client "
                "or via the WORKOS_API_KEY environment variable."
            )
        return self._api_key

    def _require_client_id(self) -> str:
        if not self.client_id:
            raise ConfigurationError(
                "This operation requires a WorkOS client ID. Provide client_id when instantiating the client "
                "or via the WORKOS_CLIENT_ID environment variable."
            )
        return self.client_id

    def _build_headers(
        self,
        method: str,
        idempotency_key: Optional[str],
        request_options: Optional[RequestOptions],
    ) -> Dict[str, str]:
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "User-Agent": f"WorkOS Python/{platform.python_version()} Python SDK/{VERSION}",
        }
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        effective_idempotency_key = idempotency_key
        if effective_idempotency_key is None and request_options:
            request_option_idempotency_key = request_options.get("idempotency_key")
            if isinstance(request_option_idempotency_key, str):
                effective_idempotency_key = request_option_idempotency_key
        if effective_idempotency_key is None and method.lower() == "post":
            effective_idempotency_key = str(uuid.uuid4())
        if effective_idempotency_key:
            headers["Idempotency-Key"] = effective_idempotency_key
        if request_options:
            extra = request_options.get("extra_headers")
            if isinstance(extra, dict):
                headers.update(cast(Dict[str, str], extra))
        return headers

    def _deserialize_response(
        self, response: httpx.Response, model: Optional[Type[Deserializable]]
    ) -> Any:
        if response.status_code == 204 or not response.content:
            return None
        try:
            data = response.json()
        except Exception:
            return None
        if model is not None:
            return model.from_dict(cast(Dict[str, Any], data))
        return data

    @staticmethod
    def _raise_error(response: httpx.Response) -> None:
        """Raise an appropriate error based on the response status code."""
        request_id = response.headers.get("x-request-id", "")
        raw_body = response.text
        request = response.request
        request_url = str(request.url) if request is not None else None
        request_method = request.method if request is not None else None
        response_json: Optional[Dict[str, Any]] = None
        try:
            response_json = cast(Dict[str, Any], response.json())
            message: str = str(response_json.get("message", response.text))
            error = cast(Optional[str], response_json.get("error"))
            errors = response_json.get("errors")
            code: Optional[str] = (
                str(response_json["code"]) if "code" in response_json else None
            )
            error_description = cast(
                Optional[str], response_json.get("error_description")
            )
            param = cast(Optional[str], response_json.get("param"))
        except Exception:
            message = response.text
            error = None
            errors = None
            code = None
            error_description = None
            param = None

        error_class = STATUS_CODE_TO_ERROR.get(response.status_code)
        if error_class:
            if error_class is RateLimitExceededError:
                retry_after = _BaseWorkOSClient._parse_retry_after(
                    response.headers.get("Retry-After")
                )
                raise RateLimitExceededError(
                    message,
                    retry_after=retry_after,
                    request_id=request_id,
                    code=code,
                    param=param,
                    response=response,
                    response_json=response_json,
                    error=error,
                    errors=errors,
                    error_description=error_description,
                    raw_body=raw_body,
                    request_url=request_url,
                    request_method=request_method,
                )
            # Auth-flow dispatch for 403 responses: check code/error field
            # for specific auth-flow errors before falling through to generic class.
            if response.status_code == 403 and response_json is not None:
                auth_code = code or error
                if auth_code is not None:
                    auth_error_class = _AUTH_CODE_TO_ERROR.get(auth_code)
                    if auth_error_class is not None:
                        raise auth_error_class(
                            message,
                            request_id=request_id,
                            code=code,
                            param=param,
                            response=response,
                            response_json=response_json,
                            error=error,
                            errors=errors,
                            error_description=error_description,
                            raw_body=raw_body,
                            request_url=request_url,
                            request_method=request_method,
                        )

            raise error_class(
                message,
                request_id=request_id,
                code=code,
                param=param,
                response=response,
                response_json=response_json,
                error=error,
                errors=errors,
                error_description=error_description,
                raw_body=raw_body,
                request_url=request_url,
                request_method=request_method,
            )

        if response.status_code >= 500:
            raise ServerError(
                message,
                status_code=response.status_code,
                request_id=request_id,
                code=code,
                param=param,
                response=response,
                response_json=response_json,
                error=error,
                errors=errors,
                error_description=error_description,
                raw_body=raw_body,
                request_url=request_url,
                request_method=request_method,
            )

        raise APIError(
            message,
            status_code=response.status_code,
            request_id=request_id,
            code=code,
            param=param,
            response=response,
            response_json=response_json,
            error=error,
            errors=errors,
            error_description=error_description,
            raw_body=raw_body,
            request_url=request_url,
            request_method=request_method,
        )


class WorkOSClient(_BaseWorkOSClient):
    """Synchronous WorkOS API client."""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        client_id: Optional[str] = None,
        base_url: Optional[str] = None,
        request_timeout: Optional[int] = None,
        jwt_leeway: float = 0.0,
        max_retries: int = MAX_RETRIES,
    ) -> None:
        """Initialize the WorkOS client.

        Args:
            api_key: WorkOS API key. Falls back to the WORKOS_API_KEY environment variable.
            client_id: WorkOS client ID. Falls back to the WORKOS_CLIENT_ID environment variable.
            base_url: Base URL for API requests. Falls back to WORKOS_BASE_URL or "https://api.workos.com".
            request_timeout: HTTP request timeout in seconds. Falls back to WORKOS_REQUEST_TIMEOUT or 60.
            jwt_leeway: JWT clock skew leeway in seconds.
            max_retries: Maximum number of retries for failed requests. Defaults to 3.

        Raises:
            ValueError: If neither api_key nor client_id is provided, directly or via environment variables.
        """
        super().__init__(
            api_key=api_key,
            client_id=client_id,
            base_url=base_url,
            request_timeout=request_timeout,
            jwt_leeway=jwt_leeway,
            max_retries=max_retries,
        )
        self._client = httpx.Client(
            timeout=self._request_timeout, follow_redirects=True
        )

    def close(self) -> None:
        """Close the underlying HTTP client and release resources."""
        self._client.close()

    def __enter__(self) -> "WorkOSClient":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    @overload
    def request(
        self,
        method: str,
        path: str,
        *,
        model: Type[D],
        params: Optional[Dict[str, Any]] = ...,
        body: Optional[Dict[str, Any]] = ...,
        idempotency_key: Optional[str] = ...,
        request_options: Optional[RequestOptions] = ...,
    ) -> D: ...

    @overload
    def request(
        self,
        method: str,
        path: str,
        *,
        model: None = ...,
        params: Optional[Dict[str, Any]] = ...,
        body: Optional[Dict[str, Any]] = ...,
        idempotency_key: Optional[str] = ...,
        request_options: Optional[RequestOptions] = ...,
    ) -> Optional[Dict[str, Any]]: ...

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        model: Optional[Type[Deserializable]] = None,
        idempotency_key: Optional[str] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> Any:
        """Make an HTTP request with retry logic."""
        url = f"{self._resolve_base_url(request_options)}/{path}"
        headers = self._build_headers(method, idempotency_key, request_options)
        timeout = self._resolve_timeout(request_options)
        max_retries = self._resolve_max_retries(request_options)
        last_error: Optional[Exception] = None
        for attempt in range(max_retries + 1):
            try:
                response = self._client.request(
                    method=method.upper(),
                    url=url,
                    params=params,
                    json=body if body is not None else None,
                    headers=headers,
                    timeout=timeout,
                )
                if response.status_code in RETRY_STATUS_CODES and attempt < max_retries:
                    delay = self._calculate_retry_delay(
                        attempt, response.headers.get("Retry-After")
                    )
                    time.sleep(delay)
                    continue
                if response.status_code >= 400:
                    self._raise_error(response)
                return self._deserialize_response(response, model)
            except httpx.TimeoutException as e:
                last_error = e
                if attempt < max_retries:
                    time.sleep(self._calculate_retry_delay(attempt))
                    continue
                raise WorkOSTimeoutError(f"Request timed out: {e}") from e
            except httpx.ConnectError as e:
                last_error = e
                if attempt < max_retries:
                    time.sleep(self._calculate_retry_delay(attempt))
                    continue
                raise WorkOSConnectionError(f"Connection failed: {e}") from e
            except httpx.HTTPError as e:
                last_error = e
                if attempt < max_retries:
                    time.sleep(self._calculate_retry_delay(attempt))
                    continue
                raise WorkOSError(f"Network error: {e}") from e
        raise WorkOSError("Max retries exceeded") from last_error

    def request_raw(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request without model deserialization.

        Returns the raw JSON dict. Use this when you need the raw
        response without mapping through a model class.
        """
        result = self.request(
            method=method,
            path=path,
            params=params,
            body=body,
            idempotency_key=idempotency_key,
            request_options=request_options,
        )
        return result if isinstance(result, dict) else {}

    def request_list(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> list[Dict[str, Any]]:
        """Make an HTTP request expecting a bare JSON array response.

        Returns the raw list of dicts. Use this for endpoints that return
        a JSON array instead of a paginated envelope.
        """
        result = self.request(
            method=method,
            path=path,
            params=params,
            body=body,
            idempotency_key=idempotency_key,
            request_options=request_options,
        )
        if not isinstance(result, list):
            raise WorkOSError(
                f"Expected array response from {method.upper()} /{path}, got {type(result).__name__}"
            )
        return result

    def request_page(
        self,
        method: str,
        path: str,
        *,
        model: Type[D],
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> SyncPage[D]:
        """Make an HTTP request that returns a paginated response."""
        raw = self.request(
            method=method,
            path=path,
            params=params,
            body=body,
            request_options=request_options,
        )
        data: Dict[str, Any] = raw if isinstance(raw, dict) else {}
        raw_items: list[Any] = cast(list[Any], data.get("data") or [])
        items: list[D] = [
            cast(D, model.from_dict(cast(Dict[str, Any], item))) for item in raw_items
        ]
        list_metadata = ListMetadata.from_dict(
            cast(Dict[str, Any], data.get("list_metadata", {}))
        )

        def _fetch(*, after: Optional[str] = None) -> SyncPage[D]:
            next_params = {**(params or {}), "after": after}
            return self.request_page(
                method=method,
                path=path,
                model=model,
                params=next_params,
                body=body,
                request_options=request_options,
            )

        return SyncPage(data=items, list_metadata=list_metadata, _fetch_page=_fetch)


class AsyncWorkOSClient(_BaseWorkOSClient):
    """Asynchronous WorkOS API client."""

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        client_id: Optional[str] = None,
        base_url: Optional[str] = None,
        request_timeout: Optional[int] = None,
        jwt_leeway: float = 0.0,
        max_retries: int = MAX_RETRIES,
    ) -> None:
        """Initialize the async WorkOS client.

        Args:
            api_key: WorkOS API key. Falls back to the WORKOS_API_KEY environment variable.
            client_id: WorkOS client ID. Falls back to the WORKOS_CLIENT_ID environment variable.
            base_url: Base URL for API requests. Falls back to WORKOS_BASE_URL or "https://api.workos.com".
            request_timeout: HTTP request timeout in seconds. Falls back to WORKOS_REQUEST_TIMEOUT or 60.
            jwt_leeway: JWT clock skew leeway in seconds.
            max_retries: Maximum number of retries for failed requests. Defaults to 3.

        Raises:
            ValueError: If neither api_key nor client_id is provided, directly or via environment variables.
        """
        super().__init__(
            api_key=api_key,
            client_id=client_id,
            base_url=base_url,
            request_timeout=request_timeout,
            jwt_leeway=jwt_leeway,
            max_retries=max_retries,
        )
        self._client = httpx.AsyncClient(
            timeout=self._request_timeout, follow_redirects=True
        )

    async def close(self) -> None:
        """Close the underlying HTTP client and release resources."""
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncWorkOSClient":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()

    @overload
    async def request(
        self,
        method: str,
        path: str,
        *,
        model: Type[D],
        params: Optional[Dict[str, Any]] = ...,
        body: Optional[Dict[str, Any]] = ...,
        idempotency_key: Optional[str] = ...,
        request_options: Optional[RequestOptions] = ...,
    ) -> D: ...

    @overload
    async def request(
        self,
        method: str,
        path: str,
        *,
        model: None = ...,
        params: Optional[Dict[str, Any]] = ...,
        body: Optional[Dict[str, Any]] = ...,
        idempotency_key: Optional[str] = ...,
        request_options: Optional[RequestOptions] = ...,
    ) -> Optional[Dict[str, Any]]: ...

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        model: Optional[Type[Deserializable]] = None,
        idempotency_key: Optional[str] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> Any:
        """Make an async HTTP request with retry logic."""
        url = f"{self._resolve_base_url(request_options)}/{path}"
        headers = self._build_headers(method, idempotency_key, request_options)
        timeout = self._resolve_timeout(request_options)
        max_retries = self._resolve_max_retries(request_options)
        last_error: Optional[Exception] = None
        for attempt in range(max_retries + 1):
            try:
                response = await self._client.request(
                    method=method.upper(),
                    url=url,
                    params=params,
                    json=body if body is not None else None,
                    headers=headers,
                    timeout=timeout,
                )
                if response.status_code in RETRY_STATUS_CODES and attempt < max_retries:
                    delay = self._calculate_retry_delay(
                        attempt, response.headers.get("Retry-After")
                    )
                    await asyncio.sleep(delay)
                    continue
                if response.status_code >= 400:
                    self._raise_error(response)
                return self._deserialize_response(response, model)
            except httpx.TimeoutException as e:
                last_error = e
                if attempt < max_retries:
                    await asyncio.sleep(self._calculate_retry_delay(attempt))
                    continue
                raise WorkOSTimeoutError(f"Request timed out: {e}") from e
            except httpx.ConnectError as e:
                last_error = e
                if attempt < max_retries:
                    await asyncio.sleep(self._calculate_retry_delay(attempt))
                    continue
                raise WorkOSConnectionError(f"Connection failed: {e}") from e
            except httpx.HTTPError as e:
                last_error = e
                if attempt < max_retries:
                    await asyncio.sleep(self._calculate_retry_delay(attempt))
                    continue
                raise WorkOSError(f"Network error: {e}") from e
        raise WorkOSError("Max retries exceeded") from last_error

    async def request_raw(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> Dict[str, Any]:
        """Make an async HTTP request without model deserialization.

        Returns the raw JSON dict. Use this when you need the raw
        response without mapping through a model class.
        """
        result = await self.request(
            method=method,
            path=path,
            params=params,
            body=body,
            idempotency_key=idempotency_key,
            request_options=request_options,
        )
        return result if isinstance(result, dict) else {}

    async def request_list(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> list[Dict[str, Any]]:
        """Make an async HTTP request expecting a bare JSON array response.

        Returns the raw list of dicts. Use this for endpoints that return
        a JSON array instead of a paginated envelope.
        """
        result = await self.request(
            method=method,
            path=path,
            params=params,
            body=body,
            idempotency_key=idempotency_key,
            request_options=request_options,
        )
        if not isinstance(result, list):
            raise WorkOSError(
                f"Expected array response from {method.upper()} /{path}, got {type(result).__name__}"
            )
        return result

    async def request_page(
        self,
        method: str,
        path: str,
        *,
        model: Type[D],
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        request_options: Optional[RequestOptions] = None,
    ) -> AsyncPage[D]:
        """Make an async HTTP request that returns a paginated response."""
        raw = await self.request(
            method=method,
            path=path,
            params=params,
            body=body,
            request_options=request_options,
        )
        data: Dict[str, Any] = raw if isinstance(raw, dict) else {}
        raw_items: list[Any] = cast(list[Any], data.get("data") or [])
        items: list[D] = [
            cast(D, model.from_dict(cast(Dict[str, Any], item))) for item in raw_items
        ]
        list_metadata = ListMetadata.from_dict(
            cast(Dict[str, Any], data.get("list_metadata", {}))
        )

        async def _fetch(*, after: Optional[str] = None) -> AsyncPage[D]:
            next_params = {**(params or {}), "after": after}
            return await self.request_page(
                method=method,
                path=path,
                model=model,
                params=next_params,
                body=body,
                request_options=request_options,
            )

        return AsyncPage(data=items, list_metadata=list_metadata, _fetch_page=_fetch)
