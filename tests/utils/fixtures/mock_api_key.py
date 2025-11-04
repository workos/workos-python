import datetime

from workos.types.api_keys import ApiKey


class MockApiKey(ApiKey):
    def __init__(self, id="api_key_01234567890"):
        now = datetime.datetime.now().isoformat()
        super().__init__(
            object="api_key",
            id=id,
            name="Development API Key",
            last_used_at=now,
            created_at=now,
            updated_at=now,
        )
