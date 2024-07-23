from typing import Optional, Protocol
import workos
from workos.utils.pagination_order import PaginationOrder
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


class DirectoryListFilters(ListArgs, total=False):
    search: Optional[str]
    organization_id: Optional[str]
    domain: Optional[str]


class DirectoryUserListFilters(
    ListArgs,
    total=False,
):
    group: Optional[str]
    directory: Optional[str]


class DirectoryGroupListFilters(ListArgs, total=False):
    user: Optional[str]
    directory: Optional[str]


class DirectorySyncModule(Protocol):
    def list_users(
        self,
        directory: Optional[str] = None,
        group: Optional[str] = None,
        limit: int = RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> WorkOsListResource[DirectoryUser, DirectoryUserListFilters]: ...

    def list_groups(
        self,
        directory: Optional[str] = None,
        user: Optional[str] = None,
        limit: int = RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> WorkOsListResource[DirectoryGroup, DirectoryGroupListFilters]: ...

    def get_user(self, user: str) -> DirectoryUser: ...

    def get_group(self, group: str) -> DirectoryGroup: ...

    def get_directory(self, directory: str) -> Directory: ...

    def list_directories(
        self,
        domain: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        organization: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> WorkOsListResource[Directory, DirectoryListFilters]: ...

    def delete_directory(self, directory: str) -> None: ...


class DirectorySync(DirectorySyncModule):
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
        directory: Optional[str] = None,
        group: Optional[str] = None,
        limit: int = RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> WorkOsListResource[DirectoryUser, DirectoryUserListFilters]:
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

        list_params: DirectoryUserListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        if group is not None:
            list_params["group"] = group
        if directory is not None:
            list_params["directory"] = directory

        response = self.request_helper.request(
            "directory_users",
            method=REQUEST_METHOD_GET,
            params=list_params,
            token=workos.api_key,
        )

        return WorkOsListResource(
            list_method=self.list_users,
            list_args=list_params,
            **ListPage[DirectoryUser](**response).model_dump(),
        )

    def list_groups(
        self,
        directory: Optional[str] = None,
        user: Optional[str] = None,
        limit: int = RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> WorkOsListResource[DirectoryGroup, DirectoryGroupListFilters]:
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
        list_params: DirectoryGroupListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        if user is not None:
            list_params["user"] = user
        if directory is not None:
            list_params["directory"] = directory

        response = self.request_helper.request(
            "directory_groups",
            method=REQUEST_METHOD_GET,
            params=list_params,
            token=workos.api_key,
        )

        return WorkOsListResource(
            list_method=self.list_groups,
            list_args=list_params,
            **ListPage[DirectoryGroup](**response).model_dump(),
        )

    def get_user(self, user: str):
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

    def get_group(self, group: str):
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

    def get_directory(self, directory: str):
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
        domain: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        organization: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> WorkOsListResource[Directory, DirectoryListFilters]:
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

        list_params: DirectoryListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
            "domain": domain,
            "organization_id": organization,
            "search": search,
        }

        response = self.request_helper.request(
            "directories",
            method=REQUEST_METHOD_GET,
            params=list_params,
            token=workos.api_key,
        )
        return WorkOsListResource(
            list_method=self.list_directories,
            list_args=list_params,
            **ListPage[Directory](**response).model_dump(),
        )

    def delete_directory(self, directory: str):
        """Delete one existing Directory.

        Args:
            directory (str): The ID of the directory to be deleted. (Required)

        Returns:
            None
        """
        self.request_helper.request(
            "directories/{directory}".format(directory=directory),
            method=REQUEST_METHOD_DELETE,
            token=workos.api_key,
        )
