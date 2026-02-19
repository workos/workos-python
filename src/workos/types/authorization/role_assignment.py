from typing import Literal

from workos.types.workos_model import WorkOSModel


class RoleAssignmentRole(WorkOSModel):
    """The role associated with a role assignment."""

    slug: str


class RoleAssignmentResource(WorkOSModel):
    """The resource associated with a role assignment."""

    id: str
    external_id: str
    resource_type_slug: str


class RoleAssignment(WorkOSModel):
    """Representation of a WorkOS Authorization Role Assignment."""

    object: Literal["role_assignment"]
    id: str
    role: RoleAssignmentRole
    resource: RoleAssignmentResource
    created_at: str
    updated_at: str
