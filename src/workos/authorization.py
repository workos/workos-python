from typing import Any, Dict, Optional, Protocol, Sequence, Union

from pydantic import TypeAdapter
from typing_extensions import TypedDict

from workos.types.authorization.environment_role import (
    EnvironmentRole,
    EnvironmentRoleList,
)
from workos.types.authorization.organization_role import OrganizationRole
from workos.types.authorization.organization_membership import (
    AuthorizationOrganizationMembership,
)
from workos.types.authorization.permission import Permission
from workos.types.authorization.resource import Resource
from workos.types.authorization.role import Role, RoleList
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
    REQUEST_METHOD_PUT,
)

AUTHORIZATION_PERMISSIONS_PATH = "authorization/permissions"
AUTHORIZATION_RESOURCES_PATH = "authorization/resources"


class ParentResourceById(TypedDict):
    parent_resource_id: str


class ParentResourceByExternalId(TypedDict):
    parent_resource_external_id: str
    parent_resource_type_slug: str


ParentResource = Union[ParentResourceById, ParentResourceByExternalId]

_role_adapter: TypeAdapter[Role] = TypeAdapter(Role)


class PermissionListFilters(ListArgs, total=False):
    pass


PermissionsListResource = WorkOSListResource[
    Permission, PermissionListFilters, ListMetadata
]


class ResourcesForMembershipListFilters(ListArgs, total=False):
    organization_membership_id: str
    resource_type: Optional[str]
    parent_resource_id: Optional[str]
    parent_organization_id: Optional[str]
    parent_resource_type: Optional[str]
    parent_external_id: Optional[str]


ResourcesForMembershipListResource = WorkOSListResource[
    Resource, ResourcesForMembershipListFilters, ListMetadata
]


class MembershipsForResourceListFilters(ListArgs, total=False):
    resource_id: str
    organization_id: str
    resource_type: str
    external_id: str


