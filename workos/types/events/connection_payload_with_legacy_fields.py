from typing import Literal
from workos.resources.sso import ConnectionWithDomains
from workos.typing.literals import LiteralOrUntyped

ConnectionStatus = Literal["linked", "unlinked"]


class ConnectionPayloadWithLegacyFields(ConnectionWithDomains):
    external_key: str
