from typing import Literal, Optional
from workos.resources.workos_model import WorkOSModel


class OrganizationDomain(WorkOSModel):
    id: str
    organization_id: str
    object: Literal["organization_domain"]
    domain: str
    state: Optional[Literal["failed", "pending", "legacy_verified", "verified"]] = None
    verification_strategy: Optional[Literal["manual", "dns"]] = None
    verification_token: Optional[str] = None
