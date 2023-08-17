import datetime
from workos.resources.base import WorkOSBaseResource


class MockUser(WorkOSBaseResource):
    def __init__(self, id):
        self.id = id
        self.email = "marcelina@foo-corp.com"
        self.first_name = "Marcelina"
        self.last_name = "Hoeger"
        self.user_type = "unmanaged"
        self.sso_profile_id = None
        self.email_verified_at = ""
        self.google_oauth_profile_id = None
        self.microsoft_oauth_profile_id = None
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()

    OBJECT_FIELDS = [
        "id",
        "email",
        "first_name",
        "last_name",
        "user_type",
        "sso_profile_id",
        "email_verified_at",
        "google_oauth_profile_id",
        "microsoft_oauth_profile_id",
        "created_at",
        "updated_at",
    ]
