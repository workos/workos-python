import workos
from workos.resources.list import WorkOSListResource
from workos.resources.users import (
    WorkOSUser,
)
from workos.utils.pagination_order import Order
from workos.utils.request import (
    RequestHelper,
    REQUEST_METHOD_POST,
    REQUEST_METHOD_GET,
)
from workos.utils.validation import validate_settings, USERS_MODULE

USER_PATH = "users"

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
            "{0}/{1}".format(USER_PATH, user),
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
