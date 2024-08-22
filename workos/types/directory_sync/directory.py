from typing import Literal, Optional
from workos.types.workos_model import WorkOSModel
from workos.types.directory_sync.directory_state import DirectoryState
from workos.types.directory_sync.directory_type import DirectoryType
from workos.typing.literals import LiteralOrUntyped


class DirectoryUsersMetadata(WorkOSModel):
    active: int
    inactive: int


class DirectoryMetadata(WorkOSModel):
    users: DirectoryUsersMetadata
    groups: int


class Directory(WorkOSModel):
    """Representation of a Directory Response as returned by WorkOS through the Directory Sync feature."""

    id: str
    object: Literal["directory"]
    domain: Optional[str] = None
    name: str
    organization_id: str
    external_key: str
    state: LiteralOrUntyped[DirectoryState]
    type: LiteralOrUntyped[DirectoryType]
    metadata: Optional[DirectoryMetadata] = None
    created_at: str
    updated_at: str
