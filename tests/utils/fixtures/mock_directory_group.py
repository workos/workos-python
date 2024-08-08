import datetime

from workos.types.directory_sync import DirectoryGroup


class MockDirectoryGroup(DirectoryGroup):
    def __init__(self, id):
        now = datetime.datetime.now().isoformat()
        super().__init__(
            object="directory_group",
            id=id,
            idp_id="idp_id_" + id,
            directory_id="directory_id",
            organization_id="organization_id",
            name="group_" + id,
            created_at=now,
            updated_at=now,
            raw_attributes={},
        )
