from typing import Any, Dict, Optional, Protocol

from workos.types.authorization.permission import Permission
from workos.types.list_resource import (
    ListArgs,
    ListMetadata,
    ListPage,
    WorkOSListResource,
)
from workos.typing.sync_or_async import SyncOrAsync
from workos.utils.http_client import AsyncHTTPClient, SyncHTTPClient
from workos.utils.pagination_order import PaginationOrder
from workos.utils.request_helper import (
    DEFAULT_LIST_RESPONSE_LIMIT,
    REQUEST_METHOD_DELETE,
    REQUEST_METHOD_GET,
    REQUEST_METHOD_PATCH,
    REQUEST_METHOD_POST,
)

AUTHORIZATION_PERMISSIONS_PATH = "authorization/permissions"


class PermissionListFilters(ListArgs, total=False):
    pass


PermissionsListResource = WorkOSListResource[
    Permission, PermissionListFilters, ListMetadata
]


class AuthorizationModule(Protocol):
    """Offers methods through the WorkOS Authorization service."""

    def create_permission(
        self,
        *,
        slug: str,
        name: str,
        description: Optional[str] = None,
    ) -> SyncOrAsync[Permission]: ...

    def list_permissions(
        self,
        *,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> SyncOrAsync[PermissionsListResource]: ...

    def get_permission(self, slug: str) -> SyncOrAsync[Permission]: ...

    def update_permission(
        self,
        slug: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> SyncOrAsync[Permission]: ...

    def delete_permission(self, slug: str) -> SyncOrAsync[None]: ...


class Authorization(AuthorizationModule):
    _http_client: SyncHTTPClient

    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def create_permission(
        self,
        *,
        slug: str,
        name: str,
        description: Optional[str] = None,
    ) -> Permission:
        json: Dict[str, Any] = {"slug": slug, "name": name}
        if description is not None:
            json["description"] = description

        response = self._http_client.request(
            AUTHORIZATION_PERMISSIONS_PATH,
            method=REQUEST_METHOD_POST,
            json=json,
        )

        return Permission.model_validate(response)

    def list_permissions(
        self,
        *,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> PermissionsListResource:
        list_params: PermissionListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        response = self._http_client.request(
            AUTHORIZATION_PERMISSIONS_PATH,
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        return WorkOSListResource[Permission, PermissionListFilters, ListMetadata](
            list_method=self.list_permissions,
            list_args=list_params,
            **ListPage[Permission](**response).model_dump(),
        )

    def get_permission(self, slug: str) -> Permission:
        response = self._http_client.request(
            f"{AUTHORIZATION_PERMISSIONS_PATH}/{slug}",
            method=REQUEST_METHOD_GET,
        )

        return Permission.model_validate(response)

    def update_permission(
        self,
        slug: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Permission:
        json: Dict[str, Any] = {}
        if name is not None:
            json["name"] = name
        if description is not None:
            json["description"] = description

        response = self._http_client.request(
            f"{AUTHORIZATION_PERMISSIONS_PATH}/{slug}",
            method=REQUEST_METHOD_PATCH,
            json=json,
        )

        return Permission.model_validate(response)

    def delete_permission(self, slug: str) -> None:
        self._http_client.request(
            f"{AUTHORIZATION_PERMISSIONS_PATH}/{slug}",
            method=REQUEST_METHOD_DELETE,
        )


class AsyncAuthorization(AuthorizationModule):
    _http_client: AsyncHTTPClient

    def __init__(self, http_client: AsyncHTTPClient):
        self._http_client = http_client

    async def create_permission(
        self,
        *,
        slug: str,
        name: str,
        description: Optional[str] = None,
    ) -> Permission:
        json: Dict[str, Any] = {"slug": slug, "name": name}
        if description is not None:
            json["description"] = description

        response = await self._http_client.request(
            AUTHORIZATION_PERMISSIONS_PATH,
            method=REQUEST_METHOD_POST,
            json=json,
        )

        return Permission.model_validate(response)

    async def list_permissions(
        self,
        *,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> PermissionsListResource:
        list_params: PermissionListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        response = await self._http_client.request(
            AUTHORIZATION_PERMISSIONS_PATH,
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        return WorkOSListResource[Permission, PermissionListFilters, ListMetadata](
            list_method=self.list_permissions,
            list_args=list_params,
            **ListPage[Permission](**response).model_dump(),
        )

    async def get_permission(self, slug: str) -> Permission:
        response = await self._http_client.request(
            f"{AUTHORIZATION_PERMISSIONS_PATH}/{slug}",
            method=REQUEST_METHOD_GET,
        )

        return Permission.model_validate(response)

    async def update_permission(
        self,
        slug: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Permission:
        json: Dict[str, Any] = {}
        if name is not None:
            json["name"] = name
        if description is not None:
            json["description"] = description

        response = await self._http_client.request(
            f"{AUTHORIZATION_PERMISSIONS_PATH}/{slug}",
            method=REQUEST_METHOD_PATCH,
            json=json,
        )

        return Permission.model_validate(response)

    async def delete_permission(self, slug: str) -> None:
        await self._http_client.request(
            f"{AUTHORIZATION_PERMISSIONS_PATH}/{slug}",
            method=REQUEST_METHOD_DELETE,
        )
