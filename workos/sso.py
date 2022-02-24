import json

from requests import Request
from warnings import warn

import workos
from workos.exceptions import ConfigurationException
from workos.resources.sso import WorkOSProfile, WorkOSProfileAndToken
from workos.utils.connection_types import ConnectionType
from workos.utils.request import (
    RequestHelper,
    RESPONSE_TYPE_CODE,
    REQUEST_METHOD_DELETE,
    REQUEST_METHOD_GET,
    REQUEST_METHOD_POST,
)
from workos.utils.validation import SSO_MODULE, validate_settings

AUTHORIZATION_PATH = "sso/authorize"
TOKEN_PATH = "sso/token"
PROFILE_PATH = "sso/profile"

OAUTH_GRANT_TYPE = "authorization_code"

RESPONSE_LIMIT = 10


class SSO(object):
    """Offers methods to assist in authenticating through the WorkOS SSO service."""

    @validate_settings(SSO_MODULE)
    def __init__(self):
        pass

    @property
    def request_helper(self):
        if not getattr(self, "_request_helper", None):
            self._request_helper = RequestHelper()
        return self._request_helper

    def get_authorization_url(
        self,
        domain=None,
        domain_hint=None,
        login_hint=None,
        redirect_uri=None,
        state=None,
        provider=None,
        connection=None,
        organization=None,
    ):
        """Generate an OAuth 2.0 authorization URL.

        The URL generated will redirect a User to the Identity Provider configured through
        WorkOS.

        Kwargs:
            domain (str) - The domain a user is associated with, as configured on WorkOS
            redirect_uri (str) - A valid redirect URI, as specified on WorkOS
            state (str) - An encoded string passed to WorkOS that'd be preserved through the authentication workflow, passed
            back as a query parameter
            provider (ConnectionType) - Authentication service provider descriptor
            connection (string) - Unique identifier for a WorkOS Connection
            organization (string) - Unique identifier for a WorkOS Organization

        Returns:
            str: URL to redirect a User to to begin the OAuth workflow with WorkOS
        """
        params = {
            "client_id": workos.client_id,
            "redirect_uri": redirect_uri,
            "response_type": RESPONSE_TYPE_CODE,
        }

        if (
            domain is None
            and provider is None
            and connection is None
            and organization is None
        ):
            raise ValueError(
                "Incomplete arguments. Need to specify either a 'connection', 'organization', 'domain', or 'provider'"
            )
        if provider is not None:
            if not isinstance(provider, ConnectionType):
                raise ValueError("'provider' must be of type ConnectionType")
            params["provider"] = str(provider.value)
        if domain is not None:
            warn(
                "The 'domain' parameter for 'get_authorization_url' is deprecated. Please use 'organization' instead.",
                DeprecationWarning,
            )
            params["domain"] = domain
        if domain_hint is not None:
            params["domain_hint"] = domain_hint
        if login_hint is not None:
            params["login_hint"] = login_hint
        if connection is not None:
            params["connection"] = connection
        if organization is not None:
            params["organization"] = organization

        if state is not None:
            params["state"] = state

        if redirect_uri is None:
            raise ValueError("Incomplete arguments. Need to specify a 'redirect_uri'.")

        prepared_request = Request(
            "GET",
            self.request_helper.generate_api_url(AUTHORIZATION_PATH),
            params=params,
        ).prepare()

        return prepared_request.url

    def get_profile(self, accessToken):
        """
        Verify that SSO has been completed successfully and retrieve the identity of the user.

        Args:
            accessToken (str): the token used to authenticate the API call

        Returns:
            WorkOSProfile
        """

        token = accessToken

        response = self.request_helper.request(
            PROFILE_PATH, method=REQUEST_METHOD_GET, token=token
        )

        return WorkOSProfile.construct_from_response(response)

    def get_profile_and_token(self, code):
        """Get the profile of an authenticated User

        Once authenticated, using the code returned having followed the authorization URL,
        get the WorkOS profile of the User.

        Args:
            code (str): Code returned by WorkOS on completion of OAuth 2.0 workflow

        Returns:
            WorkOSProfileAndToken: WorkOSProfileAndToken object representing the User
        """
        params = {
            "client_id": workos.client_id,
            "client_secret": workos.api_key,
            "code": code,
            "grant_type": OAUTH_GRANT_TYPE,
        }

        response = self.request_helper.request(
            TOKEN_PATH, method=REQUEST_METHOD_POST, params=params
        )

        return WorkOSProfileAndToken.construct_from_response(response)

    def get_connection(self, connection):
        """Gets details for a single Connection

        Args:
            connection (str): Connection unique identifier

        Returns:
            dict: Connection response from WorkOS.
        """
        return self.request_helper.request(
            "connections/{connection}".format(connection=connection),
            method=REQUEST_METHOD_GET,
            token=workos.api_key,
        )

    def list_connections(
        self,
        connection_type=None,
        domain=None,
        organization_id=None,
        limit=RESPONSE_LIMIT,
        before=None,
        after=None,
    ):
        """Gets details for existing Connections.

        Args:
            connection_type (ConnectionType): Authentication service provider descriptor. (Optional)
            domain (str): Domain of a Connection. (Optional)
            limit (int): Maximum number of records to return. (Optional)
            before (str): Pagination cursor to receive records before a provided Connection ID. (Optional)
            after (str): Pagination cursor to receive records after a provided Connection ID. (Optional)

        Returns:
            dict: Connections response from WorkOS.
        """

        # This method used to accept `connection_type` as a string, so we try
        # to convert strings to a `ConnectionType` to support existing callers.
        #
        # TODO: Remove support for string values of `ConnectionType` in the next
        #       major version.
        if connection_type is not None and isinstance(connection_type, str):
            try:
                connection_type = ConnectionType[connection_type]

                warn(
                    "Passing a string value as the 'connection_type' parameter for 'list_connections' is deprecated and will be removed in the next major version. Please pass a 'ConnectionType' instead.",
                    DeprecationWarning,
                )
            except KeyError:
                raise ValueError("'connection_type' must be a member of ConnectionType")

        params = {
            "connection_type": (
                connection_type.value if connection_type is not None else None
            ),
            "domain": domain,
            "organization_id": organization_id,
            "limit": limit,
            "before": before,
            "after": after,
        }
        return self.request_helper.request(
            "connections",
            method=REQUEST_METHOD_GET,
            params=params,
            token=workos.api_key,
        )

    def delete_connection(self, connection):
        """Deletes a single Connection

        Args:
            connection (str): Connection unique identifier
        """
        return self.request_helper.request(
            "connections/{connection}".format(connection=connection),
            method=REQUEST_METHOD_DELETE,
            token=workos.api_key,
        )
