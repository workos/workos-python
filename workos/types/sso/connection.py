from typing import Literal

from workos.resources.workos_model import WorkOSModel
from workos.typing.literals import LiteralOrUntyped
from workos.utils.connection_types import ConnectionType

ConnectionState = Literal[
    "active", "deleting", "inactive", "requires_type", "validating"
]


class Connection(WorkOSModel):
    object: Literal["connection"]
    id: str
    organization_id: str
    connection_type: LiteralOrUntyped[ConnectionType]
    name: str
    state: LiteralOrUntyped[ConnectionState]
    created_at: str
    updated_at: str
