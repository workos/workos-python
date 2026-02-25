from typing import Any, Literal, Mapping, Optional, Sequence
from typing_extensions import TypedDict

from workos.types.user_management.organization_membership_status import (
    OrganizationMembershipStatus,
)
from workos.types.workos_model import WorkOSModel
from workos.typing.literals import LiteralOrUntyped


class BaseOrganizationMembership(WorkOSModel):
    object: Literal["organization_membership"]
    id: str
    user_id: str
    organization_id: str
    status: LiteralOrUntyped[OrganizationMembershipStatus]
    custom_attributes: Optional[Mapping[str, Any]] = None
    created_at: str
    updated_at: str


class OrganizationMembershipRole(TypedDict):
    slug: str


class OrganizationMembership(BaseOrganizationMembership):
    role: OrganizationMembershipRole
    roles: Optional[Sequence[OrganizationMembershipRole]] = None
    custom_attributes: Mapping[str, Any]
