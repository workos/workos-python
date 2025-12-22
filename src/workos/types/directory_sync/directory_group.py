from typing import Any, Literal, Mapping
from workos.types.workos_model import WorkOSModel


class DirectoryGroup(WorkOSModel):
    """Representation of a Directory Group as returned by WorkOS through the Directory Sync feature."""

    id: str
    object: Literal["directory_group"]
    idp_id: str
    name: str
    directory_id: str
    organization_id: str
    raw_attributes: Mapping[str, Any]
    created_at: str
    updated_at: str
