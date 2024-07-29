from typing import Literal
from workos.resources.workos_model import WorkOSModel
from workos.types.organizations.organization_domain import OrganizationDomain


class OrganizationCommon(WorkOSModel):
    id: str
    object: Literal["organization"]
    name: str
    domains: list[OrganizationDomain]
    created_at: str
    updated_at: str
