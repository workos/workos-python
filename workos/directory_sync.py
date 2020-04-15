import workos
from workos.utils.request import RequestHelper, REQUEST_METHOD_GET
from workos.utils.validation import DIRECTORY_SYNC_MODULE, validate_settings

RESPONSE_LIMIT = 10


class DirectorySync(object):
    """Offers methods through the WorkOS Directory Sync service."""

    @validate_settings(DIRECTORY_SYNC_MODULE)
    def __init__(self):
        pass

    @property
    def request_helper(self):
        if not getattr(self, "_request_helper", None):
            self._request_helper = RequestHelper()
        return self._request_helper

    def get_directory_users(
        self, directory_endpoint_id, limit=RESPONSE_LIMIT, before=None, after=None
    ):
        """Gets a list of provisioned users for a directory endpoint.

        Args:
            directory_endpoint_id (str): Directory Endpoint unique identifier.
            limit (int): Maximum number of records to return.
            before (str): Pagination cursor to receive records before a provided directory endpoint id.
            after (str): Pagination cursor to receive records after a provided directory endpoint id.

        Returns:
            dict: Directory users response from WorkOS.
        """
        params = {"limit": limit, "before": before, "after": after}
        return self.request_helper.request(
            "directories/{directory_endpoint_id}/users".format(
                directory_endpoint_id=directory_endpoint_id
            ),
            method=REQUEST_METHOD_GET,
            params=params,
            token=workos.api_key,
        )

    def get_directory_groups(
        self, directory_endpoint_id, limit=RESPONSE_LIMIT, before=None, after=None
    ):
        """Gets a list of provisioned groups for a directory endpoint.

        Args:
            directory_endpoint_id (str): Directory Endpoint unique identifier.
            limit (int): Maximum number of records to return.
            before (str): Pagination cursor to receive records before a provided directory endpoint id.
            after (str): Pagination cursor to receive records after a provided directory endpoint id.

        Returns:
            dict: Directory groups response from WorkOS.
        """
        params = {"limit": limit, "before": before, "after": after}
        return self.request_helper.request(
            "directories/{directory_endpoint_id}/groups".format(
                directory_endpoint_id=directory_endpoint_id
            ),
            method=REQUEST_METHOD_GET,
            params=params,
            token=workos.api_key,
        )

    def get_directory_user(self, directory_endpoint_id, directory_user_id):
        """Gets details for a single provisioned directory user.

        Args:
            directory_endpoint_id (str): Directory Endpoint unique identifier.
            directory_user_id(str): Directory User unique identifier.

        Returns:
            dict: Directory user response from WorkOS.
        """
        return self.request_helper.request(
            "directories/{directory_endpoint_id}/users/{directory_user_id}".format(
                directory_endpoint_id=directory_endpoint_id,
                directory_user_id=directory_user_id,
            ),
            method=REQUEST_METHOD_GET,
            token=workos.api_key,
        )

    def get_directory_user_groups(self, directory_endpoint_id, directory_user_id):
        """Gets details for a directory user's provisioned groups.

        Args:
            directory_endpoint_id (str): Directory Endpoint unique identifier.
            directory_user_id(str): Directory User unique identifier.

        Returns:
            dict: Directory user's groups response from WorkOS.
        """
        return self.request_helper.request(
            "directories/{directory_endpoint_id}/users/{directory_user_id}/groups".format(
                directory_endpoint_id=directory_endpoint_id,
                directory_user_id=directory_user_id,
            ),
            method=REQUEST_METHOD_GET,
            token=workos.api_key,
        )
