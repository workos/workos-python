from typing import Protocol

from workos.types.api_keys import ApiKey
from workos.typing.sync_or_async import SyncOrAsync
from workos.utils.http_client import AsyncHTTPClient, SyncHTTPClient
from workos.utils.request_helper import REQUEST_METHOD_POST



class ApiKeysModule(Protocol):
    def validate_api_key(self) -> SyncOrAsync[ApiKey]:
        """Validates the configured API key.

        Returns:
            ApiKey: The validated API key details containing
                information about the key's name and usage

        Raises:
            AuthenticationException: If the API key is invalid or
                unauthorized (401)
            NotFoundException: If the API key is not found (404)
            ServerException: If the API server encounters an error
                (5xx)
        """
        ...


class ApiKeys(ApiKeysModule):
    _http_client: SyncHTTPClient

    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def validate_api_key(self) -> ApiKey:
        response = self._http_client.request(
            "api_keys/validate",
            method=REQUEST_METHOD_POST,
        )

        return ApiKey.model_validate(response)


class AsyncApiKeys(ApiKeysModule):
    _http_client: AsyncHTTPClient

    def __init__(self, http_client: AsyncHTTPClient):
        self._http_client = http_client

    async def validate_api_key(self) -> ApiKey:
        response = await self._http_client.request(
            "api_keys/validate",
            method=REQUEST_METHOD_POST,
        )

        return ApiKey.model_validate(response)
