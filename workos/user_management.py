import workos
from workos.resources.list import WorkOSListResource
from workos.resources.mfa import WorkOSAuthenticationFactorTotp, WorkOSChallenge
from workos.resources.user_management import (
    WorkOSAuthenticationResponse,
    WorkOSOrganizationMembership,
    WorkOSPasswordChallengeResponse,
    WorkOSUser,
)
from workos.utils.pagination_order import Order
from workos.utils.request import (
    RequestHelper,
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
USER_PASSWORD_PATH = "users/{0}/password"
USER_AUTHENTICATE_PATH = "users/authenticate"
USER_PASSWORD_RESET_CHALLENGE_PATH = "users/password_reset_challenge"
USER_PASSWORD_RESET_PATH = "users/password_reset"
USER_SEND_VERIFICATION_EMAIL_PATH = "users/{0}/send_verification_email"
USER_VERIFY_EMAIL_CODE_PATH = "users/verify_email_code"
USER_SEND_MAGIC_AUTH_PATH = "user_management/magic_auth/send"
USER_AUTH_FACTORS_PATH = "user_management/users/{0}/auth_factors"

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

    def create_user(self, user):
        """Create a new unmanaged user with email password authentication.

        Args:
            user (dict) - An user object
                user[email] (string) - The email address of the user.
                user[password] (string) - The password to set for the user.
                user[first_name] (string) - The user's first name.
                user[last_name] (string) - The user's last name.
                user[email_verified] (bool) - Whether the user's email address was previously verified.

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

    def update_user(self, user_id, payload):
        """Update user attributes.

        Args:
            user_id (str) - The User unique identifier
            payload (dict) - The User attributes to be updated
                user[first_name] (string) - The user's first name.
                user[last_name] (string) - The user's last name.
                user[email_verified] (bool) - Whether the user's email address was previously verified.

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

    def update_user_password(self, user_id, password):
        """Update user password.

        Args:
            user_id (str) - A user unique identifier
            password (str) - The new password to be set

        Returns:
            dict: Updated User response from WorkOS.
        """
        payload = {"password": password}

        response = self.request_helper.request(
            USER_PASSWORD_PATH.format(user_id),
            method=REQUEST_METHOD_PUT,
            params=payload,
            token=workos.api_key,
        )

        return WorkOSUser.construct_from_response(response).to_dict()

    def create_organization_membership(self, user_id, organization_id):
        """Create a new OrganizationMembership for the given Organization and User.

        Args:
            user_id: The Unique ID of the User.
            organization_id: The Unique ID of the Organization to which the user belongs to.

        Returns:
            dict: Created OrganizationMembership response from WorkOS.
        """
        headers = {}

        params = {"user_id": user_id, "organization_id": organization_id}

        response = self.request_helper.request(
            ORGANIZATION_MEMBERSHIP_PATH,
            method=REQUEST_METHOD_POST,
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
        limit=None,
        before=None,
        after=None,
        order=None,
    ):
        """Get a list of all of your existing organization memberships matching the criteria specified.

        Kwargs:
            user_id (str): Filter Organization Memberships by user. (Optional)
            organization_id (str): Filter Organization Memberships by organization. (Optional)
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

        params = {
            "user_id": user_id,
            "organization_id": organization_id,
            "limit": limit,
            "before": before,
            "after": after,
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

    def authenticate_with_magic_auth(
        self,
        code,
        user_id,
        ip_address=None,
        user_agent=None,
    ):
        """Authenticates a user by verifying a one-time code sent to the user's email address by the Magic Auth Send Code endpoint.

        Kwargs:
            code (str): The one-time code that was emailed to the user.
            user_id (str): The unique ID of the User who will be authenticated.
            ip_address (str): The IP address of the request from the user who is attempting to authenticate. (Optional)
            user_agent (str): The user agent of the request from the user who is attempting to authenticate. (Optional)

        Returns:
            (dict): Authentication response from WorkOS.
                [user] (dict): User response from WorkOS
                [session] (dict): Session response from WorkOS
        """

        headers = {}

        payload = {
            "client_id": workos.client_id,
            "client_secret": workos.api_key,
            "code": code,
            "user_id": user_id,
            "grant_type": "urn:workos:oauth:grant-type:magic-auth:code",
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

    def authenticate_with_password(
        self,
        email,
        password,
        ip_address=None,
        user_agent=None,
    ):
        """Authenticates a user with email and password and optionally creates a session.

        Kwargs:
            email (str): The email address of the user.
            password (str): The password of the user.
            ip_address (str): The IP address of the request from the user who is attempting to authenticate. (Optional)
            user_agent (str): The user agent of the request from the user who is attempting to authenticate. (Optional)

        Returns:
            (dict): Authentication response from WorkOS.
                [user] (dict): User response from WorkOS
                [session] (dict): Session response from WorkOS
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
        ip_address=None,
        user_agent=None,
    ):
        """Authenticates an OAuth user or a managed SSO user that is logging in through SSO,
            and optionally creates a session.

        Kwargs:
            code (str): The authorization value which was passed back as a query parameter in the callback to the Redirect URI.
            ip_address (str): The IP address of the request from the user who is attempting to authenticate. (Optional)
            user_agent (str): The user agent of the request from the user who is attempting to authenticate. (Optional)

        Returns:
            (dict): Authentication response from WorkOS.
                [user] (dict): User response from WorkOS
                [session] (dict): Session response from WorkOS
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

        response = self.request_helper.request(
            USER_AUTHENTICATE_PATH,
            method=REQUEST_METHOD_POST,
            headers=headers,
            params=payload,
        )

        return WorkOSAuthenticationResponse.construct_from_response(response).to_dict()

    def create_password_reset_challenge(
        self,
        email,
        password_reset_url,
    ):
        """Creates a password reset challenge and emails a password reset link to a user

        Kwargs:
            email (str): The email of the user that wishes to reset their password.
            password_reset_url (str): The URL that will be linked to in the email.

        Returns:
            (dict): Authentication response from WorkOS.
                [token] (str): The password reset token.
                [user] (dict): User response from WorkOS
        """

        headers = {}

        payload = {
            "email": email,
            "password_reset_url": password_reset_url,
        }

        response = self.request_helper.request(
            USER_PASSWORD_RESET_CHALLENGE_PATH,
            method=REQUEST_METHOD_POST,
            headers=headers,
            params=payload,
            token=workos.api_key,
        )

        return WorkOSPasswordChallengeResponse.construct_from_response(
            response
        ).to_dict()

    def complete_password_reset(
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
            USER_PASSWORD_RESET_PATH,
            method=REQUEST_METHOD_POST,
            headers=headers,
            params=payload,
            token=workos.api_key,
        )

        return WorkOSUser.construct_from_response(response).to_dict()

    def send_verification_email(
        self,
        user_id,
    ):
        """Sends a verification email to the provided user.

        Kwargs:
            user_id (str): The unique ID of the User whose email address will be verified.

        Returns:
            dict: MagicAuthChallenge response from WorkOS.
        """

        headers = {}

        response = self.request_helper.request(
            USER_SEND_VERIFICATION_EMAIL_PATH.format(user_id),
            method=REQUEST_METHOD_POST,
            headers=headers,
            token=workos.api_key,
        )

        return WorkOSUser.construct_from_response(response).to_dict()

    def verify_email_code(
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
            "user_id": user_id,
            "code": code,
        }

        response = self.request_helper.request(
            USER_VERIFY_EMAIL_CODE_PATH,
            method=REQUEST_METHOD_POST,
            headers=headers,
            params=payload,
            token=workos.api_key,
        )

        return WorkOSUser.construct_from_response(response["user"]).to_dict()

    def send_magic_auth_code(
        self,
        email,
    ):
        """Creates a one-time Magic Auth code and emails it to the user.

        Kwargs:
            email (str): The email address the one-time code will be sent to.

        Returns:
            dict: User response from WorkOS.
        """

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

        return WorkOSUser.construct_from_response(response).to_dict()

    def enroll_auth_factor(
        self,
        user_id,
        type,
        totp_issuer=None,
        totp_user=None,
    ):
        """Enrolls a user in a new auth factor.

        Kwargs:
            user_id (str): The unique ID of the User to be enrolled in the auth factor.
            type (str): The type of factor to enroll (Only option available is 'totp').
            totp_issuer (str): Name of the Organization (Optional)
            totp_user (str): Email of user (Optional)

        Returns: { WorkOSAuthenticationFactorTotp, WorkOSChallenge}
        """

        if type not in ["totp"]:
            raise ValueError("Type parameter must be 'totp'")

        headers = {}

        payload = {
            "type": type,
            "totp_issuer": totp_issuer,
            "totp_user": totp_user,
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
