import datetime

from workos.types.authorization.environment_role import EnvironmentRole


class MockEnvironmentRole(EnvironmentRole):
    def __init__(self, id: str):
        now = datetime.datetime.now().isoformat()
        super().__init__(
            object="role",
            id=id,
            name="Member",
            slug="member",
            description="Default environment member role",
            permissions=["documents:read"],
            type="EnvironmentRole",
            created_at=now,
            updated_at=now,
        )
