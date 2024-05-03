import datetime
from workos.resources.base import WorkOSBaseResource


class MockMagicAuth(WorkOSBaseResource):
    def __init__(self, id):
        self.id = id
        self.user_id = "user_01HWZBQAY251RZ9BKB4RZW4D4A"
        self.email = "marcelina@foo-corp.com"
        self.expires_at = datetime.datetime.now()
        self.code = "123456"
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()

    OBJECT_FIELDS = [
        "id",
        "user_id",
        "email",
        "expires_at",
        "code",
        "created_at",
        "updated_at",
    ]
