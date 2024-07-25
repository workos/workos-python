from typing import List, Literal, Optional
from workos.resources.workos_model import WorkOSModel
from workos.types.directory_sync.directory_group import DirectoryGroup


DirectoryUserState = Literal["active", "inactive"]


class DirectoryUserEmail(WorkOSModel):
    type: Optional[str] = None
    value: Optional[str] = None
    primary: Optional[bool] = None


class Role(WorkOSModel):
    slug: str


class DirectoryUser(WorkOSModel):
    """Representation of a Directory User as returned by WorkOS through the Directory Sync feature.

    Attributes:
        OBJECT_FIELDS (list): List of fields a DirectoryUser is comprised of.
    """

    id: str
    object: Literal["directory_user"]
    idp_id: str
    directory_id: str
    organization_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    job_title: Optional[str] = None
    emails: List[DirectoryUserEmail]
    username: Optional[str] = None
    groups: List[DirectoryGroup]
    state: DirectoryUserState
    custom_attributes: dict
    raw_attributes: dict
    created_at: str
    updated_at: str
    role: Optional[Role] = None

    def primary_email(self):
        return next((email for email in self.emails if email.primary), None)
