import datetime
from workos.resources.base import WorkOSBaseResource


class MockMagicAuth(WorkOSBaseResource):
    def __init__(self, id):
        now = datetime.datetime.now().isoformat()
        self.object = "magic_auth"
        self.id = id
        self.user_id = "user_01HWZBQAY251RZ9BKB4RZW4D4A"
        self.email = "marcelina@foo-corp.com"
        self.expires_at = now
        self.code = "123456"
        self.created_at = now
        self.updated_at = now

    OBJECT_FIELDS = [
        "object",
        "id",
        "user_id",
        "email",
        "expires_at",
        "code",
        "created_at",
        "updated_at",
    ]
