from typing import Literal, Optional
from typing_extensions import TypedDict
from workos.resources.workos_model import WorkOSModel


class OrganizationDomain(WorkOSModel):
    id: str
    organization_id: str
    object: Literal["organization_domain"]
    verification_strategy: Literal["manual", "dns"]
    state: Literal["failed", "pending", "legacy_verified", "verified"]
    domain: str


class Organization(WorkOSModel):
    id: str
    object: Literal["organization"]
    name: str
    allow_profiles_outside_organization: bool
    created_at: str
    updated_at: str
    domains: list
    lookup_key: Optional[str] = None


class DomainDataInput(TypedDict):
    domain: str
    state: Literal["verified", "pending"]
