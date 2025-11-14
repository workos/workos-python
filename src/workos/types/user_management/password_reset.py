from typing import Literal
from workos.types.workos_model import WorkOSModel


class PasswordResetCommon(WorkOSModel):
    object: Literal["password_reset"]
    id: str
    user_id: str
    email: str
    expires_at: str
    created_at: str


class PasswordReset(PasswordResetCommon):
    """Representation of a WorkOS PasswordReset object."""

    password_reset_token: str
    password_reset_url: str
