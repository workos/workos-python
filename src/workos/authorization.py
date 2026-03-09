from enum import Enum
from functools import partial
from typing import Any, Dict, Optional, Protocol, Sequence, Union

from pydantic import TypeAdapter

from workos.types.authorization.access_check_response import AccessCheckResponse
from workos.types.authorization.assignment import Assignment
from workos.types.authorization.environment_role import (
    EnvironmentRole,
    EnvironmentRoleList,
)
from workos.types.authorization.organization_membership import (
    AuthorizationOrganizationMembership,
)
from workos.types.authorization.organization_role import OrganizationRole
from workos.types.authorization.parent_resource_identifier import (
    ParentResourceIdentifier,
)
from workos.types.authorization.permission import Permission
from workos.types.authorization.resource_identifier import ResourceIdentifier
from workos.types.authorization.authorization_resource import AuthorizationResource
from workos.types.authorization.role import Role, RoleList
from workos.types.authorization.role_assignment import RoleAssignment
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


class _Unset(Enum):
    TOKEN = 0


UNSET: _Unset = _Unset.TOKEN

AUTHORIZATION_PERMISSIONS_PATH = "authorization/permissions"
AUTHORIZATION_RESOURCES_PATH = "authorization/resources"
AUTHORIZATION_ORGANIZATIONS_PATH = "authorization/organizations"
AUTHORIZATION_ORGANIZATION_MEMBERSHIPS_PATH = "authorization/organization_memberships"


class ResourceListFilters(ListArgs, total=False):
    organization_id: Optional[str]
    resource_type_slug: Optional[str]
    parent_resource_id: Optional[str]
    parent_resource_type_slug: Optional[str]
    parent_external_id: Optional[str]
    search: Optional[str]


AuthorizationResourcesList = WorkOSListResource[
    AuthorizationResource, ResourceListFilters, ListMetadata
]


class ResourcesForMembershipListFilters(ListArgs, total=False):
    permission_slug: str


AuthorizationResourcesForMembershipList = WorkOSListResource[
    AuthorizationResource, ResourcesForMembershipListFilters, ListMetadata
]


class AuthorizationOrganizationMembershipListFilters(ListArgs, total=False):
    permission_slug: str
    assignment: Optional[Assignment]


AuthorizationOrganizationMembershipList = WorkOSListResource[
    AuthorizationOrganizationMembership,
    AuthorizationOrganizationMembershipListFilters,
    ListMetadata,
]

_role_adapter: TypeAdapter[Role] = TypeAdapter(Role)


class RoleAssignmentListFilters(ListArgs, total=False):
    organization_membership_id: str


