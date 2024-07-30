from typing import Optional, Protocol, Union

import workos
from workos.typing.sync_or_async import SyncOrAsync
from workos.utils.http_client import AsyncHTTPClient, SyncHTTPClient
from workos.utils.pagination_order import PaginationOrder
from workos.resources.sso import (
    ConnectionWithDomains,
    Profile,
    ProfileAndToken,
    SsoProviderType,
)
from workos.utils.connection_types import ConnectionType
from workos.utils.request_helper import (
    DEFAULT_LIST_RESPONSE_LIMIT,
    RESPONSE_TYPE_CODE,
    REQUEST_METHOD_DELETE,
    REQUEST_METHOD_GET,
    REQUEST_METHOD_POST,
    RequestHelper,
)
from workos.utils.validation import SSO_MODULE, validate_settings
from workos.resources.list import (
    AsyncWorkOsListResource,
    ListArgs,
    ListMetadata,
    ListPage,
    SyncOrAsyncListResource,
    WorkOsListResource,
)

AUTHORIZATION_PATH = "sso/authorize"
TOKEN_PATH = "sso/token"
PROFILE_PATH = "sso/profile"

OAUTH_GRANT_TYPE = "authorization_code"


class ConnectionsListFilters(ListArgs, total=False):
    connection_type: Optional[ConnectionType]
    domain: Optional[str]
    organization_id: Optional[str]


