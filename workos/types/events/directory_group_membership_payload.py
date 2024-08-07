from workos.types.directory_sync import DirectoryGroup
from workos.types.workos_model import WorkOSModel
from workos.types.directory_sync.directory_user import DirectoryUser


class DirectoryGroupMembershipPayload(WorkOSModel):
    directory_id: str
    user: DirectoryUser
    group: DirectoryGroup
