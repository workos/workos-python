from typing import Any, Dict, Optional

from workos.types.workos_model import WorkOSModel


class ResourceType(WorkOSModel):
    type: str
    relations: Dict[str, Any]
    created_at: Optional[str] = None
