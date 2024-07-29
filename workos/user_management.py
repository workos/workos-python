from requests import Request
from warnings import warn
import workos
from workos.resources.list import WorkOSListResource
from workos.resources.mfa import WorkOSAuthenticationFactorTotp, WorkOSChallenge
from workos.resources.user_management import (
    WorkOSAuthenticationResponse,
    WorkOSRefreshTokenAuthenticationResponse,
    WorkOSEmailVerification,
    WorkOSInvitation,
    WorkOSMagicAuth,
    WorkOSPasswordReset,
    WorkOSOrganizationMembership,
    WorkOSPasswordChallengeResponse,
    WorkOSUser,
)
from workos.utils.pagination_order import Order
from workos.utils.um_provider_types import UserManagementProviderType
from workos.utils.request import (
    RequestHelper,
    RESPONSE_TYPE_CODE,
    REQUEST_METHOD_POST,
    REQUEST_METHOD_GET,
    REQUEST_METHOD_DELETE,
    REQUEST_METHOD_PUT,
)
from workos.utils.validation import validate_settings, USER_MANAGEMENT_MODULE

USER_PATH = "user_management/users"
USER_DETAIL_PATH = "user_management/users/{0}"
ORGANIZATION_MEMBERSHIP_PATH = "user_management/organization_memberships"
ORGANIZATION_MEMBERSHIP_DETAIL_PATH = "user_management/organization_memberships/{0}"
ORGANIZATION_MEMBERSHIP_DEACTIVATE_PATH = (
    ORGANIZATION_MEMBERSHIP_DETAIL_PATH + "/deactivate"
)
ORGANIZATION_MEMBERSHIP_REACTIVATE_PATH = (
    ORGANIZATION_MEMBERSHIP_DETAIL_PATH + "/reactivate"
)
USER_AUTHORIZATION_PATH = "user_management/authorize"
USER_AUTHENTICATE_PATH = "user_management/authenticate"
USER_SEND_PASSWORD_RESET_PATH = "user_management/password_reset/send"
USER_RESET_PASSWORD_PATH = "user_management/password_reset/confirm"
USER_SEND_VERIFICATION_EMAIL_PATH = "user_management/users/{0}/email_verification/send"
USER_VERIFY_EMAIL_CODE_PATH = "user_management/users/{0}/email_verification/confirm"
MAGIC_AUTH_DETAIL_PATH = "user_management/magic_auth/{0}"
MAGIC_AUTH_PATH = "user_management/magic_auth"
USER_SEND_MAGIC_AUTH_PATH = "user_management/magic_auth/send"
USER_AUTH_FACTORS_PATH = "user_management/users/{0}/auth_factors"
EMAIL_VERIFICATION_DETAIL_PATH = "user_management/email_verification/{0}"
INVITATION_PATH = "user_management/invitations"
INVITATION_DETAIL_PATH = "user_management/invitations/{0}"
INVITATION_DETAIL_BY_TOKEN_PATH = "user_management/invitations/by_token/{0}"
INVITATION_REVOKE_PATH = "user_management/invitations/{0}/revoke"
PASSWORD_RESET_PATH = "user_management/password_reset"
PASSWORD_RESET_DETAIL_PATH = "user_management/password_reset/{0}"

RESPONSE_LIMIT = 10


