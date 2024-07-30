from typing import Literal
from workos.resources.workos_model import WorkOSModel


class MagicAuthCommon(WorkOSModel):
    object: Literal["magic_auth"]
    id: str
    user_id: str
    email: str
    expires_at: str
    created_at: str
    updated_at: str
