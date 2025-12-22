from typing import Any, Mapping, Optional

from workos.types.workos_model import WorkOSModel


class AuthorizationResourceType(WorkOSModel):
    type: str
    relations: Mapping[str, Any]
    created_at: Optional[str] = None
