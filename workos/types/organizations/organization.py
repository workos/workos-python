from dataclasses import field
from typing import Optional, Sequence, Dict
from workos.types.organizations.organization_common import OrganizationCommon
from workos.types.organizations.organization_domain import OrganizationDomain


class Organization(OrganizationCommon):
    allow_profiles_outside_organization: bool
    domains: Sequence[OrganizationDomain]
    stripe_customer_id: Optional[str] = None
    external_id: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)
