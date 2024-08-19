from typing import Optional, Protocol, Sequence, Set, Type
from workos._client_configuration import ClientConfiguration
from workos.types.list_resource import (
    ListArgs,
    ListMetadata,
    ListPage,
    WorkOSListResource,
)
from workos.types.mfa import (
    AuthenticationFactor,
    AuthenticationFactorTotpAndChallengeResponse,
    AuthenticationFactorType,
)
from workos.types.user_management import (
    AuthenticationResponse,
    EmailVerification,
    Invitation,
    MagicAuth,
    OrganizationMembership,
    OrganizationMembershipStatus,
    PasswordReset,
    RefreshTokenAuthenticationResponse,
    User,
)
from workos.types.user_management.authenticate_with_common import (
    AuthenticateWithCodeParameters,
    AuthenticateWithEmailVerificationParameters,
    AuthenticateWithMagicAuthParameters,
    AuthenticateWithOrganizationSelectionParameters,
    AuthenticateWithParameters,
    AuthenticateWithPasswordParameters,
    AuthenticateWithRefreshTokenParameters,
    AuthenticateWithTotpParameters,
)
from workos.types.user_management.authentication_response import (
    AuthKitAuthenticationResponse,
    AuthenticationResponseType,
)
from workos.types.user_management.list_filters import (
    AuthenticationFactorsListFilters,
    InvitationsListFilters,
    OrganizationMembershipsListFilters,
    UsersListFilters,
)
from workos.types.user_management.password_hash_type import PasswordHashType
from workos.types.user_management.user_management_provider_type import (
    UserManagementProviderType,
)
from workos.typing.sync_or_async import SyncOrAsync
from workos.utils.http_client import AsyncHTTPClient, SyncHTTPClient
from workos.utils.pagination_order import PaginationOrder
from workos.utils.request_helper import (
    DEFAULT_LIST_RESPONSE_LIMIT,
    RESPONSE_TYPE_CODE,
    REQUEST_METHOD_POST,
    REQUEST_METHOD_GET,
    REQUEST_METHOD_DELETE,
    REQUEST_METHOD_PUT,
    QueryParameters,
    RequestHelper,
)

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


UsersListResource = WorkOSListResource[User, UsersListFilters, ListMetadata]

OrganizationMembershipsListResource = WorkOSListResource[
    OrganizationMembership, OrganizationMembershipsListFilters, ListMetadata
]

AuthenticationFactorsListResource = WorkOSListResource[
    AuthenticationFactor, AuthenticationFactorsListFilters, ListMetadata
]

InvitationsListResource = WorkOSListResource[
    Invitation, InvitationsListFilters, ListMetadata
]


