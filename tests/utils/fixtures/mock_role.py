import datetime

from workos.types.roles.role import Role


class MockRole(Role):
    def __init__(self, id):
        now = datetime.datetime.now().isoformat()
        super().__init__(
            object="role",
            id=id,
            name="Member",
            slug="member",
            description="The default member role",
            type="EnvironmentRole",
            created_at=now,
            updated_at=now,
        )
