from typing import Literal, Sequence
from workos.types.workos_model import WorkOSModel
from workos.types.organization_domains import OrganizationDomain


class OrganizationCommon(WorkOSModel):
    id: str
    object: Literal["organization"]
    name: str
    domains: Sequence[OrganizationDomain]
    created_at: str
    updated_at: str
