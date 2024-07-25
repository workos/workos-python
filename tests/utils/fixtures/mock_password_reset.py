import datetime
from workos.resources.base import WorkOSBaseResource


class MockPasswordReset(WorkOSBaseResource):
    def __init__(self, id):
        now = datetime.datetime.now().isoformat()
        self.object = "password_reset"
        self.id = id
        self.user_id = "user_01HWZBQAY251RZ9BKB4RZW4D4A"
        self.email = "marcelina@foo-corp.com"
        self.password_reset_token = "Z1uX3RbwcIl5fIGJJJCXXisdI"
        self.password_reset_url = (
            "https://your-app.com/reset-password?token=Z1uX3RbwcIl5fIGJJJCXXisdI"
        )
        self.expires_at = now
        self.created_at = now

    OBJECT_FIELDS = [
        "object",
        "id",
        "user_id",
        "email",
        "password_reset_token",
        "password_reset_url",
        "expires_at",
        "created_at",
    ]