class SSOModule(Protocol):
    _http_client: Union[SyncHTTPClient, AsyncHTTPClient]

    def get_authorization_url(
        self,
        redirect_uri: str,
        domain_hint: Optional[str] = None,
        login_hint: Optional[str] = None,
        state: Optional[str] = None,
        provider: Optional[SsoProviderType] = None,
        connection_id: Optional[str] = None,
        organization_id: Optional[str] = None,
    ) -> str:
        """Generate an OAuth 2.0 authorization URL.

        The URL generated will redirect a User to the Identity Provider configured through
        WorkOS.

        Kwargs:
            redirect_uri (str) - A valid redirect URI, as specified on WorkOS
            state (str) - An encoded string passed to WorkOS that'd be preserved through the authentication workflow, passed
            back as a query parameter
            provider (SSOProviderType) - Authentication service provider descriptor
            connection_id (string) - Unique identifier for a WorkOS Connection
            organization_id (string) - Unique identifier for a WorkOS Organization

        Returns:
            str: URL to redirect a User to to begin the OAuth workflow with WorkOS
        """
        params = {
            "client_id": workos.client_id,
            "redirect_uri": redirect_uri,
            "response_type": RESPONSE_TYPE_CODE,
        }

        if connection_id is None and organization_id is None and provider is None:
            raise ValueError(
                "Incomplete arguments. Need to specify either a 'connection', 'organization', or 'provider'"
            )
        if provider is not None:
            params["provider"] = provider
        if domain_hint is not None:
            params["domain_hint"] = domain_hint
        if login_hint is not None:
            params["login_hint"] = login_hint
        if connection_id is not None:
            params["connection"] = connection_id
        if organization_id is not None:
            params["organization"] = organization_id

        if state is not None:
            params["state"] = state

        return RequestHelper.build_url_with_query_params(
            base_url=self._http_client.base_url, path=AUTHORIZATION_PATH, **params
        )

    def get_profile(self, accessToken: str) -> SyncOrAsync[Profile]: ...

    def get_profile_and_token(self, code: str) -> SyncOrAsync[ProfileAndToken]: ...

    def get_connection(self, connection: str) -> SyncOrAsync[ConnectionWithDomains]: ...

    def list_connections(
        self,
        connection_type: Optional[ConnectionType] = None,
        domain: Optional[str] = None,
        organization_id: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> SyncOrAsyncListResource: ...

    def delete_connection(self, connection: str) -> SyncOrAsync[None]: ...


class SSO(SSOModule):
    """Offers methods to assist in authenticating through the WorkOS SSO service."""

    _http_client: SyncHTTPClient

    @validate_settings(SSO_MODULE)
    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def get_profile(self, access_token: str) -> Profile:
        """
        Verify that SSO has been completed successfully and retrieve the identity of the user.

        Args:
            accessToken (str): the token used to authenticate the API call

        Returns:
            Profile
        """
        response = self._http_client.request(
            PROFILE_PATH, method=REQUEST_METHOD_GET, token=access_token
        )

        return Profile.model_validate(response)

    def get_profile_and_token(self, code: str) -> ProfileAndToken:
        """Get the profile of an authenticated User

        Once authenticated, using the code returned having followed the authorization URL,
        get the WorkOS profile of the User.

        Args:
            code (str): Code returned by WorkOS on completion of OAuth 2.0 workflow

        Returns:
            ProfileAndToken: WorkOSProfileAndToken object representing the User
        """
        params = {
            "client_id": workos.client_id,
            "client_secret": workos.api_key,
            "code": code,
            "grant_type": OAUTH_GRANT_TYPE,
        }

        response = self._http_client.request(
            TOKEN_PATH, method=REQUEST_METHOD_POST, params=params
        )

        return ProfileAndToken.model_validate(response)

    def get_connection(self, connection_id: str) -> ConnectionWithDomains:
        """Gets details for a single Connection

        Args:
            connection (str): Connection unique identifier

        Returns:
            dict: Connection response from WorkOS.
        """
        response = self._http_client.request(
            f"connections/{connection_id}",
            method=REQUEST_METHOD_GET,
            token=workos.api_key,
        )

        return ConnectionWithDomains.model_validate(response)

    def list_connections(
        self,
        connection_type: Optional[ConnectionType] = None,
        domain: Optional[str] = None,
        organization_id: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> WorkOsListResource[
        ConnectionWithDomains, ConnectionsListFilters, ListMetadata
    ]:
        """Gets details for existing Connections.

        Args:
            connection_type (ConnectionType): Authentication service provider descriptor. (Optional)
            domain (str): Domain of a Connection. (Optional)
            limit (int): Maximum number of records to return. (Optional)
            before (str): Pagination cursor to receive records before a provided Connection ID. (Optional)
            after (str): Pagination cursor to receive records after a provided Connection ID. (Optional)
            order (Order): Sort records in either ascending or descending order by created_at timestamp.

        Returns:
            dict: Connections response from WorkOS.
        """

        params: ConnectionsListFilters = {
            "connection_type": connection_type,
            "domain": domain,
            "organization_id": organization_id,
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        response = self._http_client.request(
            "connections",
            method=REQUEST_METHOD_GET,
            params=params,
            token=workos.api_key,
        )

        return WorkOsListResource[
            ConnectionWithDomains, ConnectionsListFilters, ListMetadata
        ](
            list_method=self.list_connections,
            list_args=params,
            **ListPage[ConnectionWithDomains](**response).model_dump(),
        )

    def delete_connection(self, connection_id: str) -> None:
        """Deletes a single Connection

        Args:
            connection (str): Connection unique identifier
        """
        self._http_client.request(
            f"connections/{connection_id}",
            method=REQUEST_METHOD_DELETE,
            token=workos.api_key,
        )


class AsyncSSO(SSOModule):
    """Offers methods to assist in authenticating through the WorkOS SSO service."""

    _http_client: AsyncHTTPClient

    @validate_settings(SSO_MODULE)
    def __init__(self, http_client: AsyncHTTPClient):
        self._http_client = http_client

    async def get_profile(self, access_token: str) -> Profile:
        """
        Verify that SSO has been completed successfully and retrieve the identity of the user.

        Args:
            accessToken (str): the token used to authenticate the API call

        Returns:
            Profile
        """
        response = await self._http_client.request(
            PROFILE_PATH, method=REQUEST_METHOD_GET, token=access_token
        )

        return Profile.model_validate(response)

    async def get_profile_and_token(self, code: str) -> ProfileAndToken:
        """Get the profile of an authenticated User

        Once authenticated, using the code returned having followed the authorization URL,
        get the WorkOS profile of the User.

        Args:
            code (str): Code returned by WorkOS on completion of OAuth 2.0 workflow

        Returns:
            ProfileAndToken: WorkOSProfileAndToken object representing the User
        """
        params = {
            "client_id": workos.client_id,
            "client_secret": workos.api_key,
            "code": code,
            "grant_type": OAUTH_GRANT_TYPE,
        }

        response = await self._http_client.request(
            TOKEN_PATH, method=REQUEST_METHOD_POST, params=params
        )

        return ProfileAndToken.model_validate(response)

    async def get_connection(self, connection_id: str) -> ConnectionWithDomains:
        """Gets details for a single Connection

        Args:
            connection (str): Connection unique identifier

        Returns:
            dict: Connection response from WorkOS.
        """
        response = await self._http_client.request(
            f"connections/{connection_id}",
            method=REQUEST_METHOD_GET,
            token=workos.api_key,
        )

        return ConnectionWithDomains.model_validate(response)

    async def list_connections(
        self,
        connection_type: Optional[ConnectionType] = None,
        domain: Optional[str] = None,
        organization_id: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> AsyncWorkOsListResource[
        ConnectionWithDomains, ConnectionsListFilters, ListMetadata
    ]:
        """Gets details for existing Connections.

        Args:
            connection_type (ConnectionType): Authentication service provider descriptor. (Optional)
            domain (str): Domain of a Connection. (Optional)
            limit (int): Maximum number of records to return. (Optional)
            before (str): Pagination cursor to receive records before a provided Connection ID. (Optional)
            after (str): Pagination cursor to receive records after a provided Connection ID. (Optional)
            order (Order): Sort records in either ascending or descending order by created_at timestamp.

        Returns:
            dict: Connections response from WorkOS.
        """

        params: ConnectionsListFilters = {
            "connection_type": connection_type,
            "domain": domain,
            "organization_id": organization_id,
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        response = await self._http_client.request(
            "connections",
            method=REQUEST_METHOD_GET,
            params=params,
            token=workos.api_key,
        )

        return AsyncWorkOsListResource[
            ConnectionWithDomains, ConnectionsListFilters, ListMetadata
        ](
            list_method=self.list_connections,
            list_args=params,
            **ListPage[ConnectionWithDomains](**response).model_dump(),
        )

    async def delete_connection(self, connection_id: str) -> None:
        """Deletes a single Connection

        Args:
            connection (str): Connection unique identifier
        """
        await self._http_client.request(
            f"connections/{connection_id}",
            method=REQUEST_METHOD_DELETE,
            token=workos.api_key,
        )