MembershipsForResourceListResource = WorkOSListResource[
    AuthorizationOrganizationMembership,
    MembershipsForResourceListFilters,
    ListMetadata,
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

    # Organization Roles

    def create_organization_role(
        self,
        organization_id: str,
        *,
        slug: str,
        name: str,
        description: Optional[str] = None,
    ) -> SyncOrAsync[OrganizationRole]: ...

    def list_organization_roles(
        self, organization_id: str
    ) -> SyncOrAsync[RoleList]: ...

    def get_organization_role(
        self, organization_id: str, slug: str
    ) -> SyncOrAsync[Role]: ...

    def update_organization_role(
        self,
        organization_id: str,
        slug: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> SyncOrAsync[OrganizationRole]: ...

    def set_organization_role_permissions(
        self,
        organization_id: str,
        slug: str,
        *,
        permissions: Sequence[str],
    ) -> SyncOrAsync[OrganizationRole]: ...

    def add_organization_role_permission(
        self,
        organization_id: str,
        slug: str,
        *,
        permission_slug: str,
    ) -> SyncOrAsync[OrganizationRole]: ...

    def remove_organization_role_permission(
        self,
        organization_id: str,
        slug: str,
        *,
        permission_slug: str,
    ) -> SyncOrAsync[None]: ...

    # Environment Roles

    def create_environment_role(
        self,
        *,
        slug: str,
        name: str,
        description: Optional[str] = None,
    ) -> SyncOrAsync[EnvironmentRole]: ...

    def list_environment_roles(self) -> SyncOrAsync[EnvironmentRoleList]: ...

    def get_environment_role(self, slug: str) -> SyncOrAsync[EnvironmentRole]: ...

    def update_environment_role(
        self,
        slug: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> SyncOrAsync[EnvironmentRole]: ...

    def set_environment_role_permissions(
        self,
        slug: str,
        *,
        permissions: Sequence[str],
    ) -> SyncOrAsync[EnvironmentRole]: ...

    def add_environment_role_permission(
        self,
        slug: str,
        *,
        permission_slug: str,
    ) -> SyncOrAsync[EnvironmentRole]: ...

    # Resources

    def get_resource(self, resource_id: str) -> SyncOrAsync[Resource]: ...

    def create_resource(
        self,
        *,
        resource_type_slug: str,
        organization_id: str,
        external_id: str,
        name: str,
        parent: ParentResource,
        description: Optional[str] = None,
    ) -> SyncOrAsync[Resource]: ...

    def update_resource(
        self,
        resource_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> SyncOrAsync[Resource]: ...

    def delete_resource(
        self,
        resource_id: str,
        *,
        cascade_delete: Optional[bool] = None,
    ) -> SyncOrAsync[None]: ...

    # Resource-Membership Relationships

    def list_resources_for_membership(
        self,
        organization_membership_id: str,
        *,
        resource_type: Optional[str] = None,
        parent_resource_id: Optional[str] = None,
        parent_organization_id: Optional[str] = None,
        parent_resource_type: Optional[str] = None,
        parent_external_id: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        order: PaginationOrder = "desc",
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> SyncOrAsync[ResourcesForMembershipListResource]: ...

    def list_memberships_for_resource(
        self,
        resource_id: str,
        *,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        order: PaginationOrder = "desc",
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> SyncOrAsync[MembershipsForResourceListResource]: ...

    def list_memberships_for_resource_by_external_id(
        self,
        organization_id: str,
        resource_type: str,
        external_id: str,
        *,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        order: PaginationOrder = "desc",
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> SyncOrAsync[MembershipsForResourceListResource]: ...


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

    # Organization Roles

    def create_organization_role(
        self,
        organization_id: str,
        *,
        slug: str,
        name: str,
        description: Optional[str] = None,
    ) -> OrganizationRole:
        json: Dict[str, Any] = {"slug": slug, "name": name}
        if description is not None:
            json["description"] = description

        response = self._http_client.request(
            f"authorization/organizations/{organization_id}/roles",
            method=REQUEST_METHOD_POST,
            json=json,
        )

        return OrganizationRole.model_validate(response)

    def list_organization_roles(self, organization_id: str) -> RoleList:
        response = self._http_client.request(
            f"authorization/organizations/{organization_id}/roles",
            method=REQUEST_METHOD_GET,
        )

        return RoleList.model_validate(response)

    def get_organization_role(self, organization_id: str, slug: str) -> Role:
        response = self._http_client.request(
            f"authorization/organizations/{organization_id}/roles/{slug}",
            method=REQUEST_METHOD_GET,
        )

        return _role_adapter.validate_python(response)

    def update_organization_role(
        self,
        organization_id: str,
        slug: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> OrganizationRole:
        json: Dict[str, Any] = {}
        if name is not None:
            json["name"] = name
        if description is not None:
            json["description"] = description

        response = self._http_client.request(
            f"authorization/organizations/{organization_id}/roles/{slug}",
            method=REQUEST_METHOD_PATCH,
            json=json,
        )

        return OrganizationRole.model_validate(response)

    def set_organization_role_permissions(
        self,
        organization_id: str,
        slug: str,
        *,
        permissions: Sequence[str],
    ) -> OrganizationRole:
        response = self._http_client.request(
            f"authorization/organizations/{organization_id}/roles/{slug}/permissions",
            method=REQUEST_METHOD_PUT,
            json={"permissions": list(permissions)},
        )

        return OrganizationRole.model_validate(response)

    def add_organization_role_permission(
        self,
        organization_id: str,
        slug: str,
        *,
        permission_slug: str,
    ) -> OrganizationRole:
        response = self._http_client.request(
            f"authorization/organizations/{organization_id}/roles/{slug}/permissions",
            method=REQUEST_METHOD_POST,
            json={"slug": permission_slug},
        )

        return OrganizationRole.model_validate(response)

    def remove_organization_role_permission(
        self,
        organization_id: str,
        slug: str,
        *,
        permission_slug: str,
    ) -> None:
        self._http_client.request(
            f"authorization/organizations/{organization_id}/roles/{slug}/permissions/{permission_slug}",
            method=REQUEST_METHOD_DELETE,
        )

    # Environment Roles

    def create_environment_role(
        self,
        *,
        slug: str,
        name: str,
        description: Optional[str] = None,
    ) -> EnvironmentRole:
        json: Dict[str, Any] = {"slug": slug, "name": name}
        if description is not None:
            json["description"] = description

        response = self._http_client.request(
            "authorization/roles",
            method=REQUEST_METHOD_POST,
            json=json,
        )

        return EnvironmentRole.model_validate(response)

    def list_environment_roles(self) -> EnvironmentRoleList:
        response = self._http_client.request(
            "authorization/roles",
            method=REQUEST_METHOD_GET,
        )

        return EnvironmentRoleList.model_validate(response)

    def get_environment_role(self, slug: str) -> EnvironmentRole:
        response = self._http_client.request(
            f"authorization/roles/{slug}",
            method=REQUEST_METHOD_GET,
        )

        return EnvironmentRole.model_validate(response)

    def update_environment_role(
        self,
        slug: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> EnvironmentRole:
        json: Dict[str, Any] = {}
        if name is not None:
            json["name"] = name
        if description is not None:
            json["description"] = description

        response = self._http_client.request(
            f"authorization/roles/{slug}",
            method=REQUEST_METHOD_PATCH,
            json=json,
        )

        return EnvironmentRole.model_validate(response)

    def set_environment_role_permissions(
        self,
        slug: str,
        *,
        permissions: Sequence[str],
    ) -> EnvironmentRole:
        response = self._http_client.request(
            f"authorization/roles/{slug}/permissions",
            method=REQUEST_METHOD_PUT,
            json={"permissions": list(permissions)},
        )

        return EnvironmentRole.model_validate(response)

    def add_environment_role_permission(
        self,
        slug: str,
        *,
        permission_slug: str,
    ) -> EnvironmentRole:
        response = self._http_client.request(
            f"authorization/roles/{slug}/permissions",
            method=REQUEST_METHOD_POST,
            json={"slug": permission_slug},
        )

        return EnvironmentRole.model_validate(response)

    # Resources

    def get_resource(self, resource_id: str) -> Resource:
        response = self._http_client.request(
            f"{AUTHORIZATION_RESOURCES_PATH}/{resource_id}",
            method=REQUEST_METHOD_GET,
        )

        return Resource.model_validate(response)

    def create_resource(
        self,
        *,
        resource_type_slug: str,
        organization_id: str,
        external_id: str,
        name: str,
        parent: ParentResource,
        description: Optional[str] = None,
    ) -> Resource:
        json: Dict[str, Any] = {
            "resource_type_slug": resource_type_slug,
            "organization_id": organization_id,
            "external_id": external_id,
            "name": name,
            **parent,
        }
        if description is not None:
            json["description"] = description

        response = self._http_client.request(
            AUTHORIZATION_RESOURCES_PATH,
            method=REQUEST_METHOD_POST,
            json=json,
        )

        return Resource.model_validate(response)

    def update_resource(
        self,
        *,
        resource_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Resource:
        json: Dict[str, Any] = {}
        if name is not None:
            json["name"] = name
        if description is not None:
            json["description"] = description

        response = self._http_client.request(
            f"{AUTHORIZATION_RESOURCES_PATH}/{resource_id}",
            method=REQUEST_METHOD_PATCH,
            json=json,
        )

        return Resource.model_validate(response)

    def delete_resource(
        self,
        *,
        resource_id: str,
        cascade_delete: Optional[bool] = None,
    ) -> None:
        if cascade_delete is not None:
            self._http_client.delete_with_body(
                f"{AUTHORIZATION_RESOURCES_PATH}/{resource_id}",
                json={"cascade_delete": cascade_delete},
            )
        else:
            self._http_client.request(
                f"{AUTHORIZATION_RESOURCES_PATH}/{resource_id}",
                method=REQUEST_METHOD_DELETE,
            )

    # Resource-Membership Relationships

    def list_resources_for_membership(
        self,
        organization_membership_id: str,
        *,
        resource_type: Optional[str] = None,
        parent_resource_id: Optional[str] = None,
        parent_organization_id: Optional[str] = None,
        parent_resource_type: Optional[str] = None,
        parent_external_id: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        order: PaginationOrder = "desc",
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> ResourcesForMembershipListResource:
        list_params: ResourcesForMembershipListFilters = {
            "limit": limit,
            "order": order,
            "before": before,
            "after": after,
        }

        if resource_type is not None:
            list_params["resource_type"] = resource_type

        # Parent by internal ID and by external ID are mutually exclusive
        if parent_resource_id is not None and parent_organization_id is not None:
            raise ValueError(
                "parent_resource_id and parent_organization_id are mutually exclusive"
            )

        if parent_resource_id is not None:
            list_params["parent_resource_id"] = parent_resource_id
        elif parent_organization_id is not None:
            list_params["parent_organization_id"] = parent_organization_id
            if parent_resource_type is not None:
                list_params["parent_resource_type"] = parent_resource_type
            if parent_external_id is not None:
                list_params["parent_external_id"] = parent_external_id

        response = self._http_client.request(
            f"authorization/organization_memberships/{organization_membership_id}/resources",
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        # Add path param to list_args for pagination iterator
        list_params["organization_membership_id"] = organization_membership_id

        return ResourcesForMembershipListResource(
            list_method=self.list_resources_for_membership,
            list_args=list_params,
            **ListPage[Resource](**response).model_dump(),
        )

    def list_memberships_for_resource(
        self,
        resource_id: str,
        *,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        order: PaginationOrder = "desc",
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> MembershipsForResourceListResource:
        list_params: MembershipsForResourceListFilters = {
            "limit": limit,
            "order": order,
            "before": before,
            "after": after,
        }

        response = self._http_client.request(
            f"authorization/resources/{resource_id}/organization_memberships",
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        # Add path param to list_args for pagination iterator
        list_params["resource_id"] = resource_id

        return MembershipsForResourceListResource(
            list_method=self.list_memberships_for_resource,
            list_args=list_params,
            **ListPage[AuthorizationOrganizationMembership](**response).model_dump(),
        )

    def list_memberships_for_resource_by_external_id(
        self,
        organization_id: str,
        resource_type: str,
        external_id: str,
        *,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        order: PaginationOrder = "desc",
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> MembershipsForResourceListResource:
        list_params: MembershipsForResourceListFilters = {
            "limit": limit,
            "order": order,
            "before": before,
            "after": after,
        }

        response = self._http_client.request(
            f"authorization/organizations/{organization_id}/resources/{resource_type}/{external_id}/organization_memberships",
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        # Add path params to list_args for pagination iterator
        list_params["organization_id"] = organization_id
        list_params["resource_type"] = resource_type
        list_params["external_id"] = external_id

        return MembershipsForResourceListResource(
            list_method=self.list_memberships_for_resource_by_external_id,
            list_args=list_params,
            **ListPage[AuthorizationOrganizationMembership](**response).model_dump(),
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

    # Organization Roles

    async def create_organization_role(
        self,
        organization_id: str,
        *,
        slug: str,
        name: str,
        description: Optional[str] = None,
    ) -> OrganizationRole:
        json: Dict[str, Any] = {"slug": slug, "name": name}
        if description is not None:
            json["description"] = description

        response = await self._http_client.request(
            f"authorization/organizations/{organization_id}/roles",
            method=REQUEST_METHOD_POST,
            json=json,
        )

        return OrganizationRole.model_validate(response)

    async def list_organization_roles(self, organization_id: str) -> RoleList:
        response = await self._http_client.request(
            f"authorization/organizations/{organization_id}/roles",
            method=REQUEST_METHOD_GET,
        )

        return RoleList.model_validate(response)

    async def get_organization_role(self, organization_id: str, slug: str) -> Role:
        response = await self._http_client.request(
            f"authorization/organizations/{organization_id}/roles/{slug}",
            method=REQUEST_METHOD_GET,
        )

        return _role_adapter.validate_python(response)

    async def update_organization_role(
        self,
        organization_id: str,
        slug: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> OrganizationRole:
        json: Dict[str, Any] = {}
        if name is not None:
            json["name"] = name
        if description is not None:
            json["description"] = description

        response = await self._http_client.request(
            f"authorization/organizations/{organization_id}/roles/{slug}",
            method=REQUEST_METHOD_PATCH,
            json=json,
        )

        return OrganizationRole.model_validate(response)

    async def set_organization_role_permissions(
        self,
        organization_id: str,
        slug: str,
        *,
        permissions: Sequence[str],
    ) -> OrganizationRole:
        response = await self._http_client.request(
            f"authorization/organizations/{organization_id}/roles/{slug}/permissions",
            method=REQUEST_METHOD_PUT,
            json={"permissions": list(permissions)},
        )

        return OrganizationRole.model_validate(response)

    async def add_organization_role_permission(
        self,
        organization_id: str,
        slug: str,
        *,
        permission_slug: str,
    ) -> OrganizationRole:
        response = await self._http_client.request(
            f"authorization/organizations/{organization_id}/roles/{slug}/permissions",
            method=REQUEST_METHOD_POST,
            json={"slug": permission_slug},
        )

        return OrganizationRole.model_validate(response)

    async def remove_organization_role_permission(
        self,
        organization_id: str,
        slug: str,
        *,
        permission_slug: str,
    ) -> None:
        await self._http_client.request(
            f"authorization/organizations/{organization_id}/roles/{slug}/permissions/{permission_slug}",
            method=REQUEST_METHOD_DELETE,
        )

    # Environment Roles

    async def create_environment_role(
        self,
        *,
        slug: str,
        name: str,
        description: Optional[str] = None,
    ) -> EnvironmentRole:
        json: Dict[str, Any] = {"slug": slug, "name": name}
        if description is not None:
            json["description"] = description

        response = await self._http_client.request(
            "authorization/roles",
            method=REQUEST_METHOD_POST,
            json=json,
        )

        return EnvironmentRole.model_validate(response)

    async def list_environment_roles(self) -> EnvironmentRoleList:
        response = await self._http_client.request(
            "authorization/roles",
            method=REQUEST_METHOD_GET,
        )

        return EnvironmentRoleList.model_validate(response)

    async def get_environment_role(self, slug: str) -> EnvironmentRole:
        response = await self._http_client.request(
            f"authorization/roles/{slug}",
            method=REQUEST_METHOD_GET,
        )

        return EnvironmentRole.model_validate(response)

    async def update_environment_role(
        self,
        slug: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> EnvironmentRole:
        json: Dict[str, Any] = {}
        if name is not None:
            json["name"] = name
        if description is not None:
            json["description"] = description

        response = await self._http_client.request(
            f"authorization/roles/{slug}",
            method=REQUEST_METHOD_PATCH,
            json=json,
        )

        return EnvironmentRole.model_validate(response)

    async def set_environment_role_permissions(
        self,
        slug: str,
        *,
        permissions: Sequence[str],
    ) -> EnvironmentRole:
        response = await self._http_client.request(
            f"authorization/roles/{slug}/permissions",
            method=REQUEST_METHOD_PUT,
            json={"permissions": list(permissions)},
        )

        return EnvironmentRole.model_validate(response)

    async def add_environment_role_permission(
        self,
        slug: str,
        *,
        permission_slug: str,
    ) -> EnvironmentRole:
        response = await self._http_client.request(
            f"authorization/roles/{slug}/permissions",
            method=REQUEST_METHOD_POST,
            json={"slug": permission_slug},
        )

        return EnvironmentRole.model_validate(response)

    # Resources

    async def get_resource(self, resource_id: str) -> Resource:
        response = await self._http_client.request(
            f"{AUTHORIZATION_RESOURCES_PATH}/{resource_id}",
            method=REQUEST_METHOD_GET,
        )

        return Resource.model_validate(response)

    async def create_resource(
        self,
        *,
        resource_type_slug: str,
        organization_id: str,
        external_id: str,
        name: str,
        parent: ParentResource,
        description: Optional[str] = None,
    ) -> Resource:
        json: Dict[str, Any] = {
            "resource_type_slug": resource_type_slug,
            "organization_id": organization_id,
            "external_id": external_id,
            "name": name,
            **parent,
        }
        if description is not None:
            json["description"] = description

        response = await self._http_client.request(
            AUTHORIZATION_RESOURCES_PATH,
            method=REQUEST_METHOD_POST,
            json=json,
        )

        return Resource.model_validate(response)

    async def update_resource(
        self,
        resource_id: str,
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Resource:
        json: Dict[str, Any] = {}
        if name is not None:
            json["name"] = name
        if description is not None:
            json["description"] = description

        response = await self._http_client.request(
            f"{AUTHORIZATION_RESOURCES_PATH}/{resource_id}",
            method=REQUEST_METHOD_PATCH,
            json=json,
        )

        return Resource.model_validate(response)

    async def delete_resource(
        self,
        resource_id: str,
        *,
        cascade_delete: Optional[bool] = None,
    ) -> None:
        if cascade_delete is not None:
            await self._http_client.delete_with_body(
                f"{AUTHORIZATION_RESOURCES_PATH}/{resource_id}",
                json={"cascade_delete": cascade_delete},
            )
        else:
            await self._http_client.request(
                f"{AUTHORIZATION_RESOURCES_PATH}/{resource_id}",
                method=REQUEST_METHOD_DELETE,
            )

    # Resource-Membership Relationships

    async def list_resources_for_membership(
        self,
        organization_membership_id: str,
        *,
        resource_type: Optional[str] = None,
        parent_resource_id: Optional[str] = None,
        parent_organization_id: Optional[str] = None,
        parent_resource_type: Optional[str] = None,
        parent_external_id: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        order: PaginationOrder = "desc",
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> ResourcesForMembershipListResource:
        list_params: ResourcesForMembershipListFilters = {
            "limit": limit,
            "order": order,
            "before": before,
            "after": after,
        }

        if resource_type is not None:
            list_params["resource_type"] = resource_type

        # Parent by internal ID and by external ID are mutually exclusive
        if parent_resource_id is not None and parent_organization_id is not None:
            raise ValueError(
                "parent_resource_id and parent_organization_id are mutually exclusive"
            )

        if parent_resource_id is not None:
            list_params["parent_resource_id"] = parent_resource_id
        elif parent_organization_id is not None:
            list_params["parent_organization_id"] = parent_organization_id
            if parent_resource_type is not None:
                list_params["parent_resource_type"] = parent_resource_type
            if parent_external_id is not None:
                list_params["parent_external_id"] = parent_external_id

        response = await self._http_client.request(
            f"authorization/organization_memberships/{organization_membership_id}/resources",
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        # Add path param to list_args for pagination iterator
        list_params["organization_membership_id"] = organization_membership_id

        return ResourcesForMembershipListResource(
            list_method=self.list_resources_for_membership,
            list_args=list_params,
            **ListPage[Resource](**response).model_dump(),
        )

    async def list_memberships_for_resource(
        self,
        resource_id: str,
        *,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        order: PaginationOrder = "desc",
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> MembershipsForResourceListResource:
        list_params: MembershipsForResourceListFilters = {
            "limit": limit,
            "order": order,
            "before": before,
            "after": after,
        }

        response = await self._http_client.request(
            f"authorization/resources/{resource_id}/organization_memberships",
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        # Add path param to list_args for pagination iterator
        list_params["resource_id"] = resource_id

        return MembershipsForResourceListResource(
            list_method=self.list_memberships_for_resource,
            list_args=list_params,
            **ListPage[AuthorizationOrganizationMembership](**response).model_dump(),
        )

    async def list_memberships_for_resource_by_external_id(
        self,
        organization_id: str,
        resource_type: str,
        external_id: str,
        *,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        order: PaginationOrder = "desc",
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> MembershipsForResourceListResource:
        list_params: MembershipsForResourceListFilters = {
            "limit": limit,
            "order": order,
            "before": before,
            "after": after,
        }

        response = await self._http_client.request(
            f"authorization/organizations/{organization_id}/resources/{resource_type}/{external_id}/organization_memberships",
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        # Add path params to list_args for pagination iterator
        list_params["organization_id"] = organization_id
        list_params["resource_type"] = resource_type
        list_params["external_id"] = external_id

        return MembershipsForResourceListResource(
            list_method=self.list_memberships_for_resource_by_external_id,
            list_args=list_params,
            **ListPage[AuthorizationOrganizationMembership](**response).model_dump(),
        )
