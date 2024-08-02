from typing import Optional
from workos.types.organizations.organization_common import OrganizationCommon


class Organization(OrganizationCommon):
    allow_profiles_outside_organization: bool
    domains: list
    lookup_key: Optional[str] = None
