from typing import Literal, Optional, Sequence

from workos.types.list_resource import ListMetadata
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


class RoleAssignmentList(WorkOSModel):
    object: Literal["list"]
    data: Sequence[RoleAssignment]
    list_metadata: ListMetadata
