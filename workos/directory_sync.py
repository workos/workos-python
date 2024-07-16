from warnings import warn
import workos
from workos.utils.pagination_order import Order
from workos.utils.request import (
    RequestHelper,
    REQUEST_METHOD_DELETE,
    REQUEST_METHOD_GET,
)

from workos.utils.validation import DIRECTORY_SYNC_MODULE, validate_settings
from workos.resources.directory_sync import (
    DirectoryGroup,
    Directory,
    DirectoryUser,
)
from workos.resources.list import ListArgs, ListPage, WorkOsListResource


RESPONSE_LIMIT = 10


class DirectorySync:
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
        self,
        directory=None,
        group=None,
        limit=None,
        before=None,
        after=None,
        order=None,
    ) -> WorkOsListResource[DirectoryUser]:
        """Gets a list of provisioned Users for a Directory.

        Note, either 'directory' or 'group' must be provided.

        Args:
            directory (str): Directory unique identifier.
            group (str): Directory Group unique identifier.
            limit (int): Maximum number of records to return.
            before (str): Pagination cursor to receive records before a provided Directory ID.
            after (str): Pagination cursor to receive records after a provided Directory ID.
            order (Order): Sort records in either ascending or descending order by created_at timestamp.

        Returns:
            dict: Directory Users response from WorkOS.
        """

        if limit is None:
            limit = RESPONSE_LIMIT
            default_limit = True

        params = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order or "desc",
        }

        if group is not None:
            params["group"] = group
        if directory is not None:
            params["directory"] = directory

        if order is not None:
            if isinstance(order, Order):
                params["order"] = str(order.value)
            elif order == "asc" or order == "desc":
                params["order"] = order
            else:
                raise ValueError("Parameter order must be of enum type Order")

        response = self.request_helper.request(
            "directory_users",
            method=REQUEST_METHOD_GET,
            params=params,
            token=workos.api_key,
        )

        return WorkOsListResource(
            list_method=self.list_users,
            list_args=ListArgs.model_validate(params),
            **ListPage[DirectoryUser](**response).model_dump()
        )

    def list_groups(
        self,
        directory=None,
        user=None,
        limit=None,
        before=None,
        after=None,
        order=None,
    ) -> WorkOsListResource[DirectoryGroup]:
        """Gets a list of provisioned Groups for a Directory .

        Note, either 'directory' or 'user' must be provided.

        Args:
            directory (str): Directory unique identifier.
            user (str): Directory User unique identifier.
            limit (int): Maximum number of records to return.
            before (str): Pagination cursor to receive records before a provided Directory ID.
            after (str): Pagination cursor to receive records after a provided Directory ID.
            order (Order): Sort records in either ascending or descending order by created_at timestamp.

        Returns:
            dict: Directory Groups response from WorkOS.
        """
        if limit is None:
            limit = RESPONSE_LIMIT
            default_limit = True

        params = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order or "desc",
        }
        if user is not None:
            params["user"] = user
        if directory is not None:
            params["directory"] = directory

            if order is not None:
                if isinstance(order, Order):
                    params["order"] = str(order.value)
                elif order == "asc" or order == "desc":
                    params["order"] = order
                else:
                    raise ValueError("Parameter order must be of enum type Order")

        response = self.request_helper.request(
            "directory_groups",
            method=REQUEST_METHOD_GET,
            params=params,
            token=workos.api_key,
        )


        return WorkOsListResource(
            list_method=self.list_groups,
            list_args=ListArgs.model_validate(params),
            **ListPage[DirectoryGroup](**response).model_dump()
        )

    def get_user(self, user):
        """Gets details for a single provisioned Directory User.

        Args:
            user (str): Directory User unique identifier.

        Returns:
            dict: Directory User response from WorkOS.
        """
        response = self.request_helper.request(
            "directory_users/{user}".format(user=user),
            method=REQUEST_METHOD_GET,
            token=workos.api_key,
        )

        return DirectoryUser.model_validate(response)

    def get_group(self, group):
        """Gets details for a single provisioned Directory Group.

        Args:
            group (str): Directory Group unique identifier.

        Returns:
            dict: Directory Group response from WorkOS.
        """
        response = self.request_helper.request(
            "directory_groups/{group}".format(group=group),
            method=REQUEST_METHOD_GET,
            token=workos.api_key,
        )

        return DirectoryGroup.model_validate(response)

    def get_directory(self, directory):
        """Gets details for a single Directory

        Args:
            directory (str): Directory unique identifier.

        Returns:
            dict: Directory response from WorkOS

        """

        response = self.request_helper.request(
            "directories/{directory}".format(directory=directory),
            method=REQUEST_METHOD_GET,
            token=workos.api_key,
        )

        return Directory.model_validate(response)

    def list_directories(
        self,
        domain=None,
        search=None,
        limit=None,
        before=None,
        after=None,
        organization=None,
        order=None,
    ) -> WorkOsListResource[Directory]:
        """Gets details for existing Directories.

        Args:
            domain (str): Domain of a Directory. (Optional)
            organization: ID of an Organization (Optional)
            search (str): Searchable text for a Directory. (Optional)
            limit (int): Maximum number of records to return. (Optional)
            before (str): Pagination cursor to receive records before a provided Directory ID. (Optional)
            after (str): Pagination cursor to receive records after a provided Directory ID. (Optional)
            order (Order): Sort records in either ascending or descending order by created_at timestamp.

        Returns:
            dict: Directories response from WorkOS.
        """

        if limit is None:
            limit = RESPONSE_LIMIT
            default_limit = True

        params = {
            "domain": domain,
            "organization_id": organization,
            "search": search,
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
            "directories",
            method=REQUEST_METHOD_GET,
            params=params,
            token=workos.api_key,
        )

        return WorkOsListResource(
            list_method=self.list_directories,
            list_args=ListArgs.model_validate(params),
            **ListPage[Directory](**response).model_dump()
        )

    def delete_directory(self, directory):
        """Delete one existing Directory.

        Args:
            directory (str): The ID of the directory to be deleted. (Required)

        Returns:
            dict: Directories response from WorkOS.
        """
        response = self.request_helper.request(
            "directories/{directory}".format(directory=directory),
            method=REQUEST_METHOD_DELETE,
            token=workos.api_key,
        )

        return Directory.model_validate(response)
