from pydantic import BaseModel

from typing import List, Literal, Optional, TypedDict


class OrganizationDomain(BaseModel):
    id: str
    organization_id: str
    object: Literal["organization"]
    verification_strategy: Literal["manual", "dns"]
    state: Literal["failed", "pending", "legacy_verified", "verified"]
    domain: str


class Organization(BaseModel):
    id: str
    object: Literal["organization"]
    name: str
    allow_profiles_outside_organization: bool
    created_at: str
    updated_at: str
    domains: list
    lookup_key: Optional[str] = None


class DomainData(TypedDict):
    domain: str
    state: Literal["verified", "pending"]


class CreateOrUpdateOrganizationOptions(TypedDict):
    name: str
    domain_data: Optional[List[DomainData]]
