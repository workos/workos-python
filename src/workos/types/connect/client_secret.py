from typing import Literal, Optional

from workos.types.workos_model import WorkOSModel


class ClientSecret(WorkOSModel):
    object: Literal["connect_application_secret"]
    id: str
    secret: Optional[str] = None
    secret_hint: str
    last_used_at: Optional[str] = None
    created_at: str
    updated_at: str
