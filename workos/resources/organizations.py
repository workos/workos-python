from typing import Literal, Optional
from typing_extensions import TypedDict
from workos.resources.workos_model import WorkOSModel
from workos.types.organizations.organization_common import OrganizationCommon


class Organization(OrganizationCommon):
    allow_profiles_outside_organization: bool
    domains: list
    lookup_key: Optional[str] = None


class DomainDataInput(TypedDict):
    domain: str
    state: Literal["verified", "pending"]
