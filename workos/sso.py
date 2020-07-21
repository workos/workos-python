import json

from requests import Request
from warnings import warn

import workos
from workos.exceptions import ConfigurationException
from workos.resources.sso import WorkOSProfile
from workos.utils.connection_types import ConnectionType
from workos.utils.request import RequestHelper, RESPONSE_TYPE_CODE, REQUEST_METHOD_POST
from workos.utils.validation import SSO_MODULE, validate_settings

AUTHORIZATION_PATH = "sso/authorize"
CREATE_CONNECTION_PATH = "connections"
PROMOTE_DRAFT_CONNECTION_PATH = "draft_connections/%s/activate"
TOKEN_PATH = "sso/token"

OAUTH_GRANT_TYPE = "authorization_code"


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
        self, domain=None, redirect_uri=None, state=None, provider=None
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

        Returns:
            str: URL to redirect a User to to begin the OAuth workflow with WorkOS
        """
        params = {
            "client_id": workos.project_id,
            "redirect_uri": redirect_uri,
            "response_type": RESPONSE_TYPE_CODE,
        }

        if domain is None and provider is None:
            raise ValueError(
                "Incomplete arguments. Need to specify either a 'domain' or 'provider'"
            )
        if provider is not None:
            if not isinstance(provider, ConnectionType):
                raise ValueError("'provider' must be of type ConnectionType")
            params["provider"] = str(provider.value)
        if domain is not None:
            params["domain"] = domain

        if state is not None:
            params["state"] = state

        prepared_request = Request(
            "GET",
            self.request_helper.generate_api_url(AUTHORIZATION_PATH),
            params=params,
        ).prepare()

        return prepared_request.url

    def get_profile(self, code):
        """Get the profile of an authenticated User

        Once authenticated, using the code returned having followed the authorization URL,
        get the WorkOS profile of the User.

        Args:
            code (str): Code returned by WorkOS on completion of OAuth 2.0 workflow

        Returns:
            WorkOSProfile: WorkOSProfile object representing the User
        """
        params = {
            "client_id": workos.project_id,
            "client_secret": workos.api_key,
            "code": code,
            "grant_type": OAUTH_GRANT_TYPE,
        }

        response = self.request_helper.request(
            TOKEN_PATH, method=REQUEST_METHOD_POST, params=params
        )

        return WorkOSProfile.construct_from_response(response["profile"])

    def promote_draft_connection(self, token):
        """Promote a Draft Connection

        Promotes a Draft Connection created through the WorkOS.js embed. A Draft Connection that has
        been promoted will enable Enterprise users of the domain to begin signing in via SSO.

        Args:
            token (str): The token supplied via the response when a draft connection is created via 
            the WorkOS.js embed

        Returns:
            bool: True if a Draft Connection has been successfully promoted
        """
        warn(
            "'promote_draft_connection' is deprecated. Use 'create_connection' instead.",
            DeprecationWarning,
        )
        self.request_helper.request(
            PROMOTE_DRAFT_CONNECTION_PATH % token,
            method=REQUEST_METHOD_POST,
            token=workos.api_key,
        )

        return True

    def create_connection(self, source):
        """Activates a Draft Connection created through the WorkOS.js widget.

        Args:
            source (str): Draft Connection identifier.

        Returns:
            dict: Created Connection response from WorkOS.
        """
        params = {"source": source}
        return self.request_helper.request(
            CREATE_CONNECTION_PATH,
            method=REQUEST_METHOD_POST,
            params=params,
            token=workos.api_key,
        )
