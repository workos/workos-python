from typing import Literal, Optional, Sequence

from workos.types.workos_model import WorkOSModel


class OrganizationRole(WorkOSModel):
    object: Literal["role"]
    id: str
    organization_id: str
    name: str
    slug: str
    description: Optional[str] = None
    permissions: Sequence[str]
    type: Literal["OrganizationRole"]
    created_at: str
    updated_at: str


class OrganizationRoleList(WorkOSModel):
    object: Literal["list"]
    data: Sequence[OrganizationRole]
