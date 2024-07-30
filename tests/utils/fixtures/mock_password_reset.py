import datetime

from workos.resources.user_management import PasswordReset


class MockPasswordReset(PasswordReset):
    def __init__(self, id):
        now = datetime.datetime.now().isoformat()
        super().__init__(
            object="password_reset",
            id=id,
            user_id="user_01HWZBQAY251RZ9BKB4RZW4D4A",
            email="marcelina@foo-corp.com",
            password_reset_token="Z1uX3RbwcIl5fIGJJJCXXisdI",
            password_reset_url="https://your-app.com/reset-password?token=Z1uX3RbwcIl5fIGJJJCXXisdI",
            expires_at=now,
            created_at=now,
        )
