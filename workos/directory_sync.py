from typing import Optional, Protocol
import workos
from workos.typing.sync_or_async import SyncOrAsync
from workos.utils.http_client import AsyncHTTPClient, SyncHTTPClient
from workos.utils.pagination_order import PaginationOrder
from workos.utils.request_helper import (
    DEFAULT_LIST_RESPONSE_LIMIT,
    REQUEST_METHOD_DELETE,
    REQUEST_METHOD_GET,
)
from workos.utils.validation import DIRECTORY_SYNC_MODULE, validate_settings
from workos.resources.directory_sync import (
    DirectoryGroup,
    Directory,
    DirectoryUserWithGroups,
)
from workos.resources.list import (
    ListArgs,
    ListMetadata,
    ListPage,
    AsyncWorkOsListResource,
    SyncOrAsyncListResource,
    WorkOsListResource,
)


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
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> SyncOrAsyncListResource: ...

    def list_groups(
        self,
        directory: Optional[str] = None,
        user: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> SyncOrAsyncListResource: ...

    def get_user(self, user: str) -> SyncOrAsync[DirectoryUserWithGroups]: ...

    def get_group(self, group: str) -> SyncOrAsync[DirectoryGroup]: ...

    def get_directory(self, directory: str) -> SyncOrAsync[Directory]: ...

    def list_directories(
        self,
        search: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        organization_id: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> SyncOrAsyncListResource: ...

    def delete_directory(self, directory: str) -> SyncOrAsync[None]: ...


class DirectorySync(DirectorySyncModule):
    """Offers methods through the WorkOS Directory Sync service."""

    _http_client: SyncHTTPClient

    @validate_settings(DIRECTORY_SYNC_MODULE)
    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def list_users(
        self,
        directory: Optional[str] = None,
        group: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> WorkOsListResource[
        DirectoryUserWithGroups, DirectoryUserListFilters, ListMetadata
    ]:
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

        response = self._http_client.request(
            "directory_users",
            method=REQUEST_METHOD_GET,
            params=list_params,
            token=workos.api_key,
        )

        return WorkOsListResource(
            list_method=self.list_users,
            list_args=list_params,
            **ListPage[DirectoryUserWithGroups](**response).model_dump(),
        )

    def list_groups(
        self,
        directory: Optional[str] = None,
        user: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> WorkOsListResource[DirectoryGroup, DirectoryGroupListFilters, ListMetadata]:
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

        response = self._http_client.request(
            "directory_groups",
            method=REQUEST_METHOD_GET,
            params=list_params,
            token=workos.api_key,
        )

        return WorkOsListResource[
            DirectoryGroup, DirectoryGroupListFilters, ListMetadata
        ](
            list_method=self.list_groups,
            list_args=list_params,
            **ListPage[DirectoryGroup](**response).model_dump(),
        )

    def get_user(self, user: str) -> DirectoryUserWithGroups:
        """Gets details for a single provisioned Directory User.

        Args:
            user (str): Directory User unique identifier.

        Returns:
            dict: Directory User response from WorkOS.
        """
        response = self._http_client.request(
            "directory_users/{user}".format(user=user),
            method=REQUEST_METHOD_GET,
            token=workos.api_key,
        )

        return DirectoryUserWithGroups.model_validate(response)

    def get_group(self, group: str) -> DirectoryGroup:
        """Gets details for a single provisioned Directory Group.

        Args:
            group (str): Directory Group unique identifier.

        Returns:
            dict: Directory Group response from WorkOS.
        """
        response = self._http_client.request(
            "directory_groups/{group}".format(group=group),
            method=REQUEST_METHOD_GET,
            token=workos.api_key,
        )
        return DirectoryGroup.model_validate(response)

    def get_directory(self, directory: str) -> Directory:
        """Gets details for a single Directory

        Args:
            directory (str): Directory unique identifier.

        Returns:
            dict: Directory response from WorkOS

        """

        response = self._http_client.request(
            "directories/{directory}".format(directory=directory),
            method=REQUEST_METHOD_GET,
            token=workos.api_key,
        )

        return Directory.model_validate(response)

    def list_directories(
        self,
        search: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        organization_id: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> WorkOsListResource[Directory, DirectoryListFilters, ListMetadata]:
        """Gets details for existing Directories.

        Args:
            organization_id: ID of an Organization (Optional)
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
            "organization_id": organization_id,
            "search": search,
        }

        response = self._http_client.request(
            "directories",
            method=REQUEST_METHOD_GET,
            params=list_params,
            token=workos.api_key,
        )
        return WorkOsListResource[Directory, DirectoryListFilters, ListMetadata](
            list_method=self.list_directories,
            list_args=list_params,
            **ListPage[Directory](**response).model_dump(),
        )

    def delete_directory(self, directory: str) -> None:
        """Delete one existing Directory.

        Args:
            directory (str): The ID of the directory to be deleted. (Required)

        Returns:
            None
        """
        self._http_client.request(
            "directories/{directory}".format(directory=directory),
            method=REQUEST_METHOD_DELETE,
            token=workos.api_key,
        )


class AsyncDirectorySync(DirectorySyncModule):
    """Offers methods through the WorkOS Directory Sync service."""

    _http_client: AsyncHTTPClient

    @validate_settings(DIRECTORY_SYNC_MODULE)
    def __init__(self, http_client: AsyncHTTPClient):
        self._http_client = http_client

    async def list_users(
        self,
        directory: Optional[str] = None,
        group: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> AsyncWorkOsListResource[
        DirectoryUserWithGroups, DirectoryUserListFilters, ListMetadata
    ]:
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

        response = await self._http_client.request(
            "directory_users",
            method=REQUEST_METHOD_GET,
            params=list_params,
            token=workos.api_key,
        )

        return AsyncWorkOsListResource(
            list_method=self.list_users,
            list_args=list_params,
            **ListPage[DirectoryUserWithGroups](**response).model_dump(),
        )

    async def list_groups(
        self,
        directory: Optional[str] = None,
        user: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> AsyncWorkOsListResource[
        DirectoryGroup, DirectoryGroupListFilters, ListMetadata
    ]:
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

        response = await self._http_client.request(
            "directory_groups",
            method=REQUEST_METHOD_GET,
            params=list_params,
            token=workos.api_key,
        )

        return AsyncWorkOsListResource[
            DirectoryGroup, DirectoryGroupListFilters, ListMetadata
        ](
            list_method=self.list_groups,
            list_args=list_params,
            **ListPage[DirectoryGroup](**response).model_dump(),
        )

    async def get_user(self, user: str) -> DirectoryUserWithGroups:
        """Gets details for a single provisioned Directory User.

        Args:
            user (str): Directory User unique identifier.

        Returns:
            dict: Directory User response from WorkOS.
        """
        response = await self._http_client.request(
            "directory_users/{user}".format(user=user),
            method=REQUEST_METHOD_GET,
            token=workos.api_key,
        )

        return DirectoryUserWithGroups.model_validate(response)

    async def get_group(self, group: str) -> DirectoryGroup:
        """Gets details for a single provisioned Directory Group.

        Args:
            group (str): Directory Group unique identifier.

        Returns:
            dict: Directory Group response from WorkOS.
        """
        response = await self._http_client.request(
            "directory_groups/{group}".format(group=group),
            method=REQUEST_METHOD_GET,
            token=workos.api_key,
        )
        return DirectoryGroup.model_validate(response)

    async def get_directory(self, directory: str) -> Directory:
        """Gets details for a single Directory

        Args:
            directory (str): Directory unique identifier.

        Returns:
            dict: Directory response from WorkOS

        """

        response = await self._http_client.request(
            "directories/{directory}".format(directory=directory),
            method=REQUEST_METHOD_GET,
            token=workos.api_key,
        )

        return Directory.model_validate(response)

    async def list_directories(
        self,
        search: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        organization_id: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> AsyncWorkOsListResource[Directory, DirectoryListFilters, ListMetadata]:
        """Gets details for existing Directories.

        Args:
            domain (str): Domain of a Directory. (Optional)
            organization_id: ID of an Organization (Optional)
            search (str): Searchable text for a Directory. (Optional)
            limit (int): Maximum number of records to return. (Optional)
            before (str): Pagination cursor to receive records before a provided Directory ID. (Optional)
            after (str): Pagination cursor to receive records after a provided Directory ID. (Optional)
            order (Order): Sort records in either ascending or descending order by created_at timestamp.

        Returns:
            dict: Directories response from WorkOS.
        """

        list_params: DirectoryListFilters = {
            "organization_id": organization_id,
            "search": search,
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        response = await self._http_client.request(
            "directories",
            method=REQUEST_METHOD_GET,
            params=list_params,
            token=workos.api_key,
        )
        return AsyncWorkOsListResource[Directory, DirectoryListFilters, ListMetadata](
            list_method=self.list_directories,
            list_args=list_params,
            **ListPage[Directory](**response).model_dump(),
        )

    async def delete_directory(self, directory: str) -> None:
        """Delete one existing Directory.

        Args:
            directory (str): The ID of the directory to be deleted. (Required)

        Returns:
            None
        """
        await self._http_client.request(
            "directories/{directory}".format(directory=directory),
            method=REQUEST_METHOD_DELETE,
            token=workos.api_key,
        )
