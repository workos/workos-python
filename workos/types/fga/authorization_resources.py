from typing import Any, Mapping, Optional

from workos.types.workos_model import WorkOSModel


class AuthorizationResource(WorkOSModel):
    resource_type: str
    resource_id: str
    meta: Optional[Mapping[str, Any]] = None
    created_at: Optional[str] = None
