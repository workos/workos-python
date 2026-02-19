from typing import Any, Literal, Mapping, Optional

from workos.types.workos_model import WorkOSModel
from workos.typing.literals import LiteralOrUntyped

OrganizationMembershipStatus = Literal["active", "inactive", "pending"]


class AuthorizationOrganizationMembership(WorkOSModel):
    """Representation of an Organization Membership returned by Authorization endpoints.

    This is a separate type from the user_management OrganizationMembership because
    authorization endpoints return memberships without the `role` field.
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
