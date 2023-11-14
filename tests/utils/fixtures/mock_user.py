import datetime
from workos.resources.base import WorkOSBaseResource


class MockUser(WorkOSBaseResource):
    def __init__(self, id):
        self.id = id
        self.email = "marcelina@foo-corp.com"
        self.first_name = "Marcelina"
        self.last_name = "Hoeger"
        self.email_verified_at = ""
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()

    OBJECT_FIELDS = [
        "id",
        "email",
        "first_name",
        "last_name",
        "sso_profile_id",
        "email_verified_at",
        "created_at",
        "updated_at",
    ]
