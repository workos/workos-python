from typing import List, Literal
from workos.resources.workos_model import WorkOSModel
from workos.types.events.directory_payload import DirectoryPayload
from workos.typing.literals import LiteralOrUntyped


class MinimalOrganizationDomain(WorkOSModel):
    id: str
    organization_id: str
    object: Literal["organization_domain"]


class DirectoryPayloadWithLegacyFields(DirectoryPayload):
    domains: List[MinimalOrganizationDomain]
    external_key: str
