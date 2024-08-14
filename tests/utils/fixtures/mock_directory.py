import datetime

from workos.types.directory_sync import Directory


class MockDirectory(Directory):
    def __init__(self, id):
        now = datetime.datetime.now().isoformat()
        super().__init__(
            object="directory",
            id=id,
            organization_id="organization_id",
            external_key="ext_123",
            domain="somefakedomain.com",
            name="Some fake name",
            state="active",
            type="gsuite directory",
            created_at=now,
            updated_at=now,
        )
