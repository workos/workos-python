from typing import Literal, Optional, Sequence
from workos.types.workos_model import WorkOSModel

RoleType = Literal["EnvironmentRole", "OrganizationRole"]


class RoleCommon(WorkOSModel):
    object: Literal["role"]
    slug: str


class EventRole(RoleCommon):
    permissions: Optional[Sequence[str]] = None


class Role(RoleCommon):
    id: str
    name: str
    description: Optional[str] = None
    type: RoleType
    created_at: str
    updated_at: str


class RoleList(WorkOSModel):
    object: Literal["list"]
    data: Sequence[Role]
