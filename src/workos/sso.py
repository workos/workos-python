from typing import Optional, Protocol
from workos._client_configuration import ClientConfiguration
from workos.types.sso.connection import ConnectionType
from workos.types.sso.sso_provider_type import SsoProviderType
from workos.typing.sync_or_async import SyncOrAsync
from workos.utils.http_client import AsyncHTTPClient, SyncHTTPClient
from workos.utils.pagination_order import PaginationOrder
from workos.types.sso import ConnectionWithDomains, Profile, ProfileAndToken
from workos.utils.request_helper import (
    DEFAULT_LIST_RESPONSE_LIMIT,
    RESPONSE_TYPE_CODE,
    REQUEST_METHOD_DELETE,
    REQUEST_METHOD_GET,
    REQUEST_METHOD_POST,
    QueryParameters,
    RequestHelper,
    REQUEST_METHOD_PUT,
)
from workos.types.list_resource import (
    ListArgs,
    ListMetadata,
    ListPage,
    WorkOSListResource,
)

AUTHORIZATION_PATH = "sso/authorize"
TOKEN_PATH = "sso/token"
PROFILE_PATH = "sso/profile"

OAUTH_GRANT_TYPE = "authorization_code"


class ConnectionsListFilters(ListArgs, total=False):
    connection_type: Optional[ConnectionType]
    domain: Optional[str]
    organization_id: Optional[str]


ConnectionsListResource = WorkOSListResource[
    ConnectionWithDomains, ConnectionsListFilters, ListMetadata
]


