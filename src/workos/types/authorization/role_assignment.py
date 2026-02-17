from typing import TYPE_CHECKING, Literal, Sequence

from workos.types.workos_model import WorkOSModel

if TYPE_CHECKING:
    from workos.types.list_resource import ListMetadata


class RoleAssignmentRole(WorkOSModel):
    slug: str


class RoleAssignmentResource(WorkOSModel):
    id: str
    external_id: str
    resource_type_slug: str


class RoleAssignment(WorkOSModel):
    object: Literal["role_assignment"]
    id: str
    role: RoleAssignmentRole
    resource: RoleAssignmentResource
    created_at: str
    updated_at: str


class RoleAssignmentList(WorkOSModel):
    object: Literal["list"]
    data: Sequence[RoleAssignment]
    list_metadata: "ListMetadata"
