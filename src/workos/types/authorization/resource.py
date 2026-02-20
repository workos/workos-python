from typing import Literal, Optional

from workos.types.workos_model import WorkOSModel


class Resource(WorkOSModel):
    """Representation of an Authorization Resource."""

    object: Literal["authorization_resource"]
    id: str
    external_id: str
    name: str
    description: Optional[str] = None
    resource_type_slug: str
    organization_id: str
    parent_resource_id: Optional[str] = None
    created_at: str
    updated_at: str
