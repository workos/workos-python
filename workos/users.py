import workos
from workos.resources.authentication_response import WorkOSAuthenticationResponse
from workos.resources.password_challenge_response import WorkOSPasswordChallengeResponse
from workos.resources.list import WorkOSListResource
from workos.resources.users import (
    WorkOSUser,
)
from workos.utils.pagination_order import Order
from workos.utils.request import (
    RequestHelper,
    REQUEST_METHOD_POST,
    REQUEST_METHOD_GET,
    REQUEST_METHOD_DELETE,
)
from workos.utils.validation import validate_settings, USERS_MODULE

USER_PATH = "users"
USER_DETAIL_PATH = "users/{0}"
USER_ORGANIZATION_PATH = "users/{0}/organization/{1}"
USER_SESSION_TOKEN_PATH = "users/session/token"
USER_PASSWORD_RESET_CHALLENGE_PATH = "users/password_reset_challenge"
USER_PASSWORD_RESET_PATH = "users/password_reset"
USER_SEND_VERIFICATION_EMAIL_PATH = "users/{0}/send_verification_email"
USER_VERIFY_EMAIL_PATH = "users/verify_email"
USER_SEND_MAGIC_AUTH_PATH = "users/magic_auth/send"

RESPONSE_LIMIT = 10


class Users(WorkOSListResource):
    """Offers methods for using the WorkOS User Management API."""

    @validate_settings(USERS_MODULE)
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

    def get_user(self, user):
        """Get the details of an existing user.

        Args:
            user (str) - User unique identifier
        Returns:
            dict: User response from WorkOS.
        """
        headers = {}

        response = self.request_helper.request(
            USER_DETAIL_PATH.format(user),
            method=REQUEST_METHOD_GET,
            headers=headers,
            token=workos.api_key,
        )

        return WorkOSUser.construct_from_response(response).to_dict()

    def list_users(
        self,
        email=None,
        organization=None,
        limit=None,
        before=None,
        after=None,
        order=None,
    ):
        """Get a list of all of your existing users matching the criteria specified.

        Kwargs:
            email (str): Filter Users by their email. (Optional)
            organization (list): Filter Users by the organization they are members of. (Optional)
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
            "organization": organization,
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
            "method": Users.list_users,
        }

        if "default_limit" in locals():
            if "metadata" in response and "params" in response["metadata"]:
                response["metadata"]["params"]["default_limit"] = default_limit
            else:
                response["metadata"] = {"params": {"default_limit": default_limit}}

        return self.construct_from_response(response)

    def add_user_to_organization(self, user, organization):
        """Adds a User as a member of the given Organization.

        Kwargs:
            user (str): The unique ID of the User.
            organization (str): Unique ID of the Organization.

        Returns:
            dict: User response from WorkOS.
        """

        headers = {}

        response = self.request_helper.request(
            USER_ORGANIZATION_PATH.format(user, organization),
            method=REQUEST_METHOD_POST,
            headers=headers,
            token=workos.api_key,
        )

        return WorkOSUser.construct_from_response(response).to_dict()

    def remove_user_from_organization(self, user, organization):
        """Removes a User from the given Organization.

        Kwargs:
            user (str): The unique ID of the User.
            organization (str): Unique ID of the Organization.

        Returns:
            dict: User response from WorkOS.
        """

        headers = {}

        response = self.request_helper.request(
            USER_ORGANIZATION_PATH.format(user, organization),
            method=REQUEST_METHOD_DELETE,
            headers=headers,
            token=workos.api_key,
        )

        return WorkOSUser.construct_from_response(response).to_dict()

    def authenticate_with_magic_auth(
        self,
        code,
        magic_auth_challenge_id,
        expires_in=None,
        ip_address=None,
        user_agent=None,
    ):
        """Authenticates a user by verifying a one-time code sent to the user's email address by the Magic Auth Send Code endpoint.

        Kwargs:
            code (str): The one-time code that was emailed to the user.
            magic_auth_challenge_id (str): The challenge ID returned from when the one-time code was sent to the user.
            expires_in (int): The length of the session in minutes. Defaults to 1 day, 1440. (Optional)
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
            "magic_auth_challenge_id": magic_auth_challenge_id,
            "grant_type": "urn:workos:oauth:grant-type:magic-auth:code",
        }

        if expires_in:
            payload["expires_in"] = expires_in

        if ip_address:
            payload["ip_address"] = ip_address

        if user_agent:
            payload["user_agent"] = user_agent

        response = self.request_helper.request(
            USER_SESSION_TOKEN_PATH,
            method=REQUEST_METHOD_POST,
            headers=headers,
            params=payload,
        )

        return WorkOSAuthenticationResponse.construct_from_response(response).to_dict()

    def authenticate_with_password(
        self,
        email,
        password,
        expires_in=None,
        ip_address=None,
        user_agent=None,
    ):
        """Authenticates a user with email and password and optionally creates a session.

        Kwargs:
            email (str): The email address of the user.
            password (str): The password of the user.
            expires_in (int): The length of the session in minutes. Defaults to 1 day, 1440. (Optional)
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

        if expires_in:
            payload["expires_in"] = expires_in

        if ip_address:
            payload["ip_address"] = ip_address

        if user_agent:
            payload["user_agent"] = user_agent

        response = self.request_helper.request(
            USER_SESSION_TOKEN_PATH,
            method=REQUEST_METHOD_POST,
            headers=headers,
            params=payload,
        )

        return WorkOSAuthenticationResponse.construct_from_response(response).to_dict()

    def authenticate_with_code(
        self,
        code,
        expires_in=None,
        ip_address=None,
        user_agent=None,
    ):
        """Authenticates an OAuth user or a managed SSO user that is logging in through SSO,
            and optionally creates a session.

        Kwargs:
            code (str): The authorization value which was passed back as a query parameter in the callback to the Redirect URI.
            expires_in (int): The length of the session in minutes. Defaults to 1 day, 1440. (Optional)
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

        if expires_in:
            payload["expires_in"] = expires_in

        if ip_address:
            payload["ip_address"] = ip_address

        if user_agent:
            payload["user_agent"] = user_agent

        response = self.request_helper.request(
            USER_SESSION_TOKEN_PATH,
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
        user,
    ):
        """Sends a verification email to the provided user.

        Kwargs:
            user (str): The unique ID of the User whose email address will be verified.

        Returns:
            dict: MagicAuthChallenge response from WorkOS.
        """

        headers = {}

        response = self.request_helper.request(
            USER_SEND_VERIFICATION_EMAIL_PATH.format(user),
            method=REQUEST_METHOD_POST,
            headers=headers,
            token=workos.api_key,
        )

        return WorkOSUser.construct_from_response(response).to_dict()

    def verify_email(
        self,
        magic_auth_challenge_id,
        code,
    ):
        """Verifies user email using one-time code that was sent to the user.

        Kwargs:
            magic_auth_challenge_id (str): The challenge ID returned from the send verification email endpoint.

            code (str): The unique ID of the User whose email address will be verified.

        Returns:
            dict: User response from WorkOS.
        """

        headers = {}

        payload = {
            "magic_auth_challenge_id": magic_auth_challenge_id,
            "code": code,
        }

        response = self.request_helper.request(
            USER_VERIFY_EMAIL_PATH,
            method=REQUEST_METHOD_POST,
            headers=headers,
            params=payload,
            token=workos.api_key,
        )

        return WorkOSUser.construct_from_response(response).to_dict()

    def send_magic_auth_code(
        self,
        email,
    ):
        """Creates a one-time Magic Auth code and emails it to the user.

        Kwargs:
            email (str): The email address the one-time code will be sent to.

        Returns:
            dict: MagicAuthChallenge response from WorkOS.
        """

        headers = {}

        payload = {
            "email_address": email,
        }

        response = self.request_helper.request(
            USER_SEND_MAGIC_AUTH_PATH,
            method=REQUEST_METHOD_POST,
            headers=headers,
            params=payload,
            token=workos.api_key,
        )

        return WorkOSUser.construct_from_response(response).to_dict()
