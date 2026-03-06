from typing import Literal, Optional, Sequence

from workos.types.workos_model import WorkOSModel


class EnvironmentRole(WorkOSModel):
    object: Literal["role"]
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    resource_type_slug: str
    permissions: Sequence[str]
    type: Literal["EnvironmentRole"]
    created_at: str
    updated_at: str


class EnvironmentRoleList(WorkOSModel):
    object: Literal["list"]
    data: Sequence[EnvironmentRole]