RoleAssignmentsListResource = WorkOSListResource[
    RoleAssignment, RoleAssignmentListFilters, ListMetadata
]


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
        resource_type_slug: Optional[str] = None,
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
        resource_type_slug: Optional[str] = None,
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

    def get_resource(self, resource_id: str) -> SyncOrAsync[AuthorizationResource]: ...

    def create_resource(
        self,
        *,
        external_id: str,
        name: str,
        description: Optional[str] = None,
        resource_type_slug: str,
        organization_id: str,
        parent: Optional[ParentResourceIdentifier] = None,
    ) -> SyncOrAsync[AuthorizationResource]: ...

    def update_resource(
        self,
        resource_id: str,
        *,
        name: Optional[str] = None,
        description: Union[str, None, _Unset] = UNSET,
    ) -> SyncOrAsync[AuthorizationResource]: ...

    def delete_resource(
        self,
        resource_id: str,
        *,
        cascade_delete: Optional[bool] = None,
    ) -> SyncOrAsync[None]: ...

    def list_resources(
        self,
        *,
        organization_id: Optional[str] = None,
        resource_type_slug: Optional[str] = None,
        parent_resource_id: Optional[str] = None,
        parent_resource_type_slug: Optional[str] = None,
        parent_external_id: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> SyncOrAsync[AuthorizationResourcesList]: ...

    def get_resource_by_external_id(
        self,
        organization_id: str,
        resource_type: str,
        external_id: str,
    ) -> SyncOrAsync[AuthorizationResource]: ...

    def update_resource_by_external_id(
        self,
        organization_id: str,
        resource_type: str,
        external_id: str,
        *,
        name: Optional[str] = None,
        description: Union[str, None, _Unset] = UNSET,
    ) -> SyncOrAsync[AuthorizationResource]: ...

    def delete_resource_by_external_id(
        self,
        organization_id: str,
        resource_type: str,
        external_id: str,
        *,
        cascade_delete: Optional[bool] = None,
    ) -> SyncOrAsync[None]: ...

    def check(
        self,
        organization_membership_id: str,
        *,
        permission_slug: str,
        resource: ResourceIdentifier,
    ) -> SyncOrAsync[AccessCheckResponse]: ...

    def assign_role(
        self,
        organization_membership_id: str,
        *,
        role_slug: str,
        resource_identifier: ResourceIdentifier,
    ) -> SyncOrAsync[RoleAssignment]: ...

    def remove_role(
        self,
        organization_membership_id: str,
        *,
        role_slug: str,
        resource_identifier: ResourceIdentifier,
    ) -> SyncOrAsync[None]: ...

    def remove_role_assignment(
        self,
        organization_membership_id: str,
        role_assignment_id: str,
    ) -> SyncOrAsync[None]: ...

    def list_role_assignments(
        self,
        *,
        organization_membership_id: str,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> SyncOrAsync[RoleAssignmentsListResource]: ...

    def list_resources_for_membership(
        self,
        organization_membership_id: str,
        *,
        permission_slug: str,
        parent_resource: ParentResourceIdentifier,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> SyncOrAsync[AuthorizationResourcesForMembershipList]: ...

    def list_memberships_for_resource(
        self,
        resource_id: str,
        *,
        permission_slug: str,
        assignment: Optional[Assignment] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> SyncOrAsync[AuthorizationOrganizationMembershipList]: ...

    def list_memberships_for_resource_by_external_id(
        self,
        organization_id: str,
        resource_type_slug: str,
        external_id: str,
        *,
        permission_slug: str,
        assignment: Optional[Assignment] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> SyncOrAsync[AuthorizationOrganizationMembershipList]: ...


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
        resource_type_slug: Optional[str] = None,
    ) -> Permission:
        json: Dict[str, Any] = {"slug": slug, "name": name}
        if description is not None:
            json["description"] = description
        if resource_type_slug is not None:
            json["resource_type_slug"] = resource_type_slug

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
        resource_type_slug: Optional[str] = None,
    ) -> EnvironmentRole:
        json: Dict[str, Any] = {"slug": slug, "name": name}
        if description is not None:
            json["description"] = description
        if resource_type_slug is not None:
            json["resource_type_slug"] = resource_type_slug

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

    def get_resource(self, resource_id: str) -> AuthorizationResource:
        response = self._http_client.request(
            f"{AUTHORIZATION_RESOURCES_PATH}/{resource_id}",
            method=REQUEST_METHOD_GET,
        )

        return AuthorizationResource.model_validate(response)

    def create_resource(
        self,
        *,
        external_id: str,
        name: str,
        description: Optional[str] = None,
        resource_type_slug: str,
        organization_id: str,
        parent: Optional[ParentResourceIdentifier] = None,
    ) -> AuthorizationResource:
        json: Dict[str, Any] = {
            "resource_type_slug": resource_type_slug,
            "organization_id": organization_id,
            "external_id": external_id,
            "name": name,
        }
        if parent is not None:
            json.update(parent)
        if description is not None:
            json["description"] = description

        response = self._http_client.request(
            AUTHORIZATION_RESOURCES_PATH,
            method=REQUEST_METHOD_POST,
            json=json,
        )

        return AuthorizationResource.model_validate(response)

    def update_resource(
        self,
        resource_id: str,
        *,
        name: Optional[str] = None,
        description: Union[str, None, _Unset] = UNSET,
    ) -> AuthorizationResource:
        json: Dict[str, Any] = {}
        if name is not None:
            json["name"] = name
        if not isinstance(description, _Unset):
            json["description"] = description

        response = self._http_client.request(
            f"{AUTHORIZATION_RESOURCES_PATH}/{resource_id}",
            method=REQUEST_METHOD_PATCH,
            json=json,
            exclude_none=False,
        )

        return AuthorizationResource.model_validate(response)

    def delete_resource(
        self,
        resource_id: str,
        *,
        cascade_delete: Optional[bool] = None,
    ) -> None:
        params = (
            {"cascade_delete": str(cascade_delete).lower()}
            if cascade_delete is not None
            else None
        )
        self._http_client.request(
            f"{AUTHORIZATION_RESOURCES_PATH}/{resource_id}",
            method=REQUEST_METHOD_DELETE,
            params=params,
        )

    def list_resources(
        self,
        *,
        organization_id: Optional[str] = None,
        resource_type_slug: Optional[str] = None,
        parent_resource_id: Optional[str] = None,
        parent_resource_type_slug: Optional[str] = None,
        parent_external_id: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> AuthorizationResourcesList:
        list_params: ResourceListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }
        if organization_id is not None:
            list_params["organization_id"] = organization_id
        if resource_type_slug is not None:
            list_params["resource_type_slug"] = resource_type_slug
        if parent_resource_id is not None:
            list_params["parent_resource_id"] = parent_resource_id
        if parent_resource_type_slug is not None:
            list_params["parent_resource_type_slug"] = parent_resource_type_slug
        if parent_external_id is not None:
            list_params["parent_external_id"] = parent_external_id
        if search is not None:
            list_params["search"] = search

        response = self._http_client.request(
            AUTHORIZATION_RESOURCES_PATH,
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        return WorkOSListResource[
            AuthorizationResource, ResourceListFilters, ListMetadata
        ](
            list_method=self.list_resources,
            list_args=list_params,
            **ListPage[AuthorizationResource](**response).model_dump(),
        )

    def get_resource_by_external_id(
        self,
        organization_id: str,
        resource_type: str,
        external_id: str,
    ) -> AuthorizationResource:
        response = self._http_client.request(
            f"{AUTHORIZATION_ORGANIZATIONS_PATH}/{organization_id}/resources/{resource_type}/{external_id}",
            method=REQUEST_METHOD_GET,
        )

        return AuthorizationResource.model_validate(response)

    def update_resource_by_external_id(
        self,
        organization_id: str,
        resource_type: str,
        external_id: str,
        *,
        name: Optional[str] = None,
        description: Union[str, None, _Unset] = UNSET,
    ) -> AuthorizationResource:
        json: Dict[str, Any] = {}
        if name is not None:
            json["name"] = name
        if not isinstance(description, _Unset):
            json["description"] = description

        response = self._http_client.request(
            f"{AUTHORIZATION_ORGANIZATIONS_PATH}/{organization_id}/resources/{resource_type}/{external_id}",
            method=REQUEST_METHOD_PATCH,
            json=json,
            exclude_none=False,
        )

        return AuthorizationResource.model_validate(response)

    def delete_resource_by_external_id(
        self,
        organization_id: str,
        resource_type: str,
        external_id: str,
        *,
        cascade_delete: Optional[bool] = None,
    ) -> None:
        path = f"{AUTHORIZATION_ORGANIZATIONS_PATH}/{organization_id}/resources/{resource_type}/{external_id}"
        params = (
            {"cascade_delete": str(cascade_delete).lower()}
            if cascade_delete is not None
            else None
        )
        self._http_client.request(
            path,
            method=REQUEST_METHOD_DELETE,
            params=params,
        )

    def check(
        self,
        organization_membership_id: str,
        *,
        permission_slug: str,
        resource: ResourceIdentifier,
    ) -> AccessCheckResponse:
        json: Dict[str, Any] = {"permission_slug": permission_slug}
        json.update(resource)

        response = self._http_client.request(
            f"{AUTHORIZATION_ORGANIZATION_MEMBERSHIPS_PATH}/{organization_membership_id}/check",
            method=REQUEST_METHOD_POST,
            json=json,
        )

        return AccessCheckResponse.model_validate(response)

    def assign_role(
        self,
        organization_membership_id: str,
        *,
        role_slug: str,
        resource_identifier: ResourceIdentifier,
    ) -> RoleAssignment:
        json: Dict[str, Any] = {"role_slug": role_slug}
        json.update(resource_identifier)

        response = self._http_client.request(
            f"{AUTHORIZATION_ORGANIZATION_MEMBERSHIPS_PATH}/{organization_membership_id}/role_assignments",
            method=REQUEST_METHOD_POST,
            json=json,
        )

        return RoleAssignment.model_validate(response)

    def remove_role(
        self,
        organization_membership_id: str,
        *,
        role_slug: str,
        resource_identifier: ResourceIdentifier,
    ) -> None:
        json: Dict[str, Any] = {"role_slug": role_slug}
        json.update(resource_identifier)

        self._http_client.delete_with_body(
            f"{AUTHORIZATION_ORGANIZATION_MEMBERSHIPS_PATH}/{organization_membership_id}/role_assignments",
            json=json,
        )

    def remove_role_assignment(
        self,
        organization_membership_id: str,
        role_assignment_id: str,
    ) -> None:
        self._http_client.request(
            f"{AUTHORIZATION_ORGANIZATION_MEMBERSHIPS_PATH}/{organization_membership_id}/role_assignments/{role_assignment_id}",
            method=REQUEST_METHOD_DELETE,
        )

    def list_role_assignments(
        self,
        *,
        organization_membership_id: str,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> RoleAssignmentsListResource:
        list_params: RoleAssignmentListFilters = {
            "organization_membership_id": organization_membership_id,
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        query_params: ListArgs = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        response = self._http_client.request(
            f"{AUTHORIZATION_ORGANIZATION_MEMBERSHIPS_PATH}/{organization_membership_id}/role_assignments",
            method=REQUEST_METHOD_GET,
            params=query_params,
        )

        return WorkOSListResource[
            RoleAssignment, RoleAssignmentListFilters, ListMetadata
        ](
            list_method=self.list_role_assignments,
            list_args=list_params,
            **ListPage[RoleAssignment](**response).model_dump(),
        )

    def list_resources_for_membership(
        self,
        organization_membership_id: str,
        *,
        permission_slug: str,
        parent_resource: ParentResourceIdentifier,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> AuthorizationResourcesForMembershipList:
        list_params: ResourcesForMembershipListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
            "permission_slug": permission_slug,
        }

        http_params: Dict[str, Any] = {**list_params}
        http_params.update(parent_resource)

        response = self._http_client.request(
            f"{AUTHORIZATION_ORGANIZATION_MEMBERSHIPS_PATH}/{organization_membership_id}/resources",
            method=REQUEST_METHOD_GET,
            params=http_params,
        )

        return AuthorizationResourcesForMembershipList(
            list_method=partial(
                self.list_resources_for_membership,
                organization_membership_id,
                parent_resource=parent_resource,
            ),
            list_args=list_params,
            **ListPage[AuthorizationResource](**response).model_dump(),
        )

    def list_memberships_for_resource(
        self,
        resource_id: str,
        *,
        permission_slug: str,
        assignment: Optional[Assignment] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> AuthorizationOrganizationMembershipList:
        list_params: AuthorizationOrganizationMembershipListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
            "permission_slug": permission_slug,
        }
        if assignment is not None:
            list_params["assignment"] = assignment

        response = self._http_client.request(
            f"{AUTHORIZATION_RESOURCES_PATH}/{resource_id}/organization_memberships",
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        return WorkOSListResource[
            AuthorizationOrganizationMembership,
            AuthorizationOrganizationMembershipListFilters,
            ListMetadata,
        ](
            list_method=partial(self.list_memberships_for_resource, resource_id),
            list_args=list_params,
            **ListPage[AuthorizationOrganizationMembership](**response).model_dump(),
        )

    def list_memberships_for_resource_by_external_id(
        self,
        organization_id: str,
        resource_type_slug: str,
        external_id: str,
        *,
        permission_slug: str,
        assignment: Optional[Assignment] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> AuthorizationOrganizationMembershipList:
        list_params: AuthorizationOrganizationMembershipListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
            "permission_slug": permission_slug,
        }
        if assignment is not None:
            list_params["assignment"] = assignment

        response = self._http_client.request(
            f"{AUTHORIZATION_ORGANIZATIONS_PATH}/{organization_id}/resources/{resource_type_slug}/{external_id}/organization_memberships",
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        return WorkOSListResource[
            AuthorizationOrganizationMembership,
            AuthorizationOrganizationMembershipListFilters,
            ListMetadata,
        ](
            list_method=partial(
                self.list_memberships_for_resource_by_external_id,
                organization_id,
                resource_type_slug,
                external_id,
            ),
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
        resource_type_slug: Optional[str] = None,
    ) -> Permission:
        json: Dict[str, Any] = {"slug": slug, "name": name}
        if description is not None:
            json["description"] = description
        if resource_type_slug is not None:
            json["resource_type_slug"] = resource_type_slug

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

    async def create_environment_role(
        self,
        *,
        slug: str,
        name: str,
        description: Optional[str] = None,
        resource_type_slug: Optional[str] = None,
    ) -> EnvironmentRole:
        json: Dict[str, Any] = {"slug": slug, "name": name}
        if description is not None:
            json["description"] = description
        if resource_type_slug is not None:
            json["resource_type_slug"] = resource_type_slug

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

    async def get_resource(self, resource_id: str) -> AuthorizationResource:
        response = await self._http_client.request(
            f"{AUTHORIZATION_RESOURCES_PATH}/{resource_id}",
            method=REQUEST_METHOD_GET,
        )

        return AuthorizationResource.model_validate(response)

    async def create_resource(
        self,
        *,
        external_id: str,
        name: str,
        description: Optional[str] = None,
        resource_type_slug: str,
        organization_id: str,
        parent: Optional[ParentResourceIdentifier] = None,
    ) -> AuthorizationResource:
        json: Dict[str, Any] = {
            "resource_type_slug": resource_type_slug,
            "organization_id": organization_id,
            "external_id": external_id,
            "name": name,
        }
        if parent is not None:
            json.update(parent)
        if description is not None:
            json["description"] = description

        response = await self._http_client.request(
            AUTHORIZATION_RESOURCES_PATH,
            method=REQUEST_METHOD_POST,
            json=json,
        )

        return AuthorizationResource.model_validate(response)

    async def update_resource(
        self,
        resource_id: str,
        *,
        name: Optional[str] = None,
        description: Union[str, None, _Unset] = UNSET,
    ) -> AuthorizationResource:
        json: Dict[str, Any] = {}
        if name is not None:
            json["name"] = name
        if not isinstance(description, _Unset):
            json["description"] = description

        response = await self._http_client.request(
            f"{AUTHORIZATION_RESOURCES_PATH}/{resource_id}",
            method=REQUEST_METHOD_PATCH,
            json=json,
            exclude_none=False,
        )

        return AuthorizationResource.model_validate(response)

    async def delete_resource(
        self,
        resource_id: str,
        *,
        cascade_delete: Optional[bool] = None,
    ) -> None:
        params = (
            {"cascade_delete": str(cascade_delete).lower()}
            if cascade_delete is not None
            else None
        )
        await self._http_client.request(
            f"{AUTHORIZATION_RESOURCES_PATH}/{resource_id}",
            method=REQUEST_METHOD_DELETE,
            params=params,
        )

    async def list_resources(
        self,
        *,
        organization_id: Optional[str] = None,
        resource_type_slug: Optional[str] = None,
        parent_resource_id: Optional[str] = None,
        parent_resource_type_slug: Optional[str] = None,
        parent_external_id: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> AuthorizationResourcesList:
        list_params: ResourceListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }
        if organization_id is not None:
            list_params["organization_id"] = organization_id
        if resource_type_slug is not None:
            list_params["resource_type_slug"] = resource_type_slug
        if parent_resource_id is not None:
            list_params["parent_resource_id"] = parent_resource_id
        if parent_resource_type_slug is not None:
            list_params["parent_resource_type_slug"] = parent_resource_type_slug
        if parent_external_id is not None:
            list_params["parent_external_id"] = parent_external_id
        if search is not None:
            list_params["search"] = search

        response = await self._http_client.request(
            AUTHORIZATION_RESOURCES_PATH,
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        return WorkOSListResource[
            AuthorizationResource, ResourceListFilters, ListMetadata
        ](
            list_method=self.list_resources,
            list_args=list_params,
            **ListPage[AuthorizationResource](**response).model_dump(),
        )

    async def get_resource_by_external_id(
        self,
        organization_id: str,
        resource_type: str,
        external_id: str,
    ) -> AuthorizationResource:
        response = await self._http_client.request(
            f"{AUTHORIZATION_ORGANIZATIONS_PATH}/{organization_id}/resources/{resource_type}/{external_id}",
            method=REQUEST_METHOD_GET,
        )

        return AuthorizationResource.model_validate(response)

    async def update_resource_by_external_id(
        self,
        organization_id: str,
        resource_type: str,
        external_id: str,
        *,
        name: Optional[str] = None,
        description: Union[str, None, _Unset] = UNSET,
    ) -> AuthorizationResource:
        json: Dict[str, Any] = {}
        if name is not None:
            json["name"] = name
        if not isinstance(description, _Unset):
            json["description"] = description

        response = await self._http_client.request(
            f"{AUTHORIZATION_ORGANIZATIONS_PATH}/{organization_id}/resources/{resource_type}/{external_id}",
            method=REQUEST_METHOD_PATCH,
            json=json,
            exclude_none=False,
        )

        return AuthorizationResource.model_validate(response)

    async def delete_resource_by_external_id(
        self,
        organization_id: str,
        resource_type: str,
        external_id: str,
        *,
        cascade_delete: Optional[bool] = None,
    ) -> None:
        path = f"{AUTHORIZATION_ORGANIZATIONS_PATH}/{organization_id}/resources/{resource_type}/{external_id}"
        params = (
            {"cascade_delete": str(cascade_delete).lower()}
            if cascade_delete is not None
            else None
        )
        await self._http_client.request(
            path,
            method=REQUEST_METHOD_DELETE,
            params=params,
        )

    async def check(
        self,
        organization_membership_id: str,
        *,
        permission_slug: str,
        resource: ResourceIdentifier,
    ) -> AccessCheckResponse:
        json: Dict[str, Any] = {"permission_slug": permission_slug}
        json.update(resource)

        response = await self._http_client.request(
            f"{AUTHORIZATION_ORGANIZATION_MEMBERSHIPS_PATH}/{organization_membership_id}/check",
            method=REQUEST_METHOD_POST,
            json=json,
        )

        return AccessCheckResponse.model_validate(response)

    async def assign_role(
        self,
        organization_membership_id: str,
        *,
        role_slug: str,
        resource_identifier: ResourceIdentifier,
    ) -> RoleAssignment:
        json: Dict[str, Any] = {"role_slug": role_slug}
        json.update(resource_identifier)

        response = await self._http_client.request(
            f"{AUTHORIZATION_ORGANIZATION_MEMBERSHIPS_PATH}/{organization_membership_id}/role_assignments",
            method=REQUEST_METHOD_POST,
            json=json,
        )

        return RoleAssignment.model_validate(response)

    async def remove_role(
        self,
        organization_membership_id: str,
        *,
        role_slug: str,
        resource_identifier: ResourceIdentifier,
    ) -> None:
        json: Dict[str, Any] = {"role_slug": role_slug}
        json.update(resource_identifier)

        await self._http_client.delete_with_body(
            f"{AUTHORIZATION_ORGANIZATION_MEMBERSHIPS_PATH}/{organization_membership_id}/role_assignments",
            json=json,
        )

    async def remove_role_assignment(
        self,
        organization_membership_id: str,
        role_assignment_id: str,
    ) -> None:
        await self._http_client.request(
            f"{AUTHORIZATION_ORGANIZATION_MEMBERSHIPS_PATH}/{organization_membership_id}/role_assignments/{role_assignment_id}",
            method=REQUEST_METHOD_DELETE,
        )

    async def list_role_assignments(
        self,
        *,
        organization_membership_id: str,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> RoleAssignmentsListResource:
        list_params: RoleAssignmentListFilters = {
            "organization_membership_id": organization_membership_id,
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        query_params: ListArgs = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        response = await self._http_client.request(
            f"{AUTHORIZATION_ORGANIZATION_MEMBERSHIPS_PATH}/{organization_membership_id}/role_assignments",
            method=REQUEST_METHOD_GET,
            params=query_params,
        )

        return WorkOSListResource[
            RoleAssignment, RoleAssignmentListFilters, ListMetadata
        ](
            list_method=self.list_role_assignments,
            list_args=list_params,
            **ListPage[RoleAssignment](**response).model_dump(),
        )

    async def list_resources_for_membership(
        self,
        organization_membership_id: str,
        *,
        permission_slug: str,
        parent_resource: ParentResourceIdentifier,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> AuthorizationResourcesForMembershipList:
        list_params: ResourcesForMembershipListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
            "permission_slug": permission_slug,
        }

        http_params: Dict[str, Any] = {**list_params}
        http_params.update(parent_resource)

        response = await self._http_client.request(
            f"{AUTHORIZATION_ORGANIZATION_MEMBERSHIPS_PATH}/{organization_membership_id}/resources",
            method=REQUEST_METHOD_GET,
            params=http_params,
        )

        return AuthorizationResourcesForMembershipList(
            list_method=partial(
                self.list_resources_for_membership,
                organization_membership_id,
                parent_resource=parent_resource,
            ),
            list_args=list_params,
            **ListPage[AuthorizationResource](**response).model_dump(),
        )

    async def list_memberships_for_resource(
        self,
        resource_id: str,
        *,
        permission_slug: str,
        assignment: Optional[Assignment] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> AuthorizationOrganizationMembershipList:
        list_params: AuthorizationOrganizationMembershipListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
            "permission_slug": permission_slug,
        }
        if assignment is not None:
            list_params["assignment"] = assignment

        response = await self._http_client.request(
            f"{AUTHORIZATION_RESOURCES_PATH}/{resource_id}/organization_memberships",
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        return WorkOSListResource[
            AuthorizationOrganizationMembership,
            AuthorizationOrganizationMembershipListFilters,
            ListMetadata,
        ](
            list_method=partial(self.list_memberships_for_resource, resource_id),
            list_args=list_params,
            **ListPage[AuthorizationOrganizationMembership](**response).model_dump(),
        )

    async def list_memberships_for_resource_by_external_id(
        self,
        organization_id: str,
        resource_type_slug: str,
        external_id: str,
        *,
        permission_slug: str,
        assignment: Optional[Assignment] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> AuthorizationOrganizationMembershipList:
        list_params: AuthorizationOrganizationMembershipListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
            "permission_slug": permission_slug,
        }
        if assignment is not None:
            list_params["assignment"] = assignment

        response = await self._http_client.request(
            f"{AUTHORIZATION_ORGANIZATIONS_PATH}/{organization_id}/resources/{resource_type_slug}/{external_id}/organization_memberships",
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        return WorkOSListResource[
            AuthorizationOrganizationMembership,
            AuthorizationOrganizationMembershipListFilters,
            ListMetadata,
        ](
            list_method=partial(
                self.list_memberships_for_resource_by_external_id,
                organization_id,
                resource_type_slug,
                external_id,
            ),
            list_args=list_params,
            **ListPage[AuthorizationOrganizationMembership](**response).model_dump(),
        )
