import datetime

from workos.types.user_management import User


class MockUser(User):
    def __init__(self, id):
        now = datetime.datetime.now().isoformat()
        super().__init__(
            object="user",
            id=id,
            email="marcelina@foo-corp.com",
            first_name="Marcelina",
            last_name="Hoeger",
            email_verified=False,
            profile_picture_url="https://example.com/profile-picture.jpg",
            last_sign_in_at="2021-06-25T19:07:33.155Z",
            created_at=now,
            updated_at=now,
            metadata={"key": "value"},
        )
