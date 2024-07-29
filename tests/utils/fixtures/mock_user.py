import datetime
from workos.resources.base import WorkOSBaseResource


class MockUser(WorkOSBaseResource):
    def __init__(self, id):
        now = datetime.datetime.now().isoformat()
        self.object = "user"
        self.id = id
        self.email = "marcelina@foo-corp.com"
        self.first_name = "Marcelina"
        self.last_name = "Hoeger"
        self.email_verified = False
        self.profile_picture_url = "https://example.com/profile-picture.jpg"
        self.created_at = now
        self.updated_at = now

    OBJECT_FIELDS = [
        "object",
        "id",
        "email",
        "first_name",
        "last_name",
        "profile_picture_url",
        "email_verified",
        "created_at",
        "updated_at",
    ]
