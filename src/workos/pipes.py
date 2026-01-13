from typing import Dict, Optional, Protocol

from workos.types.pipes import (
    GetAccessTokenFailureResponse,
    GetAccessTokenResponse,
    GetAccessTokenSuccessResponse,
)
from workos.typing.sync_or_async import SyncOrAsync
from workos.utils.http_client import AsyncHTTPClient, SyncHTTPClient
from workos.utils.request_helper import REQUEST_METHOD_POST


class PipesModule(Protocol):
    """Protocol defining the Pipes module interface."""

    def get_access_token(
        self,
        *,
        provider: str,
        user_id: str,
        organization_id: Optional[str] = None,
    ) -> SyncOrAsync[GetAccessTokenResponse]:
        """Retrieve an access token for a third-party provider.

        Kwargs:
            provider (str): The third-party provider identifier
            user_id (str): The WorkOS user ID
            organization_id (str, optional): The WorkOS organization ID

        Returns:
            GetAccessTokenResponse: Success response with token or failure response with error
        """
        ...


class Pipes(PipesModule):
    """Sync implementation of the Pipes module."""

    _http_client: SyncHTTPClient

    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def get_access_token(
        self,
        *,
        provider: str,
        user_id: str,
        organization_id: Optional[str] = None,
    ) -> GetAccessTokenResponse:
        json_data: Dict[str, str] = {"user_id": user_id}
        if organization_id is not None:
            json_data["organization_id"] = organization_id

        response = self._http_client.request(
            f"data-integrations/{provider}/token",
            method=REQUEST_METHOD_POST,
            json=json_data,
        )

        if response.get("active") is True:
            return GetAccessTokenSuccessResponse.model_validate(response)
        return GetAccessTokenFailureResponse.model_validate(response)


class AsyncPipes(PipesModule):
    """Async implementation of the Pipes module."""

    _http_client: AsyncHTTPClient

    def __init__(self, http_client: AsyncHTTPClient):
        self._http_client = http_client

    async def get_access_token(
        self,
        *,
        provider: str,
        user_id: str,
        organization_id: Optional[str] = None,
    ) -> GetAccessTokenResponse:
        json_data: Dict[str, str] = {"user_id": user_id}
        if organization_id is not None:
            json_data["organization_id"] = organization_id

        response = await self._http_client.request(
            f"data-integrations/{provider}/token",
            method=REQUEST_METHOD_POST,
            json=json_data,
        )

        if response.get("active") is True:
            return GetAccessTokenSuccessResponse.model_validate(response)
        return GetAccessTokenFailureResponse.model_validate(response)
