from typing import Literal, Sequence, Union

from pydantic import Field
from typing_extensions import Annotated

from workos.types.authorization.environment_role import EnvironmentRole
from workos.types.authorization.organization_role import OrganizationRole
from workos.types.workos_model import WorkOSModel

Role = Annotated[
    Union[EnvironmentRole, OrganizationRole],
    Field(discriminator="type"),
]


class RoleList(WorkOSModel):
    object: Literal["list"]
    data: Sequence[Role]
