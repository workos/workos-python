from typing import Literal, Optional
from workos.resources.workos_model import WorkOSModel
from workos.types.user_management.impersonator import Impersonator


class SessionCreatedPayload(WorkOSModel):
    object: Literal["session"]
    id: str
    impersonator: Optional[Impersonator] = None
    ip_address: Optional[str] = None
    organization_id: Optional[str] = None
    user_agent: Optional[str] = None
    user_id: str
    created_at: str
    updated_at: str
