from typing import Any, Dict, Optional

from workos.types.workos_model import WorkOSModel


class Resource(WorkOSModel):
    resource_type: str
    resource_id: str
    meta: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
