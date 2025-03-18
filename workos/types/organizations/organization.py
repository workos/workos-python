from typing import Optional, Sequence
from workos.types.organizations.organization_common import OrganizationCommon
from workos.types.organizations.organization_domain import OrganizationDomain


class Organization(OrganizationCommon):
    allow_profiles_outside_organization: bool
    domains: Sequence[OrganizationDomain]
    stripe_customer_id: Optional[str] = None
    external_id: Optional[str] = None
