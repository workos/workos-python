from typing import Literal, Optional, Sequence

from workos.types.workos_model import WorkOSModel


class OrganizationRole(WorkOSModel):
    object: Literal["role"]
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    permissions: Sequence[str]
    type: Literal["OrganizationRole"]
    created_at: str
    updated_at: str


class OrganizationRoleEvent(WorkOSModel):
    """Organization role type for Events API responses."""

    object: Literal["organization_role"]
    organization_id: str
    slug: str
    name: str
    description: Optional[str] = None
    resource_type_slug: str
    permissions: Sequence[str]
    created_at: str
    updated_at: str


class OrganizationRoleList(WorkOSModel):
    object: Literal["list"]
    data: Sequence[OrganizationRole]
