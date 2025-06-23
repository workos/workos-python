import datetime

from workos.types.vault import (
    VaultObject,
    ObjectMetadata,
    ObjectUpdateBy,
    ObjectVersion,
    KeyContext,
)
from workos.types.vault.key import (
    DataKey,
    DataKeyPair,
    KeyContext as VaultKeyContext,
)


class MockVaultObject(VaultObject):
    def __init__(
        self, id="vault_01234567890abcdef", name="test-secret", value="secret-value"
    ):
        now = datetime.datetime.now().isoformat()
        super().__init__(
            id=id,
            name=name,
            value=value,
            metadata=ObjectMetadata(
                context=KeyContext(key="test-key"),
                environment_id="env_01234567890abcdef",
                id=id,
                key_id="key_01234567890abcdef",
                updated_at=now,
                updated_by=ObjectUpdateBy(
                    id="user_01234567890abcdef", name="Test User"
                ),
                version_id="version_01234567890abcdef",
            ),
        )


class MockObjectVersion(ObjectVersion):
    def __init__(self, id="version_01234567890abcdef", current_version=True):
        now = datetime.datetime.now().isoformat()
        super().__init__(
            id=id,
            created_at=now,
            current_version=current_version,
        )


class MockDataKey(DataKey):
    def __init__(
        self,
        id="key_01234567890abcdef",
        key="MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY=",
    ):
        super().__init__(
            id=id,
            key=key,
        )


class MockDataKeyPair(DataKeyPair):
    def __init__(
        self, context=None, data_key=None, encrypted_keys="ZW5jcnlwdGVkX2tleXNfZGF0YQ=="
    ):
        if context is None:
            context = VaultKeyContext({"key": "test-key"})
        if data_key is None:
            data_key = MockDataKey()
        super().__init__(
            context=context,
            data_key=data_key,
            encrypted_keys=encrypted_keys,
        )
