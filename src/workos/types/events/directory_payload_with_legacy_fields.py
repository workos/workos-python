from typing import Literal, Sequence
from workos.types.workos_model import WorkOSModel
from workos.types.events.directory_payload import DirectoryPayload


class MinimalOrganizationDomain(WorkOSModel):
    id: str
    # TODO: This should be domain: str in the
    # next major version to fix object parsing.
    organization_id: str
    object: Literal["organization_domain"]


# TODO: This class should be removed in the next major version once MinimalOrganizationDomain is updated.
class MinimalOrganizationDomainForEventsApi(WorkOSModel):
    id: str
    domain: str
    object: Literal["organization_domain"]


class DirectoryPayloadWithLegacyFields(DirectoryPayload):
    domains: Sequence[MinimalOrganizationDomain]
    external_key: str


# TODO: This class should be removed in the next major version once MinimalOrganizationDomain is updated.
class DirectoryPayloadWithLegacyFieldsForEventsApi(DirectoryPayload):
    domains: Sequence[MinimalOrganizationDomainForEventsApi]
    external_key: str
