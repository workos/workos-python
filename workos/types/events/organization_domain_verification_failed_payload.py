from typing import Literal
from workos.resources.workos_model import WorkOSModel
from workos.types.organizations.organization_domain import OrganizationDomain
from workos.typing.literals import LiteralOrUntyped


class OrganizationDomainVerificationFailedPayload(WorkOSModel):
    reason: LiteralOrUntyped[
        Literal[
            "domain_verification_period_expired",
            "domain_verified_by_other_organization",
        ]
    ]
    organization_domain: OrganizationDomain
