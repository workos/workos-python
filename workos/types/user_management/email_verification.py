from typing import Literal
from workos.types.workos_model import WorkOSModel


class EmailVerificationCommon(WorkOSModel):
    object: Literal["email_verification"]
    id: str
    user_id: str
    email: str
    expires_at: str
    created_at: str
    updated_at: str


class EmailVerification(EmailVerificationCommon):
    """Representation of a WorkOS EmailVerification object."""

    code: str
