from typing import Literal, Optional, Sequence
from workos.types.workos_model import WorkOSModel

RoleType = Literal["EnvironmentRole", "OrganizationRole"]


class RoleCommon(WorkOSModel):
    object: Literal["role"]
    slug: str


class Role(RoleCommon):
    permissions: Optional[Sequence[str]] = None


class OrganizationRole(RoleCommon):
    id: str
    name: str
    description: Optional[str] = None
    type: RoleType
    created_at: str
    updated_at: str


class RolesList(WorkOSModel):
    object: Literal["list"]
    data: Sequence[OrganizationRole]
