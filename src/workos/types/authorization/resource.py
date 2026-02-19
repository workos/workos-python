from typing import Any, Literal, Mapping, Optional

from workos.types.workos_model import WorkOSModel


class Resource(WorkOSModel):
    """Representation of a WorkOS Authorization Resource."""

    object: Literal["authorization_resource"]
    id: str
    resource_type: str
    resource_id: str
    organization_id: str
    external_id: Optional[str] = None
    meta: Optional[Mapping[str, Any]] = None
    environment_id: str
    created_at: str
    updated_at: str
