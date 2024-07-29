from typing import Literal
from workos.resources.workos_model import WorkOSModel


class PasswordResetCommon(WorkOSModel):
    object: Literal["password_reset"]
    id: str
    user_id: str
    email: str
    expires_at: str
    created_at: str
