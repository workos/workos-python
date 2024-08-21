import datetime

from workos.types.directory_sync import (
    Directory,
    DirectoryMetadata,
    DirectoryUsersMetadata,
)


class MockDirectoryUsersMetadata(DirectoryUsersMetadata):
    def __init__(self, active=0, inactive=0):
        super().__init__(active=active, inactive=inactive)


class MockDirectoryMetadata(DirectoryMetadata):
    def __init__(self, users, groups=0):
        super().__init__(users=users, groups=groups)


class MockDirectory(Directory):
    def __init__(self, id, metadata=None):
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
            metadata=metadata,
            created_at=now,
            updated_at=now,
        )
