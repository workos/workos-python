from typing import Optional, Protocol

from workos.types.directory_sync.list_filters import (
    DirectoryGroupListFilters,
    DirectoryListFilters,
    DirectoryUserListFilters,
)
from workos.typing.sync_or_async import SyncOrAsync
from workos.utils.http_client import AsyncHTTPClient, SyncHTTPClient
from workos.utils.pagination_order import PaginationOrder
from workos.utils.request_helper import (
    DEFAULT_LIST_RESPONSE_LIMIT,
    REQUEST_METHOD_DELETE,
    REQUEST_METHOD_GET,
)
from workos.types.directory_sync import (
    DirectoryGroup,
    Directory,
    DirectoryUserWithGroups,
)
from workos.types.list_resource import ListMetadata, ListPage, WorkOSListResource

DirectoryUsersListResource = WorkOSListResource[
    DirectoryUserWithGroups, DirectoryUserListFilters, ListMetadata
]

DirectoryGroupsListResource = WorkOSListResource[
    DirectoryGroup, DirectoryGroupListFilters, ListMetadata
]

DirectoriesListResource = WorkOSListResource[
    Directory, DirectoryListFilters, ListMetadata
]


class DirectorySyncModule(Protocol):
    """Offers methods through the WorkOS Directory Sync service."""

    def list_users(
        self,
        *,
        directory_id: Optional[str] = None,
        group_id: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> SyncOrAsync[DirectoryUsersListResource]:
        """Gets a list of provisioned Users for a Directory.

        Note, either 'directory_id' or 'group_id' must be provided.

        Kwargs:
            directory_id (str): Directory unique identifier. (Optional)
            group_id (str): Directory Group unique identifier. (Optional)
            limit (int): Maximum number of records to return. (Optional)
            before (str): Pagination cursor to receive records before a provided Directory ID. (Optional)
            after (str): Pagination cursor to receive records after a provided Directory ID. (Optional)
            order (Literal["asc","desc"]): Sort records in either ascending or descending (default) order by created_at timestamp. (Optional)

        Returns:
            DirectoryUsersListResource: Directory Users response from WorkOS.
        """
        ...

    def list_groups(
        self,
        *,
        directory_id: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> SyncOrAsync[DirectoryGroupsListResource]:
        """Gets a list of provisioned Groups for a Directory .

        Note, either 'directory_id' or 'user_id' must be provided.

        Kwargs:
            directory_id (str): Directory unique identifier. (Optional)
            user_id (str): Directory User unique identifier. (Optional)
            limit (int): Maximum number of records to return. (Optional)
            before (str): Pagination cursor to receive records before a provided Directory ID. (Optional)
            after (str): Pagination cursor to receive records after a provided Directory ID. (Optional)
            order (Literal["asc","desc"]): Sort records in either ascending or descending (default) order by created_at timestamp. (Optional)

        Returns:
            DirectoryGroupsListResource: Directory Groups response from WorkOS.
        """
        ...

    def list_directories(
        self,
        *,
        search: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        organization_id: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> SyncOrAsync[DirectoriesListResource]:
        """Gets details for existing Directories.

        Kwargs:
            organization_id: ID of an Organization (Optional)
            search (str): Searchable text for a Directory. (Optional)
            limit (int): Maximum number of records to return. (Optional)
            before (str): Pagination cursor to receive records before a provided Directory ID. (Optional)
            after (str): Pagination cursor to receive records after a provided Directory ID. (Optional)
            order (Literal["asc","desc"]): Sort records in either ascending or descending (default) order by created_at timestamp. (Optional)

        Returns:
            DirectoriesListResource: Directories response from WorkOS.
        """
        ...

    def get_user(self, user_id: str) -> SyncOrAsync[DirectoryUserWithGroups]:
        """Gets details for a single provisioned Directory User.

        Args:
            user_id (str): Directory User unique identifier.

        Returns:
            DirectoryUserWithGroups: Directory User response from WorkOS.
        """
        ...

    def get_group(self, group_id: str) -> SyncOrAsync[DirectoryGroup]:
        """Gets details for a single provisioned Directory Group.

        Args:
            group_id (str): Directory Group unique identifier.

        Returns:
            DirectoryGroup: Directory Group response from WorkOS.
        """
        ...

    def get_directory(self, directory_id: str) -> SyncOrAsync[Directory]:
        """Gets details for a single Directory

        Args:
            directory_id (str): Directory unique identifier.

        Returns:
            Directory: Directory response from WorkOS
        """
        ...

    def delete_directory(self, directory_id: str) -> SyncOrAsync[None]:
        """Delete one existing Directory.

        Args:
            directory_id (str): Directory unique identifier.

        Returns:
            None
        """
        ...


class DirectorySync(DirectorySyncModule):
    _http_client: SyncHTTPClient

    def __init__(self, http_client: SyncHTTPClient) -> None:
        self._http_client = http_client

    def list_users(
        self,
        *,
        directory_id: Optional[str] = None,
        group_id: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> DirectoryUsersListResource:

        list_params: DirectoryUserListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        if group_id is not None:
            list_params["group"] = group_id
        if directory_id is not None:
            list_params["directory"] = directory_id

        response = self._http_client.request(
            "directory_users",
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        return WorkOSListResource(
            list_method=self.list_users,
            list_args=list_params,
            **ListPage[DirectoryUserWithGroups](**response).model_dump(),
        )

    def list_groups(
        self,
        *,
        directory_id: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> DirectoryGroupsListResource:
        list_params: DirectoryGroupListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        if user_id is not None:
            list_params["user"] = user_id
        if directory_id is not None:
            list_params["directory"] = directory_id

        response = self._http_client.request(
            "directory_groups",
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        return WorkOSListResource[
            DirectoryGroup, DirectoryGroupListFilters, ListMetadata
        ](
            list_method=self.list_groups,
            list_args=list_params,
            **ListPage[DirectoryGroup](**response).model_dump(),
        )

    def get_user(self, user_id: str) -> DirectoryUserWithGroups:
        response = self._http_client.request(
            "directory_users/{user}".format(user=user_id),
            method=REQUEST_METHOD_GET,
        )

        return DirectoryUserWithGroups.model_validate(response)

    def get_group(self, group_id: str) -> DirectoryGroup:
        response = self._http_client.request(
            "directory_groups/{group}".format(group=group_id),
            method=REQUEST_METHOD_GET,
        )
        return DirectoryGroup.model_validate(response)

    def get_directory(self, directory_id: str) -> Directory:
        response = self._http_client.request(
            "directories/{directory}".format(directory=directory_id),
            method=REQUEST_METHOD_GET,
        )

        return Directory.model_validate(response)

    def list_directories(
        self,
        *,
        search: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        organization_id: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> DirectoriesListResource:
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
        )
        return WorkOSListResource[Directory, DirectoryListFilters, ListMetadata](
            list_method=self.list_directories,
            list_args=list_params,
            **ListPage[Directory](**response).model_dump(),
        )

    def delete_directory(self, directory_id: str) -> None:
        self._http_client.request(
            "directories/{directory}".format(directory=directory_id),
            method=REQUEST_METHOD_DELETE,
        )


class AsyncDirectorySync(DirectorySyncModule):
    """Offers methods through the WorkOS Directory Sync service."""

    _http_client: AsyncHTTPClient

    def __init__(self, http_client: AsyncHTTPClient):
        self._http_client = http_client

    async def list_users(
        self,
        *,
        directory_id: Optional[str] = None,
        group_id: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> DirectoryUsersListResource:

        list_params: DirectoryUserListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        if group_id is not None:
            list_params["group"] = group_id
        if directory_id is not None:
            list_params["directory"] = directory_id

        response = await self._http_client.request(
            "directory_users",
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        return WorkOSListResource(
            list_method=self.list_users,
            list_args=list_params,
            **ListPage[DirectoryUserWithGroups](**response).model_dump(),
        )

    async def list_groups(
        self,
        *,
        directory_id: Optional[str] = None,
        user_id: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> DirectoryGroupsListResource:
        list_params: DirectoryGroupListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }
        if user_id is not None:
            list_params["user"] = user_id
        if directory_id is not None:
            list_params["directory"] = directory_id

        response = await self._http_client.request(
            "directory_groups",
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        return WorkOSListResource[
            DirectoryGroup, DirectoryGroupListFilters, ListMetadata
        ](
            list_method=self.list_groups,
            list_args=list_params,
            **ListPage[DirectoryGroup](**response).model_dump(),
        )

    async def get_user(self, user_id: str) -> DirectoryUserWithGroups:
        response = await self._http_client.request(
            "directory_users/{user}".format(user=user_id),
            method=REQUEST_METHOD_GET,
        )

        return DirectoryUserWithGroups.model_validate(response)

    async def get_group(self, group_id: str) -> DirectoryGroup:
        response = await self._http_client.request(
            "directory_groups/{group}".format(group=group_id),
            method=REQUEST_METHOD_GET,
        )
        return DirectoryGroup.model_validate(response)

    async def get_directory(self, directory_id: str) -> Directory:
        response = await self._http_client.request(
            "directories/{directory}".format(directory=directory_id),
            method=REQUEST_METHOD_GET,
        )

        return Directory.model_validate(response)

    async def list_directories(
        self,
        *,
        search: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        organization_id: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> DirectoriesListResource:
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
        )
        return WorkOSListResource[Directory, DirectoryListFilters, ListMetadata](
            list_method=self.list_directories,
            list_args=list_params,
            **ListPage[Directory](**response).model_dump(),
        )

    async def delete_directory(self, directory_id: str) -> None:
        await self._http_client.request(
            "directories/{directory}".format(directory=directory_id),
            method=REQUEST_METHOD_DELETE,
        )
