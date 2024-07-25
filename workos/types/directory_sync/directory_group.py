from typing import Literal
from workos.resources.workos_model import WorkOSModel


class DirectoryGroup(WorkOSModel):
    """Representation of a Directory Group as returned by WorkOS through the Directory Sync feature.

    Attributes:
        OBJECT_FIELDS (list): List of fields a DirectoryGroup is comprised of.
    """

    id: str
    object: Literal["directory_group"]
    idp_id: str
    name: str
    directory_id: str
    organization_id: str
    raw_attributes: dict
    created_at: str
    updated_at: str
