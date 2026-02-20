from typing import Any, Literal, Mapping, Optional

from workos.types.workos_model import WorkOSModel


class AuthorizationResource(WorkOSModel):

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
