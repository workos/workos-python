import datetime

from workos.types.user_management import EmailVerification


class MockEmailVerification(EmailVerification):
    def __init__(self, id):
        now = datetime.datetime.now().isoformat()
        super().__init__(
            object="email_verification",
            id=id,
            user_id="user_01HWZBQAY251RZ9BKB4RZW4D4A",
            email="marcelina@foo-corp.com",
            expires_at=now,
            code="123456",
            created_at=now,
            updated_at=now,
        )
