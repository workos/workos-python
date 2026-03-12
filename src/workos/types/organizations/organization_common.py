from typing import Literal, Optional, Sequence
from workos.types.workos_model import WorkOSModel
from workos.types.organization_domains import OrganizationDomain


class OrganizationCommon(WorkOSModel):
    id: str
    object: Literal["organization"]
    name: str
    external_id: Optional[str] = None
    domains: Sequence[OrganizationDomain]
    created_at: str
    updated_at: str
