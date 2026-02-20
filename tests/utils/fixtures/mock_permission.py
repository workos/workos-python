import datetime

from workos.types.authorization.permission import Permission


class MockPermission(Permission):
    def __init__(self, id: str, slug: str = "documents:read"):
        now = datetime.datetime.now().isoformat()
        super().__init__(
            object="permission",
            id=id,
            slug=slug,
            name="Read Documents",
            description="Allows reading documents",
            system=False,
            created_at=now,
            updated_at=now,
        )
