from typing import Literal, Optional, Sequence

from workos.types.list_resource import ListMetadata
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


class AuthorizationResourceList(WorkOSModel):
    object: Literal["list"]
    data: Sequence[AuthorizationResource]
    list_metadata: ListMetadata
