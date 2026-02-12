from typing import Literal, Optional, Sequence
from workos.types.workos_model import WorkOSModel


class OrganizationRolePayload(WorkOSModel):
    object: Literal["organization_role"]
    organization_id: str
    slug: str
    name: str
    description: Optional[str] = None
    resource_type_slug: Optional[str] = None
    permissions: Sequence[str]
    created_at: str
    updated_at: str
