from typing import Any, Dict, Literal, Optional, Sequence, Union

from workos.types.workos_model import WorkOSModel
from workos.types.directory_sync.directory_group import DirectoryGroup


DirectoryUserState = Literal["active", "inactive"]


class DirectoryUserEmail(WorkOSModel):
    type: Optional[str] = None
    value: Optional[str] = None
    primary: Optional[bool] = None


class InlineRole(WorkOSModel):
    slug: str


class DirectoryUser(WorkOSModel):
    id: str
    object: Literal["directory_user"]
    idp_id: str
    directory_id: str
    organization_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    # @deprecated Will be removed in a future major version. Enable the `job_title` custom attribute in dashboard and pull from customAttributes instead. See https://workos.com/docs/directory-sync/attributes/custom-attributes/auto-mapped-attributes for details.
    job_title: Optional[str] = None
    # @deprecated Will be removed in a future major version. Enable the `emails` custom attribute in dashboard and pull from customAttributes instead. See https://workos.com/docs/directory-sync/attributes/custom-attributes/auto-mapped-attributes for details.
    emails: Sequence[DirectoryUserEmail]
    # @deprecated Will be removed in a future major version. Enable the `username` custom attribute in dashboard and pull from customAttributes instead. See https://workos.com/docs/directory-sync/attributes/custom-attributes/auto-mapped-attributes for details.
    username: Optional[str] = None
    state: DirectoryUserState
    custom_attributes: Dict[str, Any]
    raw_attributes: Dict[str, Any]
    created_at: str
    updated_at: str
    role: Optional[InlineRole] = None

    def primary_email(self) -> Union[DirectoryUserEmail, None]:
        return next((email for email in self.emails if email.primary), None)


class DirectoryUserWithGroups(DirectoryUser):
    """Representation of a Directory User as returned by WorkOS through the Directory Sync feature."""

    groups: Sequence[DirectoryGroup]
