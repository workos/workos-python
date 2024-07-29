from typing import Literal
from workos.resources.workos_model import WorkOSModel


class EmailVerificationPayload(WorkOSModel):
    object: Literal["email_verification"]
    id: str
    user_id: str
    email: str
    expires_at: str
