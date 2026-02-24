from typing import Any, Literal, Mapping, Optional

from workos.types.user_management.organization_membership_status import (
    OrganizationMembershipStatus,
)
from workos.types.workos_model import WorkOSModel
from workos.typing.literals import LiteralOrUntyped


class AuthorizationOrganizationMembership(WorkOSModel):
    """Representation of an Organization Membership returned by Authorization endpoints.

    This is a separate type from the user_management OrganizationMembership because
    authorization endpoints return memberships without the ``role`` field and include
    ``organization_name``. Additionally, ``custom_attributes`` is optional here as
    authorization endpoints may omit it.
    """

    object: Literal["organization_membership"]
    id: str
    user_id: str
    organization_id: str
    organization_name: str
    status: LiteralOrUntyped[OrganizationMembershipStatus]
    custom_attributes: Optional[Mapping[str, Any]] = None
    created_at: str
    updated_at: str
