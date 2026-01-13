from typing import Optional, Protocol

from workos.types.api_keys import ApiKey
from workos.typing.sync_or_async import SyncOrAsync
from workos.utils.http_client import AsyncHTTPClient, SyncHTTPClient
from workos.utils.request_helper import REQUEST_METHOD_DELETE, REQUEST_METHOD_POST

API_KEYS_PATH = "api_keys"
API_KEY_VALIDATION_PATH = "api_keys/validations"
RESOURCE_OBJECT_ATTRIBUTE_NAME = "api_key"


class ApiKeysModule(Protocol):
    def validate_api_key(self, *, value: str) -> SyncOrAsync[Optional[ApiKey]]:
        """Validate an API key.

        Kwargs:
            value (str): API key value

        Returns:
            Optional[ApiKey]: Returns ApiKey resource object
                if supplied value was valid, None if it was not
        """
        ...

    def delete_api_key(self, api_key_id: str) -> SyncOrAsync[None]:
        """Delete an API key.

        Args:
            api_key_id (str): The ID of the API key to delete

        Returns:
            None
        """
        ...


class ApiKeys(ApiKeysModule):
    _http_client: SyncHTTPClient

    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def validate_api_key(self, *, value: str) -> Optional[ApiKey]:
        response = self._http_client.request(
            API_KEY_VALIDATION_PATH, method=REQUEST_METHOD_POST, json={"value": value}
        )
        if response.get(RESOURCE_OBJECT_ATTRIBUTE_NAME) is None:
            return None
        return ApiKey.model_validate(response[RESOURCE_OBJECT_ATTRIBUTE_NAME])

    def delete_api_key(self, api_key_id: str) -> None:
        self._http_client.request(
            f"{API_KEYS_PATH}/{api_key_id}",
            method=REQUEST_METHOD_DELETE,
        )


class AsyncApiKeys(ApiKeysModule):
    _http_client: AsyncHTTPClient

    def __init__(self, http_client: AsyncHTTPClient):
        self._http_client = http_client

    async def validate_api_key(self, *, value: str) -> Optional[ApiKey]:
        response = await self._http_client.request(
            API_KEY_VALIDATION_PATH, method=REQUEST_METHOD_POST, json={"value": value}
        )
        if response.get(RESOURCE_OBJECT_ATTRIBUTE_NAME) is None:
            return None
        return ApiKey.model_validate(response[RESOURCE_OBJECT_ATTRIBUTE_NAME])

    async def delete_api_key(self, api_key_id: str) -> None:
        await self._http_client.request(
            f"{API_KEYS_PATH}/{api_key_id}",
            method=REQUEST_METHOD_DELETE,
        )