class SSOModule(Protocol):
    """Offers methods to assist in authenticating through the WorkOS SSO service."""

    _client_configuration: ClientConfiguration

    def get_authorization_url(
        self,
        *,
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

        This method is purposefully designed as synchronous as it does not make any HTTP requests.

        Kwargs:
            redirect_uri (str) : A valid redirect URI, as specified on WorkOS
            state (str) : An encoded string passed to WorkOS that'd be preserved through the authentication workflow, passed
            back as a query parameter
            provider (SSOProviderType) : Authentication service provider descriptor
            connection_id (string) : Unique identifier for a WorkOS Connection
            organization_id (string) : Unique identifier for a WorkOS Organization

        Returns:
            str: URL to redirect a User to to begin the OAuth workflow with WorkOS
        """
        params: QueryParameters = {
            "client_id": self._client_configuration.client_id,
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
            base_url=self._client_configuration.base_url,
            path=AUTHORIZATION_PATH,
            **params,
        )

    def get_profile(self, access_token: str) -> SyncOrAsync[Profile]:
        """
        Verify that SSO has been completed successfully and retrieve the identity of the user.

        Args:
            access_token (str): The token used to authenticate the API call

        Returns:
            Profile
        """
        ...

    def get_profile_and_token(self, code: str) -> SyncOrAsync[ProfileAndToken]:
        """Get the profile of an authenticated User

        Once authenticated, using the code returned having followed the authorization URL,
        get the WorkOS profile of the User.

        Args:
            code (str): Code returned by WorkOS on completion of OAuth 2.0 workflow.

        Returns:
            ProfileAndToken: WorkOSProfileAndToken object representing the User.
        """
        ...

    def get_connection(self, connection_id: str) -> SyncOrAsync[ConnectionWithDomains]:
        """Gets details for a single Connection

        Args:
            connection (str): Connection unique identifier

        Returns:
            ConnectionWithDomains: Connection response from WorkOS.
        """
        ...

    def list_connections(
        self,
        *,
        connection_type: Optional[ConnectionType] = None,
        domain: Optional[str] = None,
        organization_id: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> SyncOrAsync[ConnectionsListResource]:
        """Gets details for existing Connections.

        Kwargs:
            connection_type (ConnectionType): Authentication service provider descriptor. (Optional)
            domain (str): Domain of a Connection. (Optional)
            limit (int): Maximum number of records to return. (Optional)
            before (str): Pagination cursor to receive records before a provided Connection ID. (Optional)
            after (str): Pagination cursor to receive records after a provided Connection ID. (Optional)
            order (Literal["asc","desc"]): Sort records in either ascending or descending (default) order by created_at timestamp. (Optional)

        Returns:
            ConnectionsListResource: Connections response from WorkOS.
        """
        ...

    def update_connection(
        self,
        *,
        connection_id: str,
        saml_options_signing_key: Optional[str] = None,
        saml_options_signing_cert: Optional[str] = None,
    ) -> SyncOrAsync[ConnectionWithDomains]:
        """Updates a single connection

        Args:
            connection_id (str): Connection unique identifier
            saml_options_signing_key (str): Signing key for the connection (Optional)
            saml_options_signing_cert (str): Signing certificate for the connection (Optional)
        Returns:
            None
        """
        ...

    def delete_connection(self, connection_id: str) -> SyncOrAsync[None]:
        """Deletes a single Connection

        Args:
            connection_id (str): Connection unique identifier

        Returns:
            None
        """
        ...


class SSO(SSOModule):
    _http_client: SyncHTTPClient

    def __init__(
        self, http_client: SyncHTTPClient, client_configuration: ClientConfiguration
    ):
        self._client_configuration = client_configuration
        self._http_client = http_client

    def get_profile(self, access_token: str) -> Profile:
        response = self._http_client.request(
            PROFILE_PATH,
            method=REQUEST_METHOD_GET,
            headers={**self._http_client.auth_header_from_token(access_token)},
            exclude_default_auth_headers=True,
        )

        return Profile.model_validate(response)

    def get_profile_and_token(self, code: str) -> ProfileAndToken:
        json = {
            "client_id": self._http_client.client_id,
            "client_secret": self._http_client.api_key,
            "code": code,
            "grant_type": OAUTH_GRANT_TYPE,
        }

        response = self._http_client.request(
            TOKEN_PATH, method=REQUEST_METHOD_POST, json=json
        )

        return ProfileAndToken.model_validate(response)

    def get_connection(self, connection_id: str) -> ConnectionWithDomains:
        response = self._http_client.request(
            f"connections/{connection_id}",
            method=REQUEST_METHOD_GET,
        )

        return ConnectionWithDomains.model_validate(response)

    def list_connections(
        self,
        *,
        connection_type: Optional[ConnectionType] = None,
        domain: Optional[str] = None,
        organization_id: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> ConnectionsListResource:
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
        )

        return WorkOSListResource[
            ConnectionWithDomains, ConnectionsListFilters, ListMetadata
        ](
            list_method=self.list_connections,
            list_args=params,
            **ListPage[ConnectionWithDomains](**response).model_dump(),
        )

    def update_connection(
        self,
        *,
        connection_id: str,
        saml_options_signing_key: Optional[str] = None,
        saml_options_signing_cert: Optional[str] = None,
    ) -> ConnectionWithDomains:
        json = {
            "options": {
                "signing_key": saml_options_signing_key,
                "signing_cert": saml_options_signing_cert,
            }
        }

        response = self._http_client.request(
            f"connections/{connection_id}",
            method=REQUEST_METHOD_PUT,
            json=json,
        )

        return ConnectionWithDomains.model_validate(response)

    def delete_connection(self, connection_id: str) -> None:
        self._http_client.request(
            f"connections/{connection_id}", method=REQUEST_METHOD_DELETE
        )


class AsyncSSO(SSOModule):
    _http_client: AsyncHTTPClient

    def __init__(
        self, http_client: AsyncHTTPClient, client_configuration: ClientConfiguration
    ):
        self._client_configuration = client_configuration
        self._http_client = http_client

    async def get_profile(self, access_token: str) -> Profile:
        response = await self._http_client.request(
            PROFILE_PATH,
            method=REQUEST_METHOD_GET,
            headers={**self._http_client.auth_header_from_token(access_token)},
            exclude_default_auth_headers=True,
        )

        return Profile.model_validate(response)

    async def get_profile_and_token(self, code: str) -> ProfileAndToken:
        json = {
            "client_id": self._http_client.client_id,
            "client_secret": self._http_client.api_key,
            "code": code,
            "grant_type": OAUTH_GRANT_TYPE,
        }

        response = await self._http_client.request(
            TOKEN_PATH, method=REQUEST_METHOD_POST, json=json
        )

        return ProfileAndToken.model_validate(response)

    async def get_connection(self, connection_id: str) -> ConnectionWithDomains:
        response = await self._http_client.request(
            f"connections/{connection_id}",
            method=REQUEST_METHOD_GET,
        )

        return ConnectionWithDomains.model_validate(response)

    async def list_connections(
        self,
        *,
        connection_type: Optional[ConnectionType] = None,
        domain: Optional[str] = None,
        organization_id: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> ConnectionsListResource:
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
            "connections", method=REQUEST_METHOD_GET, params=params
        )

        return WorkOSListResource[
            ConnectionWithDomains, ConnectionsListFilters, ListMetadata
        ](
            list_method=self.list_connections,
            list_args=params,
            **ListPage[ConnectionWithDomains](**response).model_dump(),
        )

    async def update_connection(
        self,
        *,
        connection_id: str,
        saml_options_signing_key: Optional[str] = None,
        saml_options_signing_cert: Optional[str] = None,
    ) -> ConnectionWithDomains:
        json = {
            "options": {
                "signing_key": saml_options_signing_key,
                "signing_cert": saml_options_signing_cert,
            }
        }

        response = await self._http_client.request(
            f"connections/{connection_id}",
            method=REQUEST_METHOD_PUT,
            json=json,
        )

        return ConnectionWithDomains.model_validate(response)

    async def delete_connection(self, connection_id: str) -> None:
        await self._http_client.request(
            f"connections/{connection_id}",
            method=REQUEST_METHOD_DELETE,
        )
