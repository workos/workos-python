from workos.resources.directory_sync import DirectoryGroup, DirectoryUser
from workos.resources.workos_model import WorkOSModel


class DirectoryGroupMembershipPayload(WorkOSModel):
    directory_id: str
    user: DirectoryUser
    group: DirectoryGroup
