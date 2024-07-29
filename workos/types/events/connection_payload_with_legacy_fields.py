from typing import Literal
from workos.resources.sso import ConnectionWithDomains

ConnectionStatus = Literal["linked", "unlinked"]


class ConnectionPayloadWithLegacyFields(ConnectionWithDomains):
    external_key: str