class UserManagementModule(Protocol):
    """Offers methods for using the WorkOS User Management API."""

    _client_configuration: ClientConfiguration

    def get_user(self, user_id: str) -> SyncOrAsync[User]:
        """Get the details of an existing user.

        Args:
            user_id (str): User unique identifier
        Returns:
            User: User response from WorkOS.
        """
        ...

    def list_users(
        self,
        *,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> SyncOrAsync[UsersListResource]:
        """Get a list of all of your existing users matching the criteria specified.

        Kwargs:
            email (str): Filter Users by their email. (Optional)
            organization_id (str): Filter Users by the organization they are members of. (Optional)
            limit (int): Maximum number of records to return. (Optional)
            before (str): Pagination cursor to receive records before a provided User ID. (Optional)
            after (str): Pagination cursor to receive records after a provided User ID. (Optional)
            order (Literal["asc","desc"]): Sort records in either ascending or descending (default) order by created_at timestamp. (Optional)

        Returns:
            UsersListResource: Users response from WorkOS.
        """
        ...

    def create_user(
        self,
        *,
        email: str,
        password: Optional[str] = None,
        password_hash: Optional[str] = None,
        password_hash_type: Optional[PasswordHashType] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email_verified: Optional[bool] = None,
    ) -> SyncOrAsync[User]:
        """Create a new user.

        Kwargs:
            email (str): The email address of the user.
            password (str): The password to set for the user. (Optional)
            password_hash (str): The hashed password to set for the user. Mutually exclusive with password. (Optional)
            password_hash_type (str): The algorithm originally used to hash the password, used when providing a password_hash. Valid values are 'bcrypt', `firebase-scrypt`, and `ssha`. (Optional)
            first_name (str): The user's first name. (Optional)
            last_name (str): The user's last name. (Optional)
            email_verified (bool): Whether the user's email address was previously verified. (Optional)

        Returns:
            User: Created User response from WorkOS.
        """
        ...

    def update_user(
        self,
        *,
        user_id: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email_verified: Optional[bool] = None,
        password: Optional[str] = None,
        password_hash: Optional[str] = None,
        password_hash_type: Optional[PasswordHashType] = None,
    ) -> SyncOrAsync[User]:
        """Update user attributes.

        Kwargs:
            user_id (str): The User unique identifier
            first_name (str): The user's first name. (Optional)
            last_name (str): The user's last name. (Optional)
            email_verified (bool): Whether the user's email address was previously verified. (Optional)
            password (str): The password to set for the user. (Optional)
            password_hash (str): The hashed password to set for the user, used when migrating from another user store. Mutually exclusive with password. (Optional)
            password_hash_type (str): The algorithm originally used to hash the password, used when providing a password_hash. Valid values are 'bcrypt', `firebase-scrypt`, and `ssha`. (Optional)

        Returns:
            User: Updated User response from WorkOS.
        """
        ...

    def delete_user(self, user_id: str) -> SyncOrAsync[None]:
        """Delete an existing user.

        Args:
            user_id (str):  User unique identifier
        Returns:
            None
        """
        ...

    def create_organization_membership(
        self, *, user_id: str, organization_id: str, role_slug: Optional[str] = None
    ) -> SyncOrAsync[OrganizationMembership]:
        """Create a new OrganizationMembership for the given Organization and User.

        Kwargs:
            user_id: The Unique ID of the User.
            organization_id: The Unique ID of the Organization to which the user belongs to.
            role_slug: The Unique Slug of the Role to which to grant to this membership.
                If no slug is passed in, the default role will be granted.(Optional)

        Returns:
            OrganizationMembership: Created OrganizationMembership response from WorkOS.
        """
        ...

    def update_organization_membership(
        self, *, organization_membership_id: str, role_slug: Optional[str] = None
    ) -> SyncOrAsync[OrganizationMembership]:
        """Updates an OrganizationMembership for the given id.

        Args:
            organization_membership_id (str):  The unique ID of the Organization Membership.
            role_slug: The Unique Slug of the Role to which to grant to this membership.
                If no slug is passed in, it will not be changed (Optional)

        Returns:
            OrganizationMembership: Updated OrganizationMembership response from WorkOS.
        """
        ...

    def get_organization_membership(
        self, organization_membership_id: str
    ) -> SyncOrAsync[OrganizationMembership]:
        """Get the details of an organization membership.

        Args:
            organization_membership_id (str):  The unique ID of the Organization Membership.
        Returns:
            OrganizationMembership: OrganizationMembership response from WorkOS.
        """
        ...

    def list_organization_memberships(
        self,
        *,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        statuses: Optional[Sequence[OrganizationMembershipStatus]] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> SyncOrAsync[OrganizationMembershipsListResource]:
        """Get a list of all of your existing organization memberships matching the criteria specified.

        Kwargs:
            user_id (str): Filter Organization Memberships by user. (Optional)
            organization_id (str): Filter Organization Memberships by organization. (Optional)
            statuses (Sequence[OrganizationMembershipStatus]): Filter Organization Memberships by status. (Optional)
            limit (int): Maximum number of records to return. (Optional)
            before (str): Pagination cursor to receive records before a provided Organization Membership ID. (Optional)
            after (str): Pagination cursor to receive records after a provided Organization Membership ID. (Optional)
            order (Literal["asc","desc"]): Sort records in either ascending or descending (default) order by created_at timestamp. (Optional)

        Returns:
            OrganizationMembershipsListResource: Organization Memberships response from WorkOS.
        """
        ...

    def delete_organization_membership(
        self, organization_membership_id: str
    ) -> SyncOrAsync[None]:
        """Delete an existing organization membership.

        Args:
            organization_membership_id (str):  The unique ID of the Organization Membership.
        Returns:
            None
        """
        ...

    def deactivate_organization_membership(
        self, organization_membership_id: str
    ) -> SyncOrAsync[OrganizationMembership]:
        """Deactivate an organization membership.

        Args:
            organization_membership_id (str):  The unique ID of the Organization Membership.
        Returns:
            OrganizationMembership: OrganizationMembership response from WorkOS.
        """
        ...

    def reactivate_organization_membership(
        self, organization_membership_id: str
    ) -> SyncOrAsync[OrganizationMembership]:
        """Reactivates an organization membership.

        Args:
            organization_membership_id (str):  The unique ID of the Organization Membership.
        Returns:
            OrganizationMembership: OrganizationMembership response from WorkOS.
        """
        ...

    def get_authorization_url(
        self,
        *,
        redirect_uri: str,
        domain_hint: Optional[str] = None,
        login_hint: Optional[str] = None,
        state: Optional[str] = None,
        provider: Optional[UserManagementProviderType] = None,
        connection_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        code_challenge: Optional[str] = None,
    ) -> str:
        """Generate an OAuth 2.0 authorization URL.

        The URL generated will redirect a User to the Identity Provider configured through
        WorkOS.

        Kwargs:
            redirect_uri (str): A Redirect URI to return an authorized user to.
            connection_id (str): The connection_id connection selector is used to initiate SSO for a Connection.
                The value of this parameter should be a WorkOS Connection ID. (Optional)
            organization_id (str): The organization_id connection selector is used to initiate SSO for an Organization.
                The value of this parameter should be a WorkOS Organization ID. (Optional)
            provider (UserManagementProviderType): The provider connection selector is used to initiate SSO using an OAuth-compatible provider.
                Currently, the supported values for provider are 'authkit', 'AppleOAuth', 'GitHubOAuth, 'GoogleOAuth', and 'MicrosoftOAuth'. (Optional)
            domain_hint (str): Can be used to pre-fill the domain field when initiating authentication with Microsoft OAuth,
                or with a GoogleSAML connection type. (Optional)
            login_hint (str): Can be used to pre-fill the username/email address field of the IdP sign-in page for the user,
                if you know their username ahead of time. Currently, this parameter is supported for OAuth, OpenID Connect,
                OktaSAML, and AzureSAML connection types. (Optional)
            state (str): An encoded string passed to WorkOS that'd be preserved through the authentication workflow, passed
                back as a query parameter. (Optional)
            code_challenge (str): Code challenge is derived from the code verifier used for the PKCE flow. (Optional)

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
                "Incomplete arguments. Need to specify either a 'connection_id', 'organization_id', or 'provider_id'"
            )

        if connection_id is not None:
            params["connection_id"] = connection_id
        if organization_id is not None:
            params["organization_id"] = organization_id
        if provider is not None:
            params["provider"] = provider
        if domain_hint is not None:
            params["domain_hint"] = domain_hint
        if login_hint is not None:
            params["login_hint"] = login_hint
        if state is not None:
            params["state"] = state
        if code_challenge:
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"

        return RequestHelper.build_url_with_query_params(
            base_url=self._client_configuration.base_url,
            path=USER_AUTHORIZATION_PATH,
            **params,
        )

    def _authenticate_with(
        self,
        payload: AuthenticateWithParameters,
        response_model: Type[AuthenticationResponseType],
    ) -> SyncOrAsync[AuthenticationResponseType]: ...

    def authenticate_with_password(
        self,
        *,
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> SyncOrAsync[AuthenticationResponse]:
        """Authenticates a user with email and password.

        Kwargs:
            email (str): The email address of the user.
            password (str): The password of the user.
            ip_address (str): The IP address of the request from the user who is attempting to authenticate. (Optional)
            user_agent (str): The user agent of the request from the user who is attempting to authenticate. (Optional)

        Returns:
            AuthenticationResponse: Authentication response from WorkOS.
        """
        ...

    def authenticate_with_code(
        self,
        *,
        code: str,
        code_verifier: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> SyncOrAsync[AuthenticationResponse]:
        """Authenticates an OAuth user or a user that is logging in through SSO.

        Kwargs:
            code (str): The authorization value which was passed back as a query parameter in the callback to the Redirect URI.
            code_verifier (str): The randomly generated string used to derive the code challenge that was passed to the authorization
                url as part of the PKCE flow. This parameter is required when the client secret is not present. (Optional)
            ip_address (str): The IP address of the request from the user who is attempting to authenticate. (Optional)
            user_agent (str): The user agent of the request from the user who is attempting to authenticate. (Optional)

        Returns:
            AuthenticationResponse: Authentication response from WorkOS.
        """

        ...

    def authenticate_with_magic_auth(
        self,
        *,
        code: str,
        email: str,
        link_authorization_code: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> SyncOrAsync[AuthenticationResponse]:
        """Authenticates a user by verifying a one-time code sent to the user's email address by the Magic Auth Send Code endpoint.

        Kwargs:
            code (str): The one-time code that was emailed to the user.
            email (str): The email of the User who will be authenticated.
            link_authorization_code (str): An authorization code used in a previous authenticate request that resulted in an existing user error response. (Optional)
            ip_address (str): The IP address of the request from the user who is attempting to authenticate. (Optional)
            user_agent (str): The user agent of the request from the user who is attempting to authenticate. (Optional)

        Returns:
            AuthenticationResponse: Authentication response from WorkOS.
        """
        ...

    def authenticate_with_email_verification(
        self,
        *,
        code: str,
        pending_authentication_token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> SyncOrAsync[AuthenticationResponse]:
        """Authenticates a user that requires email verification by verifying a one-time code sent to the user's email address and the pending authentication token.

        Kwargs:
            code (str): The one-time code that was emailed to the user.
            pending_authentication_token (str): The token returned from an authentication attempt due to an unverified email address.
            ip_address (str): The IP address of the request from the user who is attempting to authenticate. (Optional)
            user_agent (str): The user agent of the request from the user who is attempting to authenticate. (Optional)

        Returns:
            AuthenticationResponse: Authentication response from WorkOS.
        """
        ...

    def authenticate_with_totp(
        self,
        *,
        code: str,
        authentication_challenge_id: str,
        pending_authentication_token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> SyncOrAsync[AuthenticationResponse]:
        """Authenticates a user that has MFA enrolled by verifying the TOTP code, the Challenge from the Factor, and the pending authentication token.

        Kwargs:
            code (str): The time-based-one-time-password generated by the Factor that was challenged.
            authentication_challenge_id (str): The unique ID of the authentication Challenge created for the TOTP Factor for which the user is enrolled.
            pending_authentication_token (str): The token returned from a failed authentication attempt due to MFA challenge.
            ip_address (str): The IP address of the request from the user who is attempting to authenticate. (Optional)
            user_agent (str): The user agent of the request from the user who is attempting to authenticate. (Optional)

        Returns:
            AuthenticationResponse: Authentication response from WorkOS.
        """
        ...

    def authenticate_with_organization_selection(
        self,
        *,
        organization_id: str,
        pending_authentication_token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> SyncOrAsync[AuthenticationResponse]:
        """Authenticates a user that is a member of multiple organizations by verifying the organization ID and the pending authentication token.

        Kwargs:
            organization_id (str): The organization to authenticate for.
            pending_authentication_token (str): The token returned from a failed authentication attempt due to organization selection being required.
            ip_address (str): The IP address of the request from the user who is attempting to authenticate. (Optional)
            user_agent (str): The user agent of the request from the user who is attempting to authenticate. (Optional)

        Returns:
            AuthenticationResponse: Authentication response from WorkOS.
        """
        ...

    def authenticate_with_refresh_token(
        self,
        *,
        refresh_token: str,
        organization_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> SyncOrAsync[RefreshTokenAuthenticationResponse]:
        """Authenticates a user with a refresh token.

        Kwargs:
            refresh_token (str): The token associated to the user.
            organization_id (str): The organization to issue the new access token for. (Optional)
            ip_address (str): The IP address of the request from the user who is attempting to authenticate. (Optional)
            user_agent (str): The user agent of the request from the user who is attempting to authenticate. (Optional)

        Returns:
            RefreshTokenAuthenticationResponse: Refresh Token Authentication response from WorkOS.
        """
        ...

    def get_jwks_url(self) -> str:
        """Get the public key that is used for verifying access tokens.

        Returns:
            (str): The public JWKS URL.
        """

        return f"{self._client_configuration.base_url}sso/jwks/{self._client_configuration.client_id}"

    def get_logout_url(self, session_id: str) -> str:
        """Get the URL for ending the session and redirecting the user

        Args:
            session_id (str): The ID of the user's session

        Returns:
            (str): URL to redirect the user to to end the session.
        """

        return f"{self._client_configuration.base_url}user_management/sessions/logout?session_id={session_id}"

    def get_password_reset(self, password_reset_id: str) -> SyncOrAsync[PasswordReset]:
        """Get the details of a password reset object.

        Args:
            password_reset_id (str):  The unique ID of the password reset object.

        Returns:
            PasswordReset: PasswordReset response from WorkOS.
        """

        ...

    def create_password_reset(self, email: str) -> SyncOrAsync[PasswordReset]:
        """Creates a password reset token that can be sent to a user's email to reset the password.

        Args:
            email: The email address of the user.

        Returns:
            PasswordReset: PasswordReset response from WorkOS.
        """
        ...

    def reset_password(self, *, token: str, new_password: str) -> SyncOrAsync[User]:
        """Resets user password using token that was sent to the user.

        Kwargs:
            token (str): The reset token emailed to the user.
            new_password (str): The new password to be set for the user.

        Returns:
            User: User response from WorkOS.
        """
        ...

    def get_email_verification(
        self, email_verification_id: str
    ) -> SyncOrAsync[EmailVerification]:
        """Get the details of an email verification object.

        Args:
            email_verification_id (str):  The unique ID of the email verification object.

        Returns:
            EmailVerification: EmailVerification response from WorkOS.
        """
        ...

    def send_verification_email(self, user_id: str) -> SyncOrAsync[User]:
        """Sends a verification email to the provided user.

        Args:
            user_id (str): The unique ID of the User whose email address will be verified.

        Returns:
            User: User response from WorkOS.
        """
        ...

    def verify_email(self, *, user_id: str, code: str) -> SyncOrAsync[User]:
        """Verifies user email using one-time code that was sent to the user.

        Kwargs:
            user_id (str): The unique ID of the User whose email address will be verified.
            code (str): The one-time code emailed to the user.

        Returns:
            User: User response from WorkOS.
        """
        ...

    def get_magic_auth(self, magic_auth_id: str) -> SyncOrAsync[MagicAuth]:
        """Get the details of a Magic Auth object.

        Args:
            magic_auth_id (str):  The unique ID of the Magic Auth object.

        Returns:
            MagicAuth: MagicAuth response from WorkOS.
        """
        ...

    def create_magic_auth(
        self, *, email: str, invitation_token: Optional[str] = None
    ) -> SyncOrAsync[MagicAuth]:
        """Creates a Magic Auth code challenge that can be sent to a user's email for authentication.

        Kwargs:
            email: The email address of the user.
            invitation_token: The token of an Invitation, if required. (Optional)

        Returns:
            MagicAuth: MagicAuth response from WorkOS.
        """
        ...

    def enroll_auth_factor(
        self,
        *,
        user_id: str,
        type: AuthenticationFactorType,
        totp_issuer: Optional[str] = None,
        totp_user: Optional[str] = None,
        totp_secret: Optional[str] = None,
    ) -> SyncOrAsync[AuthenticationFactorTotpAndChallengeResponse]:
        """Enrolls a user in a new auth factor.

        Kwargs:
            user_id (str): The unique ID of the User to be enrolled in the auth factor.
            type (str): The type of factor to enroll (Only option available is 'totp').
            totp_issuer (str): Name of the Organization (Optional)
            totp_user (str): Email of user (Optional)
            totp_secret (str): The secret key for the TOTP factor. Generated if not provided. (Optional)

        Returns:
            AuthenticationFactorTotpAndChallengeResponse
        """
        ...

    def list_auth_factors(
        self,
        *,
        user_id: str,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> SyncOrAsync[AuthenticationFactorsListResource]:
        """Lists the Auth Factors for a user.

        Kwargs:
            user_id (str): The unique ID of the User to list the auth factors for.
            limit (int): Maximum number of records to return. (Optional)
            before (str): Pagination cursor to receive records before a provided AuthenticationFactor ID. (Optional)
            after (str): Pagination cursor to receive records after a provided AuthenticationFactor ID. (Optional)
            order (Literal["asc","desc"]): Sort records in either ascending or descending order by created_at timestamp.(Optional)
        Returns:
            AuthenticationFactorsListResource: List of Authentication Factors for a User from WorkOS.
        """
        ...

    def get_invitation(self, invitation_id: str) -> SyncOrAsync[Invitation]:
        """Get the details of an invitation.

        Args:
            invitation_id (str):  The unique ID of the Invitation.

        Returns:
            Invitation: Invitation response from WorkOS.
        """
        ...

    def find_invitation_by_token(
        self, invitation_token: str
    ) -> SyncOrAsync[Invitation]:
        """Get the details of an invitation.

        Args:
            invitation_token (str):  The token of the Invitation.

        Returns:
            Invitation: Invitation response from WorkOS.
        """
        ...

    def list_invitations(
        self,
        *,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> SyncOrAsync[InvitationsListResource]:
        """Get a list of all of your existing invitations matching the criteria specified.

        Kwargs:
            email (str): Filter Invitations by email. (Optional)
            organization_id (str): Filter Invitations by organization. (Optional)
            limit (int): Maximum number of records to return. (Optional)
            before (str): Pagination cursor to receive records before a provided Invitation ID. (Optional)
            after (str): Pagination cursor to receive records after a provided Invitation ID. (Optional)
            order (Literal["asc","desc"]): Sort records in either ascending or descending order by created_at timestamp. (Optional)

        Returns:
            InvitationsListResource: Invitations list response from WorkOS.
        """
        ...

    def send_invitation(
        self,
        *,
        email: str,
        organization_id: Optional[str] = None,
        expires_in_days: Optional[int] = None,
        inviter_user_id: Optional[str] = None,
        role_slug: Optional[str] = None,
    ) -> SyncOrAsync[Invitation]:
        """Sends an Invitation to a recipient.

        Kwargs:
            email: The email address of the recipient.
            organization_id: The ID of the Organization to which the recipient is being invited. (Optional)
            expires_in_days: The number of days the invitations will be valid for. Must be between 1 and 30, defaults to 7 if not specified. (Optional)
            inviter_user_id: The ID of the User sending the invitation. (Optional)
            role_slug: The unique slug of the Role to give the Membership once the invite is accepted (Optional)

        Returns:
            Invitation: Sent Invitation response from WorkOS.
        """
        ...

    def revoke_invitation(self, invitation_id: str) -> SyncOrAsync[Invitation]:
        """Revokes an existing Invitation.

        Args:
            invitation_id (str):  The unique ID of the Invitation.

        Returns:
            Invitation: Invitation response from WorkOS.
        """
        ...


class UserManagement(UserManagementModule):
    _http_client: SyncHTTPClient

    def __init__(
        self, http_client: SyncHTTPClient, client_configuration: ClientConfiguration
    ):
        self._client_configuration = client_configuration
        self._http_client = http_client

    def get_user(self, user_id: str) -> User:
        response = self._http_client.request(
            USER_DETAIL_PATH.format(user_id), method=REQUEST_METHOD_GET
        )

        return User.model_validate(response)

    def list_users(
        self,
        *,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> UsersListResource:
        params: UsersListFilters = {
            "email": email,
            "organization_id": organization_id,
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        response = self._http_client.request(
            USER_PATH, method=REQUEST_METHOD_GET, params=params
        )

        return UsersListResource(
            list_method=self.list_users,
            list_args=params,
            **ListPage[User](**response).model_dump(),
        )

    def create_user(
        self,
        *,
        email: str,
        password: Optional[str] = None,
        password_hash: Optional[str] = None,
        password_hash_type: Optional[PasswordHashType] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email_verified: Optional[bool] = None,
    ) -> User:
        json = {
            "email": email,
            "password": password,
            "password_hash": password_hash,
            "password_hash_type": password_hash_type,
            "first_name": first_name,
            "last_name": last_name,
            "email_verified": email_verified or False,
        }

        response = self._http_client.request(
            USER_PATH, method=REQUEST_METHOD_POST, json=json
        )

        return User.model_validate(response)

    def update_user(
        self,
        *,
        user_id: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email_verified: Optional[bool] = None,
        password: Optional[str] = None,
        password_hash: Optional[str] = None,
        password_hash_type: Optional[PasswordHashType] = None,
    ) -> User:
        json = {
            "first_name": first_name,
            "last_name": last_name,
            "email_verified": email_verified,
            "password": password,
            "password_hash": password_hash,
            "password_hash_type": password_hash_type,
        }

        response = self._http_client.request(
            USER_DETAIL_PATH.format(user_id), method=REQUEST_METHOD_PUT, json=json
        )

        return User.model_validate(response)

    def delete_user(self, user_id: str) -> None:
        self._http_client.request(
            USER_DETAIL_PATH.format(user_id),
            method=REQUEST_METHOD_DELETE,
        )

    def create_organization_membership(
        self, *, user_id: str, organization_id: str, role_slug: Optional[str] = None
    ) -> OrganizationMembership:
        json = {
            "user_id": user_id,
            "organization_id": organization_id,
            "role_slug": role_slug,
        }

        response = self._http_client.request(
            ORGANIZATION_MEMBERSHIP_PATH, method=REQUEST_METHOD_POST, json=json
        )

        return OrganizationMembership.model_validate(response)

    def update_organization_membership(
        self, *, organization_membership_id: str, role_slug: Optional[str] = None
    ) -> OrganizationMembership:
        json = {
            "role_slug": role_slug,
        }

        response = self._http_client.request(
            ORGANIZATION_MEMBERSHIP_DETAIL_PATH.format(organization_membership_id),
            method=REQUEST_METHOD_PUT,
            json=json,
        )

        return OrganizationMembership.model_validate(response)

    def get_organization_membership(
        self, organization_membership_id: str
    ) -> OrganizationMembership:
        response = self._http_client.request(
            ORGANIZATION_MEMBERSHIP_DETAIL_PATH.format(organization_membership_id),
            method=REQUEST_METHOD_GET,
        )

        return OrganizationMembership.model_validate(response)

    def list_organization_memberships(
        self,
        *,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        statuses: Optional[Sequence[OrganizationMembershipStatus]] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> OrganizationMembershipsListResource:
        params: OrganizationMembershipsListFilters = {
            "user_id": user_id,
            "organization_id": organization_id,
            "statuses": statuses,
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        response = self._http_client.request(
            ORGANIZATION_MEMBERSHIP_PATH, method=REQUEST_METHOD_GET, params=params
        )

        return OrganizationMembershipsListResource(
            list_method=self.list_organization_memberships,
            list_args=params,
            **ListPage[OrganizationMembership](**response).model_dump(),
        )

    def delete_organization_membership(self, organization_membership_id: str) -> None:
        self._http_client.request(
            ORGANIZATION_MEMBERSHIP_DETAIL_PATH.format(organization_membership_id),
            method=REQUEST_METHOD_DELETE,
        )

    def deactivate_organization_membership(
        self, organization_membership_id: str
    ) -> OrganizationMembership:
        response = self._http_client.request(
            ORGANIZATION_MEMBERSHIP_DEACTIVATE_PATH.format(organization_membership_id),
            method=REQUEST_METHOD_PUT,
        )

        return OrganizationMembership.model_validate(response)

    def reactivate_organization_membership(
        self, organization_membership_id: str
    ) -> OrganizationMembership:
        response = self._http_client.request(
            ORGANIZATION_MEMBERSHIP_REACTIVATE_PATH.format(organization_membership_id),
            method=REQUEST_METHOD_PUT,
        )

        return OrganizationMembership.model_validate(response)

    def _authenticate_with(
        self,
        payload: AuthenticateWithParameters,
        response_model: Type[AuthenticationResponseType],
    ) -> AuthenticationResponseType:
        json = {
            "client_id": self._http_client.client_id,
            "client_secret": self._http_client.api_key,
            **payload,
        }

        response = self._http_client.request(
            USER_AUTHENTICATE_PATH,
            method=REQUEST_METHOD_POST,
            json=json,
        )

        return response_model.model_validate(response)

    def authenticate_with_password(
        self,
        *,
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuthenticationResponse:
        payload: AuthenticateWithPasswordParameters = {
            "email": email,
            "password": password,
            "grant_type": "password",
            "ip_address": ip_address,
            "user_agent": user_agent,
        }

        return self._authenticate_with(payload, response_model=AuthenticationResponse)

    def authenticate_with_code(
        self,
        *,
        code: str,
        code_verifier: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuthKitAuthenticationResponse:
        payload: AuthenticateWithCodeParameters = {
            "code": code,
            "grant_type": "authorization_code",
            "ip_address": ip_address,
            "user_agent": user_agent,
            "code_verifier": code_verifier,
        }

        return self._authenticate_with(
            payload, response_model=AuthKitAuthenticationResponse
        )

    def authenticate_with_magic_auth(
        self,
        *,
        code: str,
        email: str,
        link_authorization_code: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuthenticationResponse:
        payload: AuthenticateWithMagicAuthParameters = {
            "code": code,
            "email": email,
            "grant_type": "urn:workos:oauth:grant-type:magic-auth:code",
            "link_authorization_code": link_authorization_code,
            "ip_address": ip_address,
            "user_agent": user_agent,
        }

        return self._authenticate_with(payload, response_model=AuthenticationResponse)

    def authenticate_with_email_verification(
        self,
        *,
        code: str,
        pending_authentication_token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuthenticationResponse:
        payload: AuthenticateWithEmailVerificationParameters = {
            "code": code,
            "pending_authentication_token": pending_authentication_token,
            "grant_type": "urn:workos:oauth:grant-type:email-verification:code",
            "ip_address": ip_address,
            "user_agent": user_agent,
        }

        return self._authenticate_with(payload, response_model=AuthenticationResponse)

    def authenticate_with_totp(
        self,
        *,
        code: str,
        authentication_challenge_id: str,
        pending_authentication_token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuthenticationResponse:
        payload: AuthenticateWithTotpParameters = {
            "code": code,
            "authentication_challenge_id": authentication_challenge_id,
            "pending_authentication_token": pending_authentication_token,
            "grant_type": "urn:workos:oauth:grant-type:mfa-totp",
            "ip_address": ip_address,
            "user_agent": user_agent,
        }

        return self._authenticate_with(payload, response_model=AuthenticationResponse)

    def authenticate_with_organization_selection(
        self,
        *,
        organization_id: str,
        pending_authentication_token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuthenticationResponse:
        payload: AuthenticateWithOrganizationSelectionParameters = {
            "organization_id": organization_id,
            "pending_authentication_token": pending_authentication_token,
            "grant_type": "urn:workos:oauth:grant-type:organization-selection",
            "ip_address": ip_address,
            "user_agent": user_agent,
        }

        return self._authenticate_with(payload, response_model=AuthenticationResponse)

    def authenticate_with_refresh_token(
        self,
        *,
        refresh_token: str,
        organization_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> RefreshTokenAuthenticationResponse:
        payload: AuthenticateWithRefreshTokenParameters = {
            "refresh_token": refresh_token,
            "organization_id": organization_id,
            "grant_type": "refresh_token",
            "ip_address": ip_address,
            "user_agent": user_agent,
        }

        return self._authenticate_with(
            payload, response_model=RefreshTokenAuthenticationResponse
        )

    def get_password_reset(self, password_reset_id: str) -> PasswordReset:
        response = self._http_client.request(
            PASSWORD_RESET_DETAIL_PATH.format(password_reset_id),
            method=REQUEST_METHOD_GET,
        )

        return PasswordReset.model_validate(response)

    def create_password_reset(self, email: str) -> PasswordReset:
        json = {
            "email": email,
        }

        response = self._http_client.request(
            PASSWORD_RESET_PATH, method=REQUEST_METHOD_POST, json=json
        )

        return PasswordReset.model_validate(response)

    def reset_password(self, *, token: str, new_password: str) -> User:
        json = {
            "token": token,
            "new_password": new_password,
        }

        response = self._http_client.request(
            USER_RESET_PASSWORD_PATH, method=REQUEST_METHOD_POST, json=json
        )

        return User.model_validate(response["user"])

    def get_email_verification(self, email_verification_id: str) -> EmailVerification:
        response = self._http_client.request(
            EMAIL_VERIFICATION_DETAIL_PATH.format(email_verification_id),
            method=REQUEST_METHOD_GET,
        )

        return EmailVerification.model_validate(response)

    def send_verification_email(self, user_id: str) -> User:
        response = self._http_client.request(
            USER_SEND_VERIFICATION_EMAIL_PATH.format(user_id),
            method=REQUEST_METHOD_POST,
        )

        return User.model_validate(response["user"])

    def verify_email(self, *, user_id: str, code: str) -> User:
        json = {
            "code": code,
        }

        response = self._http_client.request(
            USER_VERIFY_EMAIL_CODE_PATH.format(user_id),
            method=REQUEST_METHOD_POST,
            json=json,
        )

        return User.model_validate(response["user"])

    def get_magic_auth(self, magic_auth_id: str) -> MagicAuth:
        response = self._http_client.request(
            MAGIC_AUTH_DETAIL_PATH.format(magic_auth_id), method=REQUEST_METHOD_GET
        )

        return MagicAuth.model_validate(response)

    def create_magic_auth(
        self,
        *,
        email: str,
        invitation_token: Optional[str] = None,
    ) -> MagicAuth:
        json = {
            "email": email,
            "invitation_token": invitation_token,
        }

        response = self._http_client.request(
            MAGIC_AUTH_PATH, method=REQUEST_METHOD_POST, json=json
        )

        return MagicAuth.model_validate(response)

    def enroll_auth_factor(
        self,
        *,
        user_id: str,
        type: AuthenticationFactorType,
        totp_issuer: Optional[str] = None,
        totp_user: Optional[str] = None,
        totp_secret: Optional[str] = None,
    ) -> AuthenticationFactorTotpAndChallengeResponse:
        json = {
            "type": type,
            "totp_issuer": totp_issuer,
            "totp_user": totp_user,
            "totp_secret": totp_secret,
        }

        response = self._http_client.request(
            USER_AUTH_FACTORS_PATH.format(user_id),
            method=REQUEST_METHOD_POST,
            json=json,
        )

        return AuthenticationFactorTotpAndChallengeResponse.model_validate(response)

    def list_auth_factors(
        self,
        *,
        user_id: str,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> AuthenticationFactorsListResource:
        params: ListArgs = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        response = self._http_client.request(
            USER_AUTH_FACTORS_PATH.format(user_id),
            method=REQUEST_METHOD_GET,
            params=params,
        )

        # We don't spread params on this dict to make mypy happy
        list_args: AuthenticationFactorsListFilters = {
            "limit": limit or DEFAULT_LIST_RESPONSE_LIMIT,
            "before": before,
            "after": after,
            "order": order,
            "user_id": user_id,
        }

        return AuthenticationFactorsListResource(
            list_method=self.list_auth_factors,
            list_args=list_args,
            **ListPage[AuthenticationFactor](**response).model_dump(),
        )

    def get_invitation(self, invitation_id: str) -> Invitation:
        response = self._http_client.request(
            INVITATION_DETAIL_PATH.format(invitation_id),
            method=REQUEST_METHOD_GET,
        )

        return Invitation.model_validate(response)

    def find_invitation_by_token(self, invitation_token: str) -> Invitation:
        response = self._http_client.request(
            INVITATION_DETAIL_BY_TOKEN_PATH.format(invitation_token),
            method=REQUEST_METHOD_GET,
        )

        return Invitation.model_validate(response)

    def list_invitations(
        self,
        *,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> InvitationsListResource:
        params: InvitationsListFilters = {
            "email": email,
            "organization_id": organization_id,
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        response = self._http_client.request(
            INVITATION_PATH, method=REQUEST_METHOD_GET, params=params
        )

        return InvitationsListResource(
            list_method=self.list_invitations,
            list_args=params,
            **ListPage[Invitation](**response).model_dump(),
        )

    def send_invitation(
        self,
        *,
        email: str,
        organization_id: Optional[str] = None,
        expires_in_days: Optional[int] = None,
        inviter_user_id: Optional[str] = None,
        role_slug: Optional[str] = None,
    ) -> Invitation:
        json = {
            "email": email,
            "organization_id": organization_id,
            "expires_in_days": expires_in_days,
            "inviter_user_id": inviter_user_id,
            "role_slug": role_slug,
        }

        response = self._http_client.request(
            INVITATION_PATH, method=REQUEST_METHOD_POST, json=json
        )

        return Invitation.model_validate(response)

    def revoke_invitation(self, invitation_id: str) -> Invitation:
        response = self._http_client.request(
            INVITATION_REVOKE_PATH.format(invitation_id), method=REQUEST_METHOD_POST
        )

        return Invitation.model_validate(response)


class AsyncUserManagement(UserManagementModule):
    _http_client: AsyncHTTPClient

    def __init__(
        self, http_client: AsyncHTTPClient, client_configuration: ClientConfiguration
    ):
        self._client_configuration = client_configuration
        self._http_client = http_client

    async def get_user(self, user_id: str) -> User:
        response = await self._http_client.request(
            USER_DETAIL_PATH.format(user_id), method=REQUEST_METHOD_GET
        )

        return User.model_validate(response)

    async def list_users(
        self,
        *,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> UsersListResource:
        params: UsersListFilters = {
            "email": email,
            "organization_id": organization_id,
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        response = await self._http_client.request(
            USER_PATH, method=REQUEST_METHOD_GET, params=params
        )

        return UsersListResource(
            list_method=self.list_users,
            list_args=params,
            **ListPage[User](**response).model_dump(),
        )

    async def create_user(
        self,
        *,
        email: str,
        password: Optional[str] = None,
        password_hash: Optional[str] = None,
        password_hash_type: Optional[PasswordHashType] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email_verified: Optional[bool] = None,
    ) -> User:
        json = {
            "email": email,
            "password": password,
            "password_hash": password_hash,
            "password_hash_type": password_hash_type,
            "first_name": first_name,
            "last_name": last_name,
            "email_verified": email_verified or False,
        }

        response = await self._http_client.request(
            USER_PATH, method=REQUEST_METHOD_POST, json=json
        )

        return User.model_validate(response)

    async def update_user(
        self,
        *,
        user_id: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email_verified: Optional[bool] = None,
        password: Optional[str] = None,
        password_hash: Optional[str] = None,
        password_hash_type: Optional[PasswordHashType] = None,
    ) -> User:
        json = {
            "first_name": first_name,
            "last_name": last_name,
            "email_verified": email_verified,
            "password": password,
            "password_hash": password_hash,
            "password_hash_type": password_hash_type,
        }

        response = await self._http_client.request(
            USER_DETAIL_PATH.format(user_id), method=REQUEST_METHOD_PUT, json=json
        )

        return User.model_validate(response)

    async def delete_user(self, user_id: str) -> None:
        await self._http_client.request(
            USER_DETAIL_PATH.format(user_id), method=REQUEST_METHOD_DELETE
        )

    async def create_organization_membership(
        self, *, user_id: str, organization_id: str, role_slug: Optional[str] = None
    ) -> OrganizationMembership:
        json = {
            "user_id": user_id,
            "organization_id": organization_id,
            "role_slug": role_slug,
        }

        response = await self._http_client.request(
            ORGANIZATION_MEMBERSHIP_PATH, method=REQUEST_METHOD_POST, json=json
        )

        return OrganizationMembership.model_validate(response)

    async def update_organization_membership(
        self, *, organization_membership_id: str, role_slug: Optional[str] = None
    ) -> OrganizationMembership:
        json = {
            "role_slug": role_slug,
        }

        response = await self._http_client.request(
            ORGANIZATION_MEMBERSHIP_DETAIL_PATH.format(organization_membership_id),
            method=REQUEST_METHOD_PUT,
            json=json,
        )

        return OrganizationMembership.model_validate(response)

    async def get_organization_membership(
        self, organization_membership_id: str
    ) -> OrganizationMembership:
        response = await self._http_client.request(
            ORGANIZATION_MEMBERSHIP_DETAIL_PATH.format(organization_membership_id),
            method=REQUEST_METHOD_GET,
        )

        return OrganizationMembership.model_validate(response)

    async def list_organization_memberships(
        self,
        *,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        statuses: Optional[Sequence[OrganizationMembershipStatus]] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> OrganizationMembershipsListResource:
        params: OrganizationMembershipsListFilters = {
            "user_id": user_id,
            "organization_id": organization_id,
            "statuses": statuses,
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        response = await self._http_client.request(
            ORGANIZATION_MEMBERSHIP_PATH, method=REQUEST_METHOD_GET, params=params
        )

        return OrganizationMembershipsListResource(
            list_method=self.list_organization_memberships,
            list_args=params,
            **ListPage[OrganizationMembership](**response).model_dump(),
        )

    async def delete_organization_membership(
        self, organization_membership_id: str
    ) -> None:
        await self._http_client.request(
            ORGANIZATION_MEMBERSHIP_DETAIL_PATH.format(organization_membership_id),
            method=REQUEST_METHOD_DELETE,
        )

    async def deactivate_organization_membership(
        self, organization_membership_id: str
    ) -> OrganizationMembership:
        response = await self._http_client.request(
            ORGANIZATION_MEMBERSHIP_DEACTIVATE_PATH.format(organization_membership_id),
            method=REQUEST_METHOD_PUT,
        )

        return OrganizationMembership.model_validate(response)

    async def reactivate_organization_membership(
        self, organization_membership_id: str
    ) -> OrganizationMembership:
        response = await self._http_client.request(
            ORGANIZATION_MEMBERSHIP_REACTIVATE_PATH.format(organization_membership_id),
            method=REQUEST_METHOD_PUT,
        )

        return OrganizationMembership.model_validate(response)

    async def _authenticate_with(
        self,
        payload: AuthenticateWithParameters,
        response_model: Type[AuthenticationResponseType],
    ) -> AuthenticationResponseType:
        json = {
            "client_id": self._http_client.client_id,
            "client_secret": self._http_client.api_key,
            **payload,
        }

        response = await self._http_client.request(
            USER_AUTHENTICATE_PATH,
            method=REQUEST_METHOD_POST,
            json=json,
        )

        return response_model.model_validate(response)

    async def authenticate_with_password(
        self,
        *,
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuthenticationResponse:
        payload: AuthenticateWithPasswordParameters = {
            "email": email,
            "password": password,
            "grant_type": "password",
            "ip_address": ip_address,
            "user_agent": user_agent,
        }

        return await self._authenticate_with(
            payload, response_model=AuthenticationResponse
        )

    async def authenticate_with_code(
        self,
        *,
        code: str,
        code_verifier: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuthKitAuthenticationResponse:
        payload: AuthenticateWithCodeParameters = {
            "code": code,
            "grant_type": "authorization_code",
            "ip_address": ip_address,
            "user_agent": user_agent,
            "code_verifier": code_verifier,
        }

        return await self._authenticate_with(
            payload, response_model=AuthKitAuthenticationResponse
        )

    async def authenticate_with_magic_auth(
        self,
        *,
        code: str,
        email: str,
        link_authorization_code: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuthenticationResponse:
        payload: AuthenticateWithMagicAuthParameters = {
            "code": code,
            "email": email,
            "grant_type": "urn:workos:oauth:grant-type:magic-auth:code",
            "link_authorization_code": link_authorization_code,
            "ip_address": ip_address,
            "user_agent": user_agent,
        }

        return await self._authenticate_with(
            payload, response_model=AuthenticationResponse
        )

    async def authenticate_with_email_verification(
        self,
        *,
        code: str,
        pending_authentication_token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuthenticationResponse:
        payload: AuthenticateWithEmailVerificationParameters = {
            "code": code,
            "pending_authentication_token": pending_authentication_token,
            "grant_type": "urn:workos:oauth:grant-type:email-verification:code",
            "ip_address": ip_address,
            "user_agent": user_agent,
        }

        return await self._authenticate_with(
            payload, response_model=AuthenticationResponse
        )

    async def authenticate_with_totp(
        self,
        *,
        code: str,
        authentication_challenge_id: str,
        pending_authentication_token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuthenticationResponse:
        payload: AuthenticateWithTotpParameters = {
            "code": code,
            "authentication_challenge_id": authentication_challenge_id,
            "pending_authentication_token": pending_authentication_token,
            "grant_type": "urn:workos:oauth:grant-type:mfa-totp",
            "ip_address": ip_address,
            "user_agent": user_agent,
        }

        return await self._authenticate_with(
            payload, response_model=AuthenticationResponse
        )

    async def authenticate_with_organization_selection(
        self,
        *,
        organization_id: str,
        pending_authentication_token: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuthenticationResponse:
        payload: AuthenticateWithOrganizationSelectionParameters = {
            "organization_id": organization_id,
            "pending_authentication_token": pending_authentication_token,
            "grant_type": "urn:workos:oauth:grant-type:organization-selection",
            "ip_address": ip_address,
            "user_agent": user_agent,
        }

        return await self._authenticate_with(
            payload, response_model=AuthenticationResponse
        )

    async def authenticate_with_refresh_token(
        self,
        *,
        refresh_token: str,
        organization_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> RefreshTokenAuthenticationResponse:
        payload: AuthenticateWithRefreshTokenParameters = {
            "refresh_token": refresh_token,
            "organization_id": organization_id,
            "grant_type": "refresh_token",
            "ip_address": ip_address,
            "user_agent": user_agent,
        }

        return await self._authenticate_with(
            payload, response_model=RefreshTokenAuthenticationResponse
        )

    async def get_password_reset(self, password_reset_id: str) -> PasswordReset:
        response = await self._http_client.request(
            PASSWORD_RESET_DETAIL_PATH.format(password_reset_id),
            method=REQUEST_METHOD_GET,
        )

        return PasswordReset.model_validate(response)

    async def create_password_reset(self, email: str) -> PasswordReset:
        json = {
            "email": email,
        }

        response = await self._http_client.request(
            PASSWORD_RESET_PATH, method=REQUEST_METHOD_POST, json=json
        )

        return PasswordReset.model_validate(response)

    async def reset_password(self, *, token: str, new_password: str) -> User:
        json = {
            "token": token,
            "new_password": new_password,
        }

        response = await self._http_client.request(
            USER_RESET_PASSWORD_PATH, method=REQUEST_METHOD_POST, json=json
        )

        return User.model_validate(response["user"])

    async def get_email_verification(
        self, email_verification_id: str
    ) -> EmailVerification:
        response = await self._http_client.request(
            EMAIL_VERIFICATION_DETAIL_PATH.format(email_verification_id),
            method=REQUEST_METHOD_GET,
        )

        return EmailVerification.model_validate(response)

    async def send_verification_email(self, user_id: str) -> User:
        response = await self._http_client.request(
            USER_SEND_VERIFICATION_EMAIL_PATH.format(user_id),
            method=REQUEST_METHOD_POST,
        )

        return User.model_validate(response["user"])

    async def verify_email(self, *, user_id: str, code: str) -> User:
        json = {
            "code": code,
        }

        response = await self._http_client.request(
            USER_VERIFY_EMAIL_CODE_PATH.format(user_id),
            method=REQUEST_METHOD_POST,
            json=json,
        )

        return User.model_validate(response["user"])

    async def get_magic_auth(self, magic_auth_id: str) -> MagicAuth:
        response = await self._http_client.request(
            MAGIC_AUTH_DETAIL_PATH.format(magic_auth_id), method=REQUEST_METHOD_GET
        )

        return MagicAuth.model_validate(response)

    async def create_magic_auth(
        self,
        *,
        email: str,
        invitation_token: Optional[str] = None,
    ) -> MagicAuth:
        json = {
            "email": email,
            "invitation_token": invitation_token,
        }

        response = await self._http_client.request(
            MAGIC_AUTH_PATH, method=REQUEST_METHOD_POST, json=json
        )

        return MagicAuth.model_validate(response)

    async def enroll_auth_factor(
        self,
        *,
        user_id: str,
        type: AuthenticationFactorType,
        totp_issuer: Optional[str] = None,
        totp_user: Optional[str] = None,
        totp_secret: Optional[str] = None,
    ) -> AuthenticationFactorTotpAndChallengeResponse:
        json = {
            "type": type,
            "totp_issuer": totp_issuer,
            "totp_user": totp_user,
            "totp_secret": totp_secret,
        }

        response = await self._http_client.request(
            USER_AUTH_FACTORS_PATH.format(user_id),
            method=REQUEST_METHOD_POST,
            json=json,
        )

        return AuthenticationFactorTotpAndChallengeResponse.model_validate(response)

    async def list_auth_factors(
        self,
        *,
        user_id: str,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> AuthenticationFactorsListResource:
        params: ListArgs = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        response = await self._http_client.request(
            USER_AUTH_FACTORS_PATH.format(user_id),
            method=REQUEST_METHOD_GET,
            params=params,
        )

        # We don't spread params on this dict to make mypy happy
        list_args: AuthenticationFactorsListFilters = {
            "limit": limit or DEFAULT_LIST_RESPONSE_LIMIT,
            "before": before,
            "after": after,
            "order": order,
            "user_id": user_id,
        }

        return AuthenticationFactorsListResource(
            list_method=self.list_auth_factors,
            list_args=list_args,
            **ListPage[AuthenticationFactor](**response).model_dump(),
        )

    async def get_invitation(self, invitation_id: str) -> Invitation:
        response = await self._http_client.request(
            INVITATION_DETAIL_PATH.format(invitation_id), method=REQUEST_METHOD_GET
        )

        return Invitation.model_validate(response)

    async def find_invitation_by_token(self, invitation_token: str) -> Invitation:
        response = await self._http_client.request(
            INVITATION_DETAIL_BY_TOKEN_PATH.format(invitation_token),
            method=REQUEST_METHOD_GET,
        )

        return Invitation.model_validate(response)

    async def list_invitations(
        self,
        *,
        email: Optional[str] = None,
        organization_id: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> InvitationsListResource:
        params: InvitationsListFilters = {
            "email": email,
            "organization_id": organization_id,
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        response = await self._http_client.request(
            INVITATION_PATH, method=REQUEST_METHOD_GET, params=params
        )

        return InvitationsListResource(
            list_method=self.list_invitations,
            list_args=params,
            **ListPage[Invitation](**response).model_dump(),
        )

    async def send_invitation(
        self,
        *,
        email: str,
        organization_id: Optional[str] = None,
        expires_in_days: Optional[int] = None,
        inviter_user_id: Optional[str] = None,
        role_slug: Optional[str] = None,
    ) -> Invitation:
        json = {
            "email": email,
            "organization_id": organization_id,
            "expires_in_days": expires_in_days,
            "inviter_user_id": inviter_user_id,
            "role_slug": role_slug,
        }

        response = await self._http_client.request(
            INVITATION_PATH, method=REQUEST_METHOD_POST, json=json
        )

        return Invitation.model_validate(response)

    async def revoke_invitation(self, invitation_id: str) -> Invitation:
        response = await self._http_client.request(
            INVITATION_REVOKE_PATH.format(invitation_id), method=REQUEST_METHOD_POST
        )

        return Invitation.model_validate(response)
