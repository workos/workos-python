import datetime

from workos.types.vault import (
    VaultObject,
    ObjectDigest,
    ObjectMetadata,
    ObjectUpdateBy,
    ObjectVersion,
    KeyContext,
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


class MockObjectDigest(ObjectDigest):
    def __init__(self, id="vault_01234567890abcdef", name="test-secret"):
        now = datetime.datetime.now().isoformat()
        super().__init__(id=id, name=name, updated_at=now)


class MockObjectMetadata(ObjectMetadata):
    def __init__(self, id="vault_01234567890abcdef"):
        now = datetime.datetime.now().isoformat()
        super().__init__(
            context=KeyContext(key="test-key"),
            environment_id="env_01234567890abcdef",
            id=id,
            key_id="key_01234567890abcdef",
            updated_at=now,
            updated_by=ObjectUpdateBy(id="user_01234567890abcdef", name="Test User"),
            version_id="version_01234567890abcdef",
        )


class MockObjectVersion(ObjectVersion):
    def __init__(self, id="version_01234567890abcdef", current_version=True):
        now = datetime.datetime.now().isoformat()
        super().__init__(
            id=id,
            created_at=now,
            current_version=current_version,
        )
