from functools import partial
from typing import Optional, Protocol, Sequence

from workos.types.connect import ClientSecret, ConnectApplication
from workos.types.connect.connect_application import ApplicationType
from workos.types.connect.list_filters import (
    ClientSecretListFilters,
    ConnectApplicationListFilters,
)
from workos.types.list_resource import ListMetadata, ListPage, WorkOSListResource
from workos.typing.sync_or_async import SyncOrAsync
from workos.utils.http_client import AsyncHTTPClient, SyncHTTPClient
from workos.utils.pagination_order import PaginationOrder
from workos.utils.request_helper import (
    DEFAULT_LIST_RESPONSE_LIMIT,
    REQUEST_METHOD_DELETE,
    REQUEST_METHOD_GET,
    REQUEST_METHOD_POST,
    REQUEST_METHOD_PUT,
)

CONNECT_APPLICATIONS_PATH = "connect/applications"
CONNECT_CLIENT_SECRETS_PATH = "connect/client_secrets"

ConnectApplicationsListResource = WorkOSListResource[
    ConnectApplication, ConnectApplicationListFilters, ListMetadata
]

ClientSecretsListResource = WorkOSListResource[
    ClientSecret, ClientSecretListFilters, ListMetadata
]


class ConnectModule(Protocol):
    """Offers methods through the WorkOS Connect service."""

    def list_applications(
        self,
        *,
        organization_id: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> SyncOrAsync[ConnectApplicationsListResource]:
        """Retrieve a list of connect applications.

        Kwargs:
            organization_id (str): Filter by organization ID. (Optional)
            limit (int): Maximum number of records to return. (Optional)
            before (str): Pagination cursor to receive records before a provided ID. (Optional)
            after (str): Pagination cursor to receive records after a provided ID. (Optional)
            order (Literal["asc","desc"]): Sort records in either ascending or descending order. (Optional)

        Returns:
            ConnectApplicationsListResource: Applications list response from WorkOS.
        """
        ...

    def get_application(self, application_id: str) -> SyncOrAsync[ConnectApplication]:
        """Gets details for a single connect application.

        Args:
            application_id (str): Application ID or client ID.

        Returns:
            ConnectApplication: Application response from WorkOS.
        """
        ...

    def create_application(
        self,
        *,
        name: str,
        application_type: ApplicationType,
        is_first_party: bool,
        description: Optional[str] = None,
        scopes: Optional[Sequence[str]] = None,
        redirect_uris: Optional[Sequence[str]] = None,
        uses_pkce: Optional[bool] = None,
        organization_id: Optional[str] = None,
    ) -> SyncOrAsync[ConnectApplication]:
        """Create a connect application.

        Kwargs:
            name (str): Application name.
            application_type (ApplicationType): "oauth" or "m2m".
            is_first_party (bool): Whether this is a first-party application.
            description (str): Application description. (Optional)
            scopes (Sequence[str]): Permission slugs. (Optional)
            redirect_uris (Sequence[str]): OAuth redirect URIs. (Optional)
            uses_pkce (bool): PKCE support (OAuth only). (Optional)
            organization_id (str): Organization ID. Required for M2M and third-party OAuth. (Optional)

        Returns:
            ConnectApplication: Created application response from WorkOS.
        """
        ...

    def update_application(
        self,
        *,
        application_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        scopes: Optional[Sequence[str]] = None,
        redirect_uris: Optional[Sequence[str]] = None,
    ) -> SyncOrAsync[ConnectApplication]:
        """Update a connect application.

        Kwargs:
            application_id (str): Application ID or client ID.
            name (str): Updated application name. (Optional)
            description (str): Updated description. (Optional)
            scopes (Sequence[str]): Updated permission slugs. (Optional)
            redirect_uris (Sequence[str]): Updated OAuth redirect URIs. (Optional)

        Returns:
            ConnectApplication: Updated application response from WorkOS.
        """
        ...

    def delete_application(self, application_id: str) -> SyncOrAsync[None]:
        """Delete a connect application.

        Args:
            application_id (str): Application ID or client ID.

        Returns:
            None
        """
        ...

    def create_client_secret(self, application_id: str) -> SyncOrAsync[ClientSecret]:
        """Create a client secret for a connect application.

        Args:
            application_id (str): Application ID or client ID.

        Returns:
            ClientSecret: Created client secret response from WorkOS.
        """
        ...

    def list_client_secrets(
        self,
        application_id: str,
        *,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> SyncOrAsync[ClientSecretsListResource]:
        """List client secrets for a connect application.

        Args:
            application_id (str): Application ID or client ID.

        Kwargs:
            limit (int): Maximum number of records to return. (Optional)
            before (str): Pagination cursor to receive records before a provided ID. (Optional)
            after (str): Pagination cursor to receive records after a provided ID. (Optional)
            order (Literal["asc","desc"]): Sort records in either ascending or descending order. (Optional)

        Returns:
            ClientSecretsListResource: Client secrets list response from WorkOS.
        """
        ...

    def delete_client_secret(self, client_secret_id: str) -> SyncOrAsync[None]:
        """Delete a client secret.

        Args:
            client_secret_id (str): Client secret ID.

        Returns:
            None
        """
        ...


class Connect(ConnectModule):
    _http_client: SyncHTTPClient

    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def list_applications(
        self,
        *,
        organization_id: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> ConnectApplicationsListResource:
        list_params: ConnectApplicationListFilters = {
            "organization_id": organization_id,
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        response = self._http_client.request(
            CONNECT_APPLICATIONS_PATH,
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        return WorkOSListResource[
            ConnectApplication, ConnectApplicationListFilters, ListMetadata
        ](
            list_method=self.list_applications,
            list_args=list_params,
            **ListPage[ConnectApplication](**response).model_dump(),
        )

    def get_application(self, application_id: str) -> ConnectApplication:
        response = self._http_client.request(
            f"{CONNECT_APPLICATIONS_PATH}/{application_id}",
            method=REQUEST_METHOD_GET,
        )

        return ConnectApplication.model_validate(response)

    def create_application(
        self,
        *,
        name: str,
        application_type: ApplicationType,
        is_first_party: bool,
        description: Optional[str] = None,
        scopes: Optional[Sequence[str]] = None,
        redirect_uris: Optional[Sequence[str]] = None,
        uses_pkce: Optional[bool] = None,
        organization_id: Optional[str] = None,
    ) -> ConnectApplication:
        json = {
            "name": name,
            "application_type": application_type,
            "is_first_party": is_first_party,
            "description": description,
            "scopes": scopes,
            "redirect_uris": redirect_uris,
            "uses_pkce": uses_pkce,
            "organization_id": organization_id,
        }

        response = self._http_client.request(
            CONNECT_APPLICATIONS_PATH,
            method=REQUEST_METHOD_POST,
            json=json,
        )

        return ConnectApplication.model_validate(response)

    def update_application(
        self,
        *,
        application_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        scopes: Optional[Sequence[str]] = None,
        redirect_uris: Optional[Sequence[str]] = None,
    ) -> ConnectApplication:
        json = {
            "name": name,
            "description": description,
            "scopes": scopes,
            "redirect_uris": redirect_uris,
        }

        response = self._http_client.request(
            f"{CONNECT_APPLICATIONS_PATH}/{application_id}",
            method=REQUEST_METHOD_PUT,
            json=json,
        )

        return ConnectApplication.model_validate(response)

    def delete_application(self, application_id: str) -> None:
        self._http_client.request(
            f"{CONNECT_APPLICATIONS_PATH}/{application_id}",
            method=REQUEST_METHOD_DELETE,
        )

    def create_client_secret(self, application_id: str) -> ClientSecret:
        response = self._http_client.request(
            f"{CONNECT_APPLICATIONS_PATH}/{application_id}/client_secrets",
            method=REQUEST_METHOD_POST,
            json={},
        )

        return ClientSecret.model_validate(response)

    def list_client_secrets(
        self,
        application_id: str,
        *,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> ClientSecretsListResource:
        list_params: ClientSecretListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        response = self._http_client.request(
            f"{CONNECT_APPLICATIONS_PATH}/{application_id}/client_secrets",
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        return WorkOSListResource[ClientSecret, ClientSecretListFilters, ListMetadata](
            list_method=partial(self.list_client_secrets, application_id),
            list_args=list_params,
            **ListPage[ClientSecret](**response).model_dump(),
        )

    def delete_client_secret(self, client_secret_id: str) -> None:
        self._http_client.request(
            f"{CONNECT_CLIENT_SECRETS_PATH}/{client_secret_id}",
            method=REQUEST_METHOD_DELETE,
        )


class AsyncConnect(ConnectModule):
    _http_client: AsyncHTTPClient

    def __init__(self, http_client: AsyncHTTPClient):
        self._http_client = http_client

    async def list_applications(
        self,
        *,
        organization_id: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> ConnectApplicationsListResource:
        list_params: ConnectApplicationListFilters = {
            "organization_id": organization_id,
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        response = await self._http_client.request(
            CONNECT_APPLICATIONS_PATH,
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        return WorkOSListResource[
            ConnectApplication, ConnectApplicationListFilters, ListMetadata
        ](
            list_method=self.list_applications,
            list_args=list_params,
            **ListPage[ConnectApplication](**response).model_dump(),
        )

    async def get_application(self, application_id: str) -> ConnectApplication:
        response = await self._http_client.request(
            f"{CONNECT_APPLICATIONS_PATH}/{application_id}",
            method=REQUEST_METHOD_GET,
        )

        return ConnectApplication.model_validate(response)

    async def create_application(
        self,
        *,
        name: str,
        application_type: ApplicationType,
        is_first_party: bool,
        description: Optional[str] = None,
        scopes: Optional[Sequence[str]] = None,
        redirect_uris: Optional[Sequence[str]] = None,
        uses_pkce: Optional[bool] = None,
        organization_id: Optional[str] = None,
    ) -> ConnectApplication:
        json = {
            "name": name,
            "application_type": application_type,
            "is_first_party": is_first_party,
            "description": description,
            "scopes": scopes,
            "redirect_uris": redirect_uris,
            "uses_pkce": uses_pkce,
            "organization_id": organization_id,
        }

        response = await self._http_client.request(
            CONNECT_APPLICATIONS_PATH,
            method=REQUEST_METHOD_POST,
            json=json,
        )

        return ConnectApplication.model_validate(response)

    async def update_application(
        self,
        *,
        application_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        scopes: Optional[Sequence[str]] = None,
        redirect_uris: Optional[Sequence[str]] = None,
    ) -> ConnectApplication:
        json = {
            "name": name,
            "description": description,
            "scopes": scopes,
            "redirect_uris": redirect_uris,
        }

        response = await self._http_client.request(
            f"{CONNECT_APPLICATIONS_PATH}/{application_id}",
            method=REQUEST_METHOD_PUT,
            json=json,
        )

        return ConnectApplication.model_validate(response)

    async def delete_application(self, application_id: str) -> None:
        await self._http_client.request(
            f"{CONNECT_APPLICATIONS_PATH}/{application_id}",
            method=REQUEST_METHOD_DELETE,
        )

    async def create_client_secret(self, application_id: str) -> ClientSecret:
        response = await self._http_client.request(
            f"{CONNECT_APPLICATIONS_PATH}/{application_id}/client_secrets",
            method=REQUEST_METHOD_POST,
            json={},
        )

        return ClientSecret.model_validate(response)

    async def list_client_secrets(
        self,
        application_id: str,
        *,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> ClientSecretsListResource:
        list_params: ClientSecretListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        response = await self._http_client.request(
            f"{CONNECT_APPLICATIONS_PATH}/{application_id}/client_secrets",
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        return WorkOSListResource[ClientSecret, ClientSecretListFilters, ListMetadata](
            list_method=partial(self.list_client_secrets, application_id),
            list_args=list_params,
            **ListPage[ClientSecret](**response).model_dump(),
        )

    async def delete_client_secret(self, client_secret_id: str) -> None:
        await self._http_client.request(
            f"{CONNECT_CLIENT_SECRETS_PATH}/{client_secret_id}",
            method=REQUEST_METHOD_DELETE,
        )
