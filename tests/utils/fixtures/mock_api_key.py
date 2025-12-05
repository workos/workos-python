import datetime

from workos.types.api_keys import ApiKey


class MockApiKey(ApiKey):
    def __init__(self, id="api_key_01234567890"):
        now = datetime.datetime.now().isoformat()
        super().__init__(
            object="api_key",
            id=id,
            owner={"type": "organization", "id": "org_1337"},
            name="Development API Key",
            obfuscated_value="api_..0",
            permissions=[],
            last_used_at=now,
            created_at=now,
            updated_at=now,
        )
