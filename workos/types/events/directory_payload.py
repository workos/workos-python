from typing import Literal
from workos.resources.directory_sync import DirectoryState, DirectoryType
from workos.resources.workos_model import WorkOSModel
from workos.typing.literals import LiteralOrUntyped


class DirectoryPayload(WorkOSModel):
    id: str
    name: str
    state: LiteralOrUntyped[DirectoryState]
    type: LiteralOrUntyped[DirectoryType]
    organization_id: str
    created_at: str
    updated_at: str
    object: Literal["directory"]
