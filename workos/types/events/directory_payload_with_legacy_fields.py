from typing import Literal, Sequence
from workos.types.workos_model import WorkOSModel
from workos.types.events.directory_payload import DirectoryPayload


class MinimalOrganizationDomain(WorkOSModel):
    id: str
    organization_id: str
    object: Literal["organization_domain"]


class DirectoryPayloadWithLegacyFields(DirectoryPayload):
    domains: Sequence[MinimalOrganizationDomain]
    external_key: str
