from typing import Any, Literal, Mapping, Optional, Sequence

from typing_extensions import TypedDict

from workos.types.workos_model import WorkOSModel
from workos.typing.literals import LiteralOrUntyped

OrganizationMembershipStatus = Literal["active", "inactive", "pending"]


class BaseOrganizationMembership(WorkOSModel):
    object: Literal["organization_membership"]
    id: str
    user_id: str
    organization_id: str
    organization_name: Optional[str] = None
    status: LiteralOrUntyped[OrganizationMembershipStatus]
    directory_managed: bool = False
    created_at: str
    updated_at: str


class OrganizationMembershipRole(TypedDict):
    slug: str


class OrganizationMembership(BaseOrganizationMembership):
    """Representation of an WorkOS Organization Membership."""

    role: OrganizationMembershipRole
    roles: Optional[Sequence[OrganizationMembershipRole]] = None
    custom_attributes: Mapping[str, Any] = {}
