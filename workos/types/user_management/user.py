from typing import Literal, Optional
from workos.types.workos_model import WorkOSModel


class User(WorkOSModel):
    """Representation of a WorkOS User."""

    object: Literal["user"]
    id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email_verified: bool
    profile_picture_url: Optional[str] = None
    created_at: str
    updated_at: str
