from typing import Any, Literal, Mapping, Optional

from workos.types.user_management.organization_membership_status import (
    OrganizationMembershipStatus,
)
from workos.types.workos_model import WorkOSModel
from workos.typing.literals import LiteralOrUntyped


class AuthorizationOrganizationMembership(WorkOSModel):
    object: Literal["organization_membership"]
    id: str
    user_id: str
    organization_id: str
    status: LiteralOrUntyped[OrganizationMembershipStatus]
    created_at: str
    updated_at: str