class UserManagement(WorkOSListResource):
    """Offers methods for using the WorkOS User Management API."""

    @validate_settings(USER_MANAGEMENT_MODULE)
    def __init__(self):
        pass

    @property
    def request_helper(self):
        if not getattr(self, "_request_helper", None):
            self._request_helper = RequestHelper()
        return self._request_helper

    def get_user(self, user_id):
        """Get the details of an existing user.

        Args:
            user_id (str) - User unique identifier
        Returns:
            dict: User response from WorkOS.
        """
        headers = {}

        response = self.request_helper.request(
            USER_DETAIL_PATH.format(user_id),
            method=REQUEST_METHOD_GET,
            headers=headers,
            token=workos.api_key,
        )

        return WorkOSUser.construct_from_response(response).to_dict()

    def list_users(
        self,
        email=None,
        organization_id=None,
        limit=None,
        before=None,
        after=None,
        order=None,
    ):
        """Get a list of all of your existing users matching the criteria specified.

        Kwargs:
            email (str): Filter Users by their email. (Optional)
            organization_id (str): Filter Users by the organization they are members of. (Optional)
            limit (int): Maximum number of records to return. (Optional)
            before (str): Pagination cursor to receive records before a provided User ID. (Optional)
            after (str): Pagination cursor to receive records after a provided User ID. (Optional)
            order (Order): Sort records in either ascending or descending order by created_at timestamp: "asc" or "desc" (Optional)

        Returns:
            dict: Users response from WorkOS.
        """

        default_limit = None

        if limit is None:
            limit = RESPONSE_LIMIT
            default_limit = True

        params = {
            "email": email,
            "organization_id": organization_id,
            "limit": limit,
            "before": before,
            "after": after,
            "order": order or "desc",
        }

        if order is not None:
            if isinstance(order, Order):
                params["order"] = str(order.value)
            elif order == "asc" or order == "desc":
                params["order"] = order
            else:
                raise ValueError("Parameter order must be of enum type Order")

        response = self.request_helper.request(
            USER_PATH,
            method=REQUEST_METHOD_GET,
            params=params,
            token=workos.api_key,
        )

        response["metadata"] = {
            "params": params,
            "method": UserManagement.list_users,
        }

        if "default_limit" in locals():
            if "metadata" in response and "params" in response["metadata"]:
                response["metadata"]["params"]["default_limit"] = default_limit
            else:
                response["metadata"] = {"params": {"default_limit": default_limit}}

        return self.construct_from_response(response)

    def create_user(self, user):
        """Create a new user.

        Args:
            user (dict) - An user object
                user[email] (str) - The email address of the user.
                user[password] (str) - The password to set for the user. (Optional)
                user[password_hash] (str) - The hashed password to set for the user. Mutually exclusive with password. (Optional)
                user[password_hash_type] (str) - The algorithm originally used to hash the password, used when providing a password_hash. Valid values are 'bcrypt', `firebase-scrypt`, and `ssha`. (Optional)
                user[first_name] (str) - The user's first name. (Optional)
                user[last_name] (str) - The user's last name. (Optional)
                user[email_verified] (bool) - Whether the user's email address was previously verified. (Optional)

        Returns:
            dict: Created User response from WorkOS.
        """
        headers = {}

        response = self.request_helper.request(
            USER_PATH,
            method=REQUEST_METHOD_POST,
            params=user,
            headers=headers,
            token=workos.api_key,
        )

        return WorkOSUser.construct_from_response(response).to_dict()

    def update_user(self, user_id, payload):
        """Update user attributes.

        Args:
            user_id (str) - The User unique identifier
            payload (dict) - The User attributes to be updated
                payload[first_name] (str) - The user's first name. (Optional)
                payload[last_name] (str) - The user's last name. (Optional)
                payload[email_verified] (bool) - Whether the user's email address was previously verified. (Optional)
                payload[password] (str) - The password to set for the user. (Optional)
                payload[password_hash] (str) - The hashed password to set for the user, used when migrating from another user store. Mutually exclusive with password. (Optional)
                payload[password_hash_type] (str) - The algorithm originally used to hash the password, used when providing a password_hash. Valid values are 'bcrypt', `firebase-scrypt`, and `ssha`. (Optional)

        Returns:
            dict: Updated User response from WorkOS.
        """
        response = self.request_helper.request(
            USER_DETAIL_PATH.format(user_id),
            method=REQUEST_METHOD_PUT,
            params=payload,
            token=workos.api_key,
        )

        return WorkOSUser.construct_from_response(response).to_dict()

    def delete_user(self, user_id):
        """Delete an existing user.

        Args:
            user_id (str) -  User unique identifier
        """
        self.request_helper.request(
            USER_DETAIL_PATH.format(user_id),
            method=REQUEST_METHOD_DELETE,
            token=workos.api_key,
        )

    def create_organization_membership(self, user_id, organization_id, role_slug=None):
        """Create a new OrganizationMembership for the given Organization and User.

        Args:
            user_id: The Unique ID of the User.
            organization_id: The Unique ID of the Organization to which the user belongs to.
            role_slug: The Unique Slug of the Role to which to grant to this membership.
                If no slug is passed in, the default role will be granted.(Optional)

        Returns:
            dict: Created OrganizationMembership response from WorkOS.
        """
        headers = {}

        params = {
            "user_id": user_id,
            "organization_id": organization_id,
            "role_slug": role_slug,
        }

        response = self.request_helper.request(
            ORGANIZATION_MEMBERSHIP_PATH,
            method=REQUEST_METHOD_POST,
            params=params,
            headers=headers,
            token=workos.api_key,
        )

        return WorkOSOrganizationMembership.construct_from_response(response).to_dict()

    def update_organization_membership(
        self, organization_membership_id, role_slug=None
    ):
        """Updates an OrganizationMembership for the given id.

        Args:
            organization_membership_id (str) -  The unique ID of the Organization Membership.
            role_slug: The Unique Slug of the Role to which to grant to this membership.
                If no slug is passed in, it will not be changed (Optional)

        Returns:
            dict: Created OrganizationMembership response from WorkOS.
        """
        headers = {}

        params = {
            "role_slug": role_slug,
        }

        response = self.request_helper.request(
            ORGANIZATION_MEMBERSHIP_DETAIL_PATH.format(organization_membership_id),
            method=REQUEST_METHOD_PUT,
            params=params,
            headers=headers,
            token=workos.api_key,
        )

        return WorkOSOrganizationMembership.construct_from_response(response).to_dict()

    def get_organization_membership(self, organization_membership_id):
        """Get the details of an organization membership.

        Args:
            organization_membership_id (str) -  The unique ID of the Organization Membership.
        Returns:
            dict: OrganizationMembership response from WorkOS.
        """
        headers = {}

        response = self.request_helper.request(
            ORGANIZATION_MEMBERSHIP_DETAIL_PATH.format(organization_membership_id),
            method=REQUEST_METHOD_GET,
            headers=headers,
            token=workos.api_key,
        )

        return WorkOSOrganizationMembership.construct_from_response(response).to_dict()

    def list_organization_memberships(
        self,
        user_id=None,
        organization_id=None,
        statuses=None,
        limit=None,
        before=None,
        after=None,
        order=None,
    ):
        """Get a list of all of your existing organization memberships matching the criteria specified.

        Kwargs:
            user_id (str): Filter Organization Memberships by user. (Optional)
            organization_id (str): Filter Organization Memberships by organization. (Optional)
            statuses (list): Filter Organization Memberships by status. (Optional)
            limit (int): Maximum number of records to return. (Optional)
            before (str): Pagination cursor to receive records before a provided Organization Membership ID. (Optional)
            after (str): Pagination cursor to receive records after a provided Organization Membership ID. (Optional)
            order (Order): Sort records in either ascending or descending order by created_at timestamp: "asc" or "desc" (Optional)

        Returns:
            dict: Organization Memberships response from WorkOS.
        """

        default_limit = None

        if limit is None:
            limit = RESPONSE_LIMIT
            default_limit = True

        if statuses is not None:
            statuses = ",".join(statuses)

        params = {
            "user_id": user_id,
            "organization_id": organization_id,
            "statuses": statuses,
            "limit": limit,
            "before": before,
            "after": after,
            "order": order or "desc",
        }

        if order is not None:
            if isinstance(order, Order):
                params["order"] = str(order.value)
            elif order == "asc" or order == "desc":
                params["order"] = order
            else:
                raise ValueError("Parameter order must be of enum type Order")

        response = self.request_helper.request(
            ORGANIZATION_MEMBERSHIP_PATH,
            method=REQUEST_METHOD_GET,
            params=params,
            token=workos.api_key,
        )

        response["metadata"] = {
            "params": params,
            "method": UserManagement.list_organization_memberships,
        }

        if "default_limit" in locals():
            if "metadata" in response and "params" in response["metadata"]:
                response["metadata"]["params"]["default_limit"] = default_limit
            else:
                response["metadata"] = {"params": {"default_limit": default_limit}}

        return self.construct_from_response(response)

    def delete_organization_membership(self, organization_membership_id):
        """Delete an existing organization membership.

        Args:
            organization_membership_id (str) -  The unique ID of the Organization Membership.
        """
        self.request_helper.request(
            ORGANIZATION_MEMBERSHIP_DETAIL_PATH.format(organization_membership_id),
            method=REQUEST_METHOD_DELETE,
            token=workos.api_key,
        )

    def deactivate_organization_membership(self, organization_membership_id):
        """Deactivate an organization membership.

        Args:
            organization_membership_id (str) -  The unique ID of the Organization Membership.
        Returns:
            dict: OrganizationMembership response from WorkOS.
        """
        response = self.request_helper.request(
            ORGANIZATION_MEMBERSHIP_DEACTIVATE_PATH.format(organization_membership_id),
            method=REQUEST_METHOD_PUT,
            token=workos.api_key,
        )

        return WorkOSOrganizationMembership.construct_from_response(response).to_dict()

    def reactivate_organization_membership(self, organization_membership_id):
        """Reactivates an organization membership.

        Args:
            organization_membership_id (str) -  The unique ID of the Organization Membership.
        Returns:
            dict: OrganizationMembership response from WorkOS.
        """
        response = self.request_helper.request(
            ORGANIZATION_MEMBERSHIP_REACTIVATE_PATH.format(organization_membership_id),
            method=REQUEST_METHOD_PUT,
            token=workos.api_key,
        )

        return WorkOSOrganizationMembership.construct_from_response(response).to_dict()

    def get_authorization_url(
        self,
        redirect_uri,
        connection_id=None,
        organization_id=None,
        provider=None,
        domain_hint=None,
        login_hint=None,
        state=None,
        code_challenge=None,
    ):
        """Generate an OAuth 2.0 authorization URL.

        The URL generated will redirect a User to the Identity Provider configured through
        WorkOS.

        Kwargs:
            redirect_uri (str) - A Redirect URI to return an authorized user to.
            connection_id (str) - The connection_id connection selector is used to initiate SSO for a Connection.
                The value of this parameter should be a WorkOS Connection ID. (Optional)
            organization_id (str) - The organization_id connection selector is used to initiate SSO for an Organization.
                The value of this parameter should be a WorkOS Organization ID. (Optional)
            provider (UserManagementProviderType) - The provider connection selector is used to initiate SSO using an OAuth-compatible provider.
                Currently, the supported values for provider are 'authkit', 'AppleOAuth', 'GitHubOAuth, 'GoogleOAuth', and 'MicrosoftOAuth'. (Optional)
            domain_hint (str) - Can be used to pre-fill the domain field when initiating authentication with Microsoft OAuth,
                or with a GoogleSAML connection type. (Optional)
            login_hint (str) - Can be used to pre-fill the username/email address field of the IdP sign-in page for the user,
                if you know their username ahead of time. Currently, this parameter is supported for OAuth, OpenID Connect,
                OktaSAML, and AzureSAML connection types. (Optional)
            state (str) - An encoded string passed to WorkOS that'd be preserved through the authentication workflow, passed
                back as a query parameter. (Optional)
            code_challenge (str) - Code challenge is derived from the code verifier used for the PKCE flow. (Optional)

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
                "Incomplete arguments. Need to specify either a 'connection_id', 'organization_id', or 'provider_id'"
            )

        if connection_id is not None:
            params["connection_id"] = connection_id
        if organization_id is not None:
            params["organization_id"] = organization_id
        if provider is not None:
            if not isinstance(provider, UserManagementProviderType):
                raise ValueError(
                    "'provider' must be of type UserManagementProviderType"
                )

            params["provider"] = provider.value
        if domain_hint is not None:
            params["domain_hint"] = domain_hint
        if login_hint is not None:
            params["login_hint"] = login_hint
        if state is not None:
            params["state"] = state
        if code_challenge:
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"

        prepared_request = Request(
            "GET",
            self.request_helper.generate_api_url(USER_AUTHORIZATION_PATH),
            params=params,
        ).prepare()

        return prepared_request.url

    def authenticate_with_password(
        self,
        email,
        password,
        ip_address=None,
        user_agent=None,
    ):
        """Authenticates a user with email and password.

        Kwargs:
            email (str): The email address of the user.
            password (str): The password of the user.
            ip_address (str): The IP address of the request from the user who is attempting to authenticate. (Optional)
            user_agent (str): The user agent of the request from the user who is attempting to authenticate. (Optional)

        Returns:
            (dict): Authentication response from WorkOS.
                [user] (dict): User response from WorkOS
                [organization_id] (str): The Organization the user selected to sign in for, if applicable.
        """

        headers = {}

        payload = {
            "client_id": workos.client_id,
            "client_secret": workos.api_key,
            "email": email,
            "password": password,
            "grant_type": "password",
        }

        if ip_address:
            payload["ip_address"] = ip_address

        if user_agent:
            payload["user_agent"] = user_agent

        response = self.request_helper.request(
            USER_AUTHENTICATE_PATH,
            method=REQUEST_METHOD_POST,
            headers=headers,
            params=payload,
        )

        return WorkOSAuthenticationResponse.construct_from_response(response).to_dict()

    def authenticate_with_code(
        self,
        code,
        code_verifier=None,
        ip_address=None,
        user_agent=None,
    ):
        """Authenticates an OAuth user or a user that is logging in through SSO.

        Kwargs:
            code (str): The authorization value which was passed back as a query parameter in the callback to the Redirect URI.
            code_verifier (str): The randomly generated string used to derive the code challenge that was passed to the authorization
                url as part of the PKCE flow. This parameter is required when the client secret is not present. (Optional)
            ip_address (str): The IP address of the request from the user who is attempting to authenticate. (Optional)
            user_agent (str): The user agent of the request from the user who is attempting to authenticate. (Optional)

        Returns:
            (dict): Authentication response from WorkOS.
                [user] (dict): User response from WorkOS
                [organization_id] (str): The Organization the user selected to sign in for, if applicable.
        """

        headers = {}

        payload = {
            "client_id": workos.client_id,
            "client_secret": workos.api_key,
            "code": code,
            "grant_type": "authorization_code",
        }

        if ip_address:
            payload["ip_address"] = ip_address

        if user_agent:
            payload["user_agent"] = user_agent

        if code_verifier:
            payload["code_verifier"] = code_verifier

        response = self.request_helper.request(
            USER_AUTHENTICATE_PATH,
            method=REQUEST_METHOD_POST,
            headers=headers,
            params=payload,
        )

        return WorkOSAuthenticationResponse.construct_from_response(response).to_dict()

    def authenticate_with_magic_auth(
        self,
        code,
        email,
        link_authorization_code=None,
        ip_address=None,
        user_agent=None,
    ):
        """Authenticates a user by verifying a one-time code sent to the user's email address by the Magic Auth Send Code endpoint.

        Kwargs:
            code (str): The one-time code that was emailed to the user.
            email (str): The email of the User who will be authenticated.
            link_authorization_code (str): An authorization code used in a previous authenticate request that resulted in an existing user error response. (Optional)
            ip_address (str): The IP address of the request from the user who is attempting to authenticate. (Optional)
            user_agent (str): The user agent of the request from the user who is attempting to authenticate. (Optional)

        Returns:
            (dict): Authentication response from WorkOS.
                [user] (dict): User response from WorkOS
                [organization_id] (str): The Organization the user selected to sign in for, if applicable.
        """

        headers = {}

        payload = {
            "client_id": workos.client_id,
            "client_secret": workos.api_key,
            "code": code,
            "email": email,
            "grant_type": "urn:workos:oauth:grant-type:magic-auth:code",
        }

        if link_authorization_code:
            payload["link_authorization_code"] = link_authorization_code

        if ip_address:
            payload["ip_address"] = ip_address

        if user_agent:
            payload["user_agent"] = user_agent

        response = self.request_helper.request(
            USER_AUTHENTICATE_PATH,
            method=REQUEST_METHOD_POST,
            headers=headers,
            params=payload,
        )

        return WorkOSAuthenticationResponse.construct_from_response(response).to_dict()

    def authenticate_with_email_verification(
        self,
        code,
        pending_authentication_token,
        ip_address=None,
        user_agent=None,
    ):
        """Authenticates a user that requires email verification by verifying a one-time code sent to the user's email address and the pending authentication token.

        Kwargs:
            code (str): The one-time code that was emailed to the user.
            pending_authentication_token (str): The token returned from an authentication attempt due to an unverified email address.
            ip_address (str): The IP address of the request from the user who is attempting to authenticate. (Optional)
            user_agent (str): The user agent of the request from the user who is attempting to authenticate. (Optional)

        Returns:
            (dict): Authentication response from WorkOS.
                [user] (dict): User response from WorkOS
                [organization_id] (str): The Organization the user selected to sign in for, if applicable.
        """

        headers = {}

        payload = {
            "client_id": workos.client_id,
            "client_secret": workos.api_key,
            "code": code,
            "pending_authentication_token": pending_authentication_token,
            "grant_type": "urn:workos:oauth:grant-type:email-verification:code",
        }

        if ip_address:
            payload["ip_address"] = ip_address

        if user_agent:
            payload["user_agent"] = user_agent

        response = self.request_helper.request(
            USER_AUTHENTICATE_PATH,
            method=REQUEST_METHOD_POST,
            headers=headers,
            params=payload,
        )

        return WorkOSAuthenticationResponse.construct_from_response(response).to_dict()

    def authenticate_with_totp(
        self,
        code,
        authentication_challenge_id,
        pending_authentication_token,
        ip_address=None,
        user_agent=None,
    ):
        """Authenticates a user that has MFA enrolled by verifying the TOTP code, the Challenge from the Factor, and the pending authentication token.

        Kwargs:
            code (str): The time-based-one-time-password generated by the Factor that was challenged.
            authentication_challenge_id (str): The unique ID of the authentication Challenge created for the TOTP Factor for which the user is enrolled.
            pending_authentication_token (str): The token returned from a failed authentication attempt due to MFA challenge.
            ip_address (str): The IP address of the request from the user who is attempting to authenticate. (Optional)
            user_agent (str): The user agent of the request from the user who is attempting to authenticate. (Optional)

        Returns:
            (dict): Authentication response from WorkOS.
                [user] (dict): User response from WorkOS
                [organization_id] (str): The Organization the user selected to sign in for, if applicable.
        """

        headers = {}

        payload = {
            "client_id": workos.client_id,
            "client_secret": workos.api_key,
            "code": code,
            "authentication_challenge_id": authentication_challenge_id,
            "pending_authentication_token": pending_authentication_token,
            "grant_type": "urn:workos:oauth:grant-type:mfa-totp",
        }

        if ip_address:
            payload["ip_address"] = ip_address

        if user_agent:
            payload["user_agent"] = user_agent

        response = self.request_helper.request(
            USER_AUTHENTICATE_PATH,
            method=REQUEST_METHOD_POST,
            headers=headers,
            params=payload,
        )

        return WorkOSAuthenticationResponse.construct_from_response(response).to_dict()

    def authenticate_with_organization_selection(
        self,
        organization_id,
        pending_authentication_token,
        ip_address=None,
        user_agent=None,
    ):
        """Authenticates a user that is a member of multiple organizations by verifying the organization ID and the pending authentication token.

        Kwargs:
            organization_id (str): The time-based-one-time-password generated by the Factor that was challenged.
            pending_authentication_token (str): The token returned from a failed authentication attempt due to organization selection being required.
            ip_address (str): The IP address of the request from the user who is attempting to authenticate. (Optional)
            user_agent (str): The user agent of the request from the user who is attempting to authenticate. (Optional)

        Returns:
            (dict): Authentication response from WorkOS.
                [user] (dict): User response from WorkOS
                [organization_id] (str): The Organization the user selected to sign in for, if applicable.
        """

        headers = {}

        payload = {
            "client_id": workos.client_id,
            "client_secret": workos.api_key,
            "organization_id": organization_id,
            "pending_authentication_token": pending_authentication_token,
            "grant_type": "urn:workos:oauth:grant-type:organization-selection",
        }

        if ip_address:
            payload["ip_address"] = ip_address

        if user_agent:
            payload["user_agent"] = user_agent

        response = self.request_helper.request(
            USER_AUTHENTICATE_PATH,
            method=REQUEST_METHOD_POST,
            headers=headers,
            params=payload,
        )

        return WorkOSAuthenticationResponse.construct_from_response(response).to_dict()

    def authenticate_with_refresh_token(
        self,
        refresh_token,
        organization_id=None,
        ip_address=None,
        user_agent=None,
    ):
        """Authenticates a user with a refresh token.

        Kwargs:
            refresh_token (str): The token associated to the user.
            organization_id (str): The organization to issue the new access token for. (Optional)
            ip_address (str): The IP address of the request from the user who is attempting to authenticate. (Optional)
            user_agent (str): The user agent of the request from the user who is attempting to authenticate. (Optional)

        Returns:
            (dict): Refresh Token Authentication response from WorkOS.
                [access_token] (str): The refreshed access token
                [refresh_token] (str): The new refresh token.
        """

        headers = {}

        payload = {
            "client_id": workos.client_id,
            "client_secret": workos.api_key,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        if organization_id:
            payload["organization_id"] = organization_id

        if ip_address:
            payload["ip_address"] = ip_address

        if user_agent:
            payload["user_agent"] = user_agent

        response = self.request_helper.request(
            USER_AUTHENTICATE_PATH,
            method=REQUEST_METHOD_POST,
            headers=headers,
            params=payload,
        )

        return WorkOSRefreshTokenAuthenticationResponse.construct_from_response(
            response
        ).to_dict()

    def get_jwks_url(self):
        """Get the public key that is used for verifying access tokens.

        Returns:
            (str): The public JWKS URL.
        """

        return "%ssso/jwks/%s" % (workos.base_api_url, workos.client_id)

    def get_logout_url(self, session_id):
        """Get the URL for ending the session and redirecting the user

        Kwargs:
            session_id (str): The ID of the user's session

        Returns:
            (str): URL to redirect the user to to end the session.
        """

        return "%suser_management/sessions/logout?session_id=%s" % (
            workos.base_api_url,
            session_id,
        )

    def get_password_reset(self, password_reset_id):
        """Get the details of a password reset object.

        Args:
            password_reset_id (str) -  The unique ID of the password reset object.

        Returns:
            dict: PasswordReset response from WorkOS.
        """
        headers = {}

        response = self.request_helper.request(
            PASSWORD_RESET_DETAIL_PATH.format(password_reset_id),
            method=REQUEST_METHOD_GET,
            headers=headers,
            token=workos.api_key,
        )

        return WorkOSPasswordReset.construct_from_response(response).to_dict()

    def create_password_reset(
        self,
        email,
    ):
        """Creates a password reset token that can be sent to a user's email to reset the password.

        Args:
            email: The email address of the user.

        Returns:
            dict: PasswordReset response from WorkOS.
        """
        headers = {}

        params = {
            "email": email,
        }

        response = self.request_helper.request(
            PASSWORD_RESET_PATH,
            method=REQUEST_METHOD_POST,
            params=params,
            headers=headers,
            token=workos.api_key,
        )

        return WorkOSPasswordReset.construct_from_response(response).to_dict()

    def send_password_reset_email(
        self,
        email,
        password_reset_url,
    ):
        """Sends a password reset email to a user.

        Deprecated: Please use `create_password_reset` instead. This method will be removed in a future major version.

        Kwargs:
            email (str): The email of the user that wishes to reset their password.
            password_reset_url (str): The URL that will be linked to in the email.
        """

        warn(
            "'send_password_reset_email' is deprecated. Please use 'create_password_reset' instead. This method will be removed in a future major version.",
            DeprecationWarning,
        )

        headers = {}

        payload = {
            "email": email,
            "password_reset_url": password_reset_url,
        }

        self.request_helper.request(
            USER_SEND_PASSWORD_RESET_PATH,
            method=REQUEST_METHOD_POST,
            headers=headers,
            params=payload,
            token=workos.api_key,
        )

    def reset_password(
        self,
        token,
        new_password,
    ):
        """Resets user password using token that was sent to the user.

        Kwargs:
            token (str): The reset token emailed to the user.
            new_password (str): The new password to be set for the user.

        Returns:
            dict: User response from WorkOS.
        """

        headers = {}

        payload = {
            "token": token,
            "new_password": new_password,
        }

        response = self.request_helper.request(
            USER_RESET_PASSWORD_PATH,
            method=REQUEST_METHOD_POST,
            headers=headers,
            params=payload,
            token=workos.api_key,
        )

        return WorkOSUser.construct_from_response(response["user"]).to_dict()

    def get_email_verification(self, email_verification_id):
        """Get the details of an email verification object.

        Args:
            email_verificationh_id (str) -  The unique ID of the email verification object.

        Returns:
            dict: EmailVerification response from WorkOS.
        """
        headers = {}

        response = self.request_helper.request(
            EMAIL_VERIFICATION_DETAIL_PATH.format(email_verification_id),
            method=REQUEST_METHOD_GET,
            headers=headers,
            token=workos.api_key,
        )

        return WorkOSEmailVerification.construct_from_response(response).to_dict()

    def send_verification_email(
        self,
        user_id,
    ):
        """Sends a verification email to the provided user.

        Kwargs:
            user_id (str): The unique ID of the User whose email address will be verified.

        Returns:
            dict: User response from WorkOS.
        """

        headers = {}

        response = self.request_helper.request(
            USER_SEND_VERIFICATION_EMAIL_PATH.format(user_id),
            method=REQUEST_METHOD_POST,
            headers=headers,
            token=workos.api_key,
        )

        return WorkOSUser.construct_from_response(response["user"]).to_dict()

    def verify_email(
        self,
        user_id,
        code,
    ):
        """Verifies user email using one-time code that was sent to the user.

        Kwargs:
            user_id (str): The unique ID of the User whose email address will be verified.

            code (str): The one-time code emailed to the user.

        Returns:
            dict: User response from WorkOS.
        """

        headers = {}

        payload = {
            "code": code,
        }

        response = self.request_helper.request(
            USER_VERIFY_EMAIL_CODE_PATH.format(user_id),
            method=REQUEST_METHOD_POST,
            headers=headers,
            params=payload,
            token=workos.api_key,
        )

        return WorkOSUser.construct_from_response(response["user"]).to_dict()

    def get_magic_auth(self, magic_auth_id):
        """Get the details of a Magic Auth object.

        Args:
            magic_auth_id (str) -  The unique ID of the Magic Auth object.

        Returns:
            dict: MagicAuth response from WorkOS.
        """
        headers = {}

        response = self.request_helper.request(
            MAGIC_AUTH_DETAIL_PATH.format(magic_auth_id),
            method=REQUEST_METHOD_GET,
            headers=headers,
            token=workos.api_key,
        )

        return WorkOSMagicAuth.construct_from_response(response).to_dict()

    def create_magic_auth(
        self,
        email,
        invitation_token=None,
    ):
        """Creates a Magic Auth code challenge that can be sent to a user's email for authentication.

        Args:
            email: The email address of the user.
            invitation_token: The token of an Invitation, if required. (Optional)

        Returns:
            dict: MagicAuth response from WorkOS.
        """
        headers = {}

        params = {
            "email": email,
            "invitation_token": invitation_token,
        }

        response = self.request_helper.request(
            MAGIC_AUTH_PATH,
            method=REQUEST_METHOD_POST,
            params=params,
            headers=headers,
            token=workos.api_key,
        )

        return WorkOSMagicAuth.construct_from_response(response).to_dict()

    def send_magic_auth_code(
        self,
        email,
    ):
        """Creates a one-time Magic Auth code and emails it to the user.

        Deprecated: Please use `create_magic_auth` instead. This method will be removed in a future major version.

        Kwargs:
            email (str): The email address the one-time code will be sent to.
        """

        warn(
            "'send_magic_auth_code' is deprecated. Please use 'create_magic_auth' instead. This method will be removed in a future major version.",
            DeprecationWarning,
        )

        headers = {}

        payload = {
            "email": email,
        }

        response = self.request_helper.request(
            USER_SEND_MAGIC_AUTH_PATH,
            method=REQUEST_METHOD_POST,
            headers=headers,
            params=payload,
            token=workos.api_key,
        )

    def enroll_auth_factor(
        self,
        user_id,
        type,
        totp_issuer=None,
        totp_user=None,
        totp_secret=None,
    ):
        """Enrolls a user in a new auth factor.

        Kwargs:
            user_id (str): The unique ID of the User to be enrolled in the auth factor.
            type (str): The type of factor to enroll (Only option available is 'totp').
            totp_issuer (str): Name of the Organization (Optional)
            totp_user (str): Email of user (Optional)
            totp_secret (str): The secret key for the TOTP factor. Generated if not provided. (Optional)

        Returns: { WorkOSAuthenticationFactorTotp, WorkOSChallenge}
        """

        if type not in ["totp"]:
            raise ValueError("Type parameter must be 'totp'")

        headers = {}

        payload = {
            "type": type,
            "totp_issuer": totp_issuer,
            "totp_user": totp_user,
            "totp_secret": totp_secret,
        }

        response = self.request_helper.request(
            USER_AUTH_FACTORS_PATH.format(user_id),
            method=REQUEST_METHOD_POST,
            headers=headers,
            params=payload,
            token=workos.api_key,
        )

        factor_and_challenge = {}
        factor_and_challenge[
            "authentication_factor"
        ] = WorkOSAuthenticationFactorTotp.construct_from_response(
            response["authentication_factor"]
        ).to_dict()

        factor_and_challenge[
            "authentication_challenge"
        ] = WorkOSChallenge.construct_from_response(
            response["authentication_challenge"]
        ).to_dict()

        return factor_and_challenge

    def list_auth_factors(
        self,
        user_id,
    ):
        """Lists the Auth Factors for a user.

        Kwargs:
            user_id (str): The unique ID of the User to list the auth factors for.

        Returns:
            dict: List of Authentication Factors for a User from WorkOS.
        """
        response = self.request_helper.request(
            USER_AUTH_FACTORS_PATH.format(user_id),
            method=REQUEST_METHOD_GET,
            token=workos.api_key,
        )

        response["metadata"] = {
            "params": {
                "user_id": user_id,
            },
            "method": UserManagement.list_auth_factors,
        }

        return self.construct_from_response(response)

    def get_invitation(self, invitation_id):
        """Get the details of an invitation.

        Args:
            invitation_id (str) -  The unique ID of the Invitation.

        Returns:
            dict: Invitation response from WorkOS.
        """
        headers = {}

        response = self.request_helper.request(
            INVITATION_DETAIL_PATH.format(invitation_id),
            method=REQUEST_METHOD_GET,
            headers=headers,
            token=workos.api_key,
        )

        return WorkOSInvitation.construct_from_response(response).to_dict()

    def find_invitation_by_token(self, invitation_token):
        """Get the details of an invitation.

        Args:
            invitation_token (str) -  The token of the Invitation.

        Returns:
            dict: Invitation response from WorkOS.
        """
        headers = {}

        response = self.request_helper.request(
            INVITATION_DETAIL_BY_TOKEN_PATH.format(invitation_token),
            method=REQUEST_METHOD_GET,
            headers=headers,
            token=workos.api_key,
        )

        return WorkOSInvitation.construct_from_response(response).to_dict()

    def list_invitations(
        self,
        email=None,
        organization_id=None,
        limit=None,
        before=None,
        after=None,
        order=None,
    ):
        """Get a list of all of your existing invitations matching the criteria specified.

        Kwargs:
            email (str): Filter Invitations by email. (Optional)
            organization_id (str): Filter Invitations by organization. (Optional)
            limit (int): Maximum number of records to return. (Optional)
            before (str): Pagination cursor to receive records before a provided Invitation ID. (Optional)
            after (str): Pagination cursor to receive records after a provided Invitation ID. (Optional)
            order (Order): Sort records in either ascending or descending order by created_at timestamp: "asc" or "desc" (Optional)

        Returns:
            dict: Users response from WorkOS.
        """

        default_limit = None

        if limit is None:
            limit = RESPONSE_LIMIT
            default_limit = True

        params = {
            "email": email,
            "organization_id": organization_id,
            "limit": limit,
            "before": before,
            "after": after,
            "order": order or "desc",
        }

        if order is not None:
            if isinstance(order, Order):
                params["order"] = str(order.value)
            elif order == "asc" or order == "desc":
                params["order"] = order
            else:
                raise ValueError("Parameter order must be of enum type Order")

        response = self.request_helper.request(
            INVITATION_PATH,
            method=REQUEST_METHOD_GET,
            params=params,
            token=workos.api_key,
        )

        response["metadata"] = {
            "params": params,
            "method": UserManagement.list_invitations,
        }

        if "default_limit" in locals():
            if "metadata" in response and "params" in response["metadata"]:
                response["metadata"]["params"]["default_limit"] = default_limit
            else:
                response["metadata"] = {"params": {"default_limit": default_limit}}

        return self.construct_from_response(response)

    def send_invitation(
        self,
        email,
        organization_id=None,
        expires_in_days=None,
        inviter_user_id=None,
        role_slug=None,
    ):
        """Sends an Invitation to a recipient.

        Args:
            email: The email address of the recipient.
            organization_id: The ID of the Organization to which the recipient is being invited. (Optional)
            expires_in_days: The number of days the invitations will be valid for. Must be between 1 and 30, defaults to 7 if not specified. (Optional)
            inviter_user_id: The ID of the User sending the invitation. (Optional)
            role_slug: The unique slug of the Role to give the Membership once the invite is accepted (Optional)

        Returns:
            dict: Sent Invitation response from WorkOS.
        """
        headers = {}

        params = {
            "email": email,
            "organization_id": organization_id,
            "expires_in_days": expires_in_days,
            "inviter_user_id": inviter_user_id,
            "role_slug": role_slug,
        }

        response = self.request_helper.request(
            INVITATION_PATH,
            method=REQUEST_METHOD_POST,
            params=params,
            headers=headers,
            token=workos.api_key,
        )

        return WorkOSInvitation.construct_from_response(response).to_dict()

    def revoke_invitation(self, invitation_id):
        """Revokes an existing Invitation.

        Args:
            invitation_id (str) -  The unique ID of the Invitation.

        Returns:
            dict: Invitation response from WorkOS.
        """
        headers = {}

        response = self.request_helper.request(
            INVITATION_REVOKE_PATH.format(invitation_id),
            method=REQUEST_METHOD_POST,
            headers=headers,
            token=workos.api_key,
        )

        return WorkOSInvitation.construct_from_response(response).to_dict()
