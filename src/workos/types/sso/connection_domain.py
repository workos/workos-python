from typing import Literal
from workos.types.workos_model import WorkOSModel


class ConnectionDomain(WorkOSModel):
    object: Literal["connection_domain"]
    id: str
    domain: str
