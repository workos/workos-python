from typing import Literal, Optional
from workos.types.workos_model import WorkOSModel


class PermissionPayload(WorkOSModel):
    object: Literal["permission"]
    id: str
    slug: str
    name: str
    description: Optional[str] = None
    system: bool
    created_at: str
    updated_at: str
