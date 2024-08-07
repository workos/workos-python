from typing import Literal
from workos.resources.workos_model import WorkOSModel


class PasswordlessSession(WorkOSModel):
    """Representation of a WorkOS Passwordless Session Response."""

    object: Literal["passwordless_session"]
    id: str
    email: str
    expires_at: str
    link: str
