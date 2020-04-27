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

    def list_users(
        self, directory=None, group=None, limit=RESPONSE_LIMIT, before=None, after=None
    ):
        """Gets a list of provisioned Users for a Directory.

        Note, either 'directory' or 'group' must be provided.

        Args:
            directory (str): Directory unique identifier.
            group (str): Directory Group unique identifier.
            limit (int): Maximum number of records to return.
            before (str): Pagination cursor to receive records before a provided Directory ID.
            after (str): Pagination cursor to receive records after a provided Directory ID.

        Returns:
            dict: Directory Users response from WorkOS.
        """
        params = {"limit": limit, "before": before, "after": after}
        if group is not None:
            params["group"] = group
        if directory is not None:
            params["directory"] = directory
        return self.request_helper.request(
            "directory_users",
            method=REQUEST_METHOD_GET,
            params=params,
            token=workos.api_key,
        )

    def list_groups(
        self, directory=None, user=None, limit=RESPONSE_LIMIT, before=None, after=None
    ):
        """Gets a list of provisioned Groups for a Directory .

        Note, either 'directory' or 'user' must be provided.

        Args:
            directory (str): Directory unique identifier.
            user (str): Directory User unique identifier.
            limit (int): Maximum number of records to return.
            before (str): Pagination cursor to receive records before a provided Directory ID.
            after (str): Pagination cursor to receive records after a provided Directory ID.

        Returns:
            dict: Directory Groups response from WorkOS.
        """
        params = {"limit": limit, "before": before, "after": after}
        if user is not None:
            params["user"] = user
        if directory is not None:
            params["directory"] = directory
        return self.request_helper.request(
            "directory_groups",
            method=REQUEST_METHOD_GET,
            params=params,
            token=workos.api_key,
        )

    def get_user(self, user):
        """Gets details for a single provisioned Directory User.

        Args:
            user (str): Directory User unique identifier.

        Returns:
            dict: Directory User response from WorkOS.
        """
        return self.request_helper.request(
            "directory_users/{user}".format(user=user),
            method=REQUEST_METHOD_GET,
            token=workos.api_key,
        )

    def get_group(self, group):
        """Gets details for a single provisioned Directory Group.

        Args:
            group (str): Directory Group unique identifier.

        Returns:
            dict: Directory Group response from WorkOS.
        """
        return self.request_helper.request(
            "directory_groups/{group}".format(group=group),
            method=REQUEST_METHOD_GET,
            token=workos.api_key,
        )

    def list_directories(
        self, domain=None, search=None, limit=RESPONSE_LIMIT, before=None, after=None
    ):
        """Gets details for existing Directories.

        Args:
            domain (str): Domain of a Directory. (Optional)
            search (str): Searchable text for a Directory. (Optional)
            limit (int): Maximum number of records to return. (Optional)
            before (str): Pagination cursor to receive records before a provided Directory ID. (Optional)
            after (str): Pagination cursor to receive records after a provided Directory ID. (Optional)

        Returns:
            dict: Directories response from WorkOS.
        """
        params = {
            "domain": domain,
            "search": search,
            "limit": limit,
            "before": before,
            "after": after,
        }
        return self.request_helper.request(
            "directories",
            method=REQUEST_METHOD_GET,
            params=params,
            token=workos.api_key,
        )
