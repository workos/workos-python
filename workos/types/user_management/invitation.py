from typing import Literal, Optional
from workos.types.workos_model import WorkOSModel
from workos.typing.literals import LiteralOrUntyped

InvitationState = Literal["accepted", "expired", "pending", "revoked"]


class InvitationCommon(WorkOSModel):
    object: Literal["invitation"]
    id: str
    email: str
    state: LiteralOrUntyped[InvitationState]
    accepted_at: Optional[str] = None
    revoked_at: Optional[str] = None
    expires_at: str
    organization_id: Optional[str] = None
    inviter_user_id: Optional[str] = None
    created_at: str
    updated_at: str


class Invitation(InvitationCommon):
    """Representation of a WorkOS Invitation as returned."""

    token: str
    accept_invitation_url: str
