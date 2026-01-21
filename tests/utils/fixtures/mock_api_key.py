import datetime

from workos.types.api_keys import ApiKey, ApiKeyWithValue


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


class MockApiKeyWithValue(ApiKeyWithValue):
    def __init__(self, id="api_key_01234567890"):
        now = datetime.datetime.now().isoformat()
        super().__init__(
            object="api_key",
            id=id,
            owner={"type": "organization", "id": "org_1337"},
            name="Development API Key",
            obfuscated_value="sk_...xyz",
            value="sk_live_abc123xyz",
            permissions=["posts:read", "posts:write"],
            last_used_at=None,
            created_at=now,
            updated_at=now,
        )
