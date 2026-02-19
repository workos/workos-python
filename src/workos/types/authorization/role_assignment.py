from typing import Literal

from workos.types.workos_model import WorkOSModel


class RoleAssignment(WorkOSModel):
    """Representation of a WorkOS Authorization Role Assignment."""

    object: Literal["role_assignment"]
    id: str
    role_slug: str
    role_name: str
    role_id: str
