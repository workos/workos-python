from typing import List, Optional
from workos.types.organizations.organization_common import OrganizationCommon
from workos.types.organizations.organization_domain import OrganizationDomain


class Organization(OrganizationCommon):
    allow_profiles_outside_organization: bool
    domains: List[OrganizationDomain]
    lookup_key: Optional[str] = None
