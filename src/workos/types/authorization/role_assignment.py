from typing import Literal

from workos.types.workos_model import WorkOSModel


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
