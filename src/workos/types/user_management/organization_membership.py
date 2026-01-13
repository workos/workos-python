from typing import Literal, Sequence, Optional
from typing_extensions import TypedDict

from workos.types.workos_model import WorkOSModel
from workos.typing.literals import LiteralOrUntyped

OrganizationMembershipStatus = Literal["active", "inactive", "pending"]


class OrganizationMembershipRole(TypedDict):
    slug: str


class OrganizationMembership(WorkOSModel):
    """Representation of an WorkOS Organization Membership."""

    object: Literal["organization_membership"]
    id: str
    user_id: str
    organization_id: str
    role: OrganizationMembershipRole
    roles: Optional[Sequence[OrganizationMembershipRole]] = None
    status: LiteralOrUntyped[OrganizationMembershipStatus]
    created_at: str
    updated_at: str
