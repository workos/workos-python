import datetime

from workos.types.connect import ClientSecret


class MockClientSecret(ClientSecret):
    def __init__(self, id: str, include_secret: bool = False):
        now = datetime.datetime.now().isoformat()
        kwargs = {
            "object": "connect_application_secret",
            "id": id,
            "secret_hint": "...abcd",
            "last_used_at": None,
            "created_at": now,
            "updated_at": now,
        }
        if include_secret:
            kwargs["secret"] = "sk_test_secret_value_123"
        super().__init__(**kwargs)
