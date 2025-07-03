import pytest
from tests.utils.fixtures.mock_vault_object import (
    MockVaultObject,
    MockObjectVersion,
    MockObjectDigest,
    MockObjectMetadata,
)
from tests.utils.list_resource import list_response_of
from tests.utils.syncify import syncify
from workos.vault import Vault
from workos.types.vault.key import KeyContext


class TestVault:
    @pytest.fixture(autouse=True)
    def setup(self, sync_http_client_for_test):
        self.http_client = sync_http_client_for_test
        self.vault = Vault(http_client=self.http_client)

    @pytest.fixture
    def mock_vault_object(self):
        return MockVaultObject(
            "vault_01234567890abcdef", "test-secret", "secret-value"
        ).dict()

    @pytest.fixture
    def mock_object_digest(self):
        return MockObjectDigest("vault_01234567890abcdef", "test-secret").dict()

    @pytest.fixture
    def mock_object_metadata(self):
        return MockObjectMetadata("vault_01234567890abcdef").dict()

    @pytest.fixture
    def mock_vault_object_no_value(self):
        mock_obj = MockVaultObject("vault_01234567890abcdef", "test-secret")
        mock_obj.value = None
        return mock_obj.dict()

    @pytest.fixture
    def mock_vault_objects_list(self):
        vault_objects = [
            MockObjectDigest(f"vault_{i}", f"secret-{i}").dict() for i in range(5)
        ]
        return {
            "data": vault_objects,
            "list_metadata": {"before": None, "after": None},
            "object": "list",
        }

    @pytest.fixture
    def mock_vault_objects_multiple_pages(self):
        vault_objects = [
            MockObjectDigest(f"vault_{i}", f"secret-{i}").dict() for i in range(25)
        ]
        return list_response_of(data=vault_objects)

    @pytest.fixture
    def mock_object_versions(self):
        versions = [
            MockObjectVersion(f"version_{i}", current_version=(i == 0)).dict()
            for i in range(3)
        ]
        return {"data": versions}

    @pytest.fixture
    def mock_data_key(self):
        return {
            "id": "key_01234567890abcdef",
            "data_key": "MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY=",
        }

    @pytest.fixture
    def mock_data_key_pair(self):
        return {
            "context": {"key": "test-key"},
            "id": "key_01234567890abcdef",
            "data_key": "MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY=",
            "encrypted_keys": "ZW5jcnlwdGVkX2tleXNfZGF0YQ==",
        }

    def test_read_object_success(
        self, mock_vault_object, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_vault_object, 200
        )

        vault_object = self.vault.read_object(object_id="vault_01234567890abcdef")

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith("/vault/v1/kv/vault_01234567890abcdef")
        assert vault_object.id == "vault_01234567890abcdef"
        assert vault_object.name == "test-secret"
        assert vault_object.value == "secret-value"
        assert vault_object.metadata.environment_id == "env_01234567890abcdef"

    def test_read_object_missing_object_id(self):
        with pytest.raises(
            ValueError, match="Incomplete arguments: 'object_id' is a required argument"
        ):
            self.vault.read_object(object_id="")

    def test_read_object_none_object_id(self):
        with pytest.raises(
            ValueError, match="Incomplete arguments: 'object_id' is a required argument"
        ):
            self.vault.read_object(object_id=None)

    def test_list_objects_default_params(
        self, mock_vault_objects_list, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_vault_objects_list, 200
        )

        vault_objects = self.vault.list_objects()

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith("/vault/v1/kv")
        assert request_kwargs["params"]["limit"] == 10
        assert "before" not in request_kwargs["params"]
        assert "after" not in request_kwargs["params"]
        assert len(vault_objects.data) == 5
        assert vault_objects.data[0].id == "vault_0"
        assert vault_objects.data[0].name == "secret-0"

    def test_list_objects_with_params(
        self, mock_vault_objects_list, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_vault_objects_list, 200
        )

        vault_objects = self.vault.list_objects(
            limit=5, before="vault_before", after="vault_after"
        )

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith("/vault/v1/kv")
        assert request_kwargs["params"]["limit"] == 5
        assert request_kwargs["params"]["before"] == "vault_before"
        assert request_kwargs["params"]["after"] == "vault_after"

    def test_list_objects_auto_pagination(
        self, mock_vault_objects_multiple_pages, test_auto_pagination
    ):
        test_auto_pagination(
            http_client=self.http_client,
            list_function=self.vault.list_objects,
            expected_all_page_data=mock_vault_objects_multiple_pages["data"],
        )

    def test_list_object_versions_success(
        self, mock_object_versions, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_object_versions, 200
        )

        versions = self.vault.list_object_versions(object_id="vault_01234567890abcdef")

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith(
            "/vault/v1/kv/vault_01234567890abcdef/versions"
        )
        assert len(versions) == 3
        assert versions[0].id == "version_0"
        assert versions[0].current_version is True
        assert versions[1].current_version is False

    def test_list_object_versions_empty_data(
        self, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, {"data": []}, 200
        )

        versions = self.vault.list_object_versions(object_id="vault_01234567890abcdef")

        assert request_kwargs["method"] == "get"
        assert len(versions) == 0

    def test_create_object_success(
        self, mock_object_metadata, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_object_metadata, 200
        )

        object_metadata = self.vault.create_object(
            name="test-secret",
            value="secret-value",
            key_context=KeyContext({"key": "test-key"}),
        )

        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith("/vault/v1/kv")
        assert request_kwargs["json"]["name"] == "test-secret"
        assert request_kwargs["json"]["value"] == "secret-value"
        assert request_kwargs["json"]["key_context"] == KeyContext({"key": "test-key"})
        assert object_metadata.id == "vault_01234567890abcdef"

    def test_create_object_missing_name(self):
        with pytest.raises(
            ValueError,
            match="Incomplete arguments: 'name' and 'value' are required arguments",
        ):
            self.vault.create_object(
                name="",
                value="secret-value",
                key_context=KeyContext({"key": "test-key"}),
            )

    def test_create_object_missing_value(self):
        with pytest.raises(
            ValueError,
            match="Incomplete arguments: 'name' and 'value' are required arguments",
        ):
            self.vault.create_object(
                name="test-secret",
                value="",
                key_context=KeyContext({"key": "test-key"}),
            )

    def test_create_object_missing_both(self):
        with pytest.raises(
            ValueError,
            match="Incomplete arguments: 'name' and 'value' are required arguments",
        ):
            self.vault.create_object(
                name="", value="", key_context=KeyContext({"key": "test-key"})
            )

    def test_update_object_with_value(
        self, mock_vault_object, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_vault_object, 200
        )

        vault_object = self.vault.update_object(
            object_id="vault_01234567890abcdef",
            value="updated-value",
        )

        assert request_kwargs["method"] == "put"
        assert request_kwargs["url"].endswith("/vault/v1/kv/vault_01234567890abcdef")
        assert request_kwargs["json"]["value"] == "updated-value"
        assert "version_check" not in request_kwargs["json"]
        assert vault_object.id == "vault_01234567890abcdef"

    def test_update_object_with_version_check(
        self, mock_vault_object, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_vault_object, 200
        )

        vault_object = self.vault.update_object(
            object_id="vault_01234567890abcdef",
            value="updated-value",
            version_check="version_123",
        )

        assert request_kwargs["method"] == "put"
        assert request_kwargs["json"]["value"] == "updated-value"
        assert request_kwargs["json"]["version_check"] == "version_123"

    def test_update_object_missing_value(self):
        with pytest.raises(
            TypeError, match="missing 1 required keyword-only argument: 'value'"
        ):
            self.vault.update_object(object_id="vault_01234567890abcdef")

    def test_update_object_missing_object_id(self):
        with pytest.raises(
            ValueError, match="Incomplete arguments: 'object_id' is a required argument"
        ):
            self.vault.update_object(object_id="", value="test-value")

    def test_update_object_none_object_id(self):
        with pytest.raises(
            ValueError,
            match="Incomplete arguments: 'object_id' is a required argument",
        ):
            self.vault.update_object(object_id=None, value="updated-value")

    def test_delete_object_success(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(self.http_client, {}, 204)

        result = self.vault.delete_object(object_id="vault_01234567890abcdef")

        assert request_kwargs["method"] == "delete"
        assert request_kwargs["url"].endswith("/vault/v1/kv/vault_01234567890abcdef")
        assert result is None

    def test_delete_object_missing_object_id(self):
        with pytest.raises(
            ValueError, match="Incomplete arguments: 'object_id' is a required argument"
        ):
            self.vault.delete_object(object_id="")

    def test_delete_object_none_object_id(self):
        with pytest.raises(
            ValueError, match="Incomplete arguments: 'object_id' is a required argument"
        ):
            self.vault.delete_object(object_id=None)

    def test_create_data_key_success(
        self, mock_data_key_pair, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_data_key_pair, 200
        )

        data_key_pair = self.vault.create_data_key(
            key_context=KeyContext({"key": "test-key"})
        )

        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith("/vault/v1/keys/data-key")
        assert request_kwargs["json"]["context"] == KeyContext({"key": "test-key"})
        assert data_key_pair.data_key.id == "key_01234567890abcdef"
        assert data_key_pair.encrypted_keys == "ZW5jcnlwdGVkX2tleXNfZGF0YQ=="

    def test_decrypt_data_key_success(
        self, mock_data_key, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_data_key, 200
        )

        data_key = self.vault.decrypt_data_key(keys="ZW5jcnlwdGVkX2tleXNfZGF0YQ==")

        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith("/vault/v1/keys/decrypt")
        assert request_kwargs["json"]["keys"] == "ZW5jcnlwdGVkX2tleXNfZGF0YQ=="
        assert data_key.id == "key_01234567890abcdef"
        assert data_key.key == "MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY="

    def test_encrypt_success(
        self, mock_data_key_pair, capture_and_mock_http_client_request
    ):
        # Mock the create_data_key call
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_data_key_pair, 200
        )

        plaintext = "Hello, World!"
        context = KeyContext({"key": "test-key"})

        encrypted_data = self.vault.encrypt(data=plaintext, key_context=context)

        # Verify create_data_key was called
        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith("/vault/v1/keys/data-key")
        assert request_kwargs["json"]["context"] == KeyContext({"key": "test-key"})

        # Verify we got encrypted data back
        assert isinstance(encrypted_data, str)
        assert len(encrypted_data) > 0

    def test_encrypt_with_associated_data(
        self, mock_data_key_pair, capture_and_mock_http_client_request
    ):
        # Mock the create_data_key call
        capture_and_mock_http_client_request(self.http_client, mock_data_key_pair, 200)

        plaintext = "Hello, World!"
        context = KeyContext({"key": "test-key"})
        associated_data = "additional-context"

        encrypted_data = self.vault.encrypt(
            data=plaintext, key_context=context, associated_data=associated_data
        )

        # Verify we got encrypted data back
        assert isinstance(encrypted_data, str)
        assert len(encrypted_data) > 0

    def test_decrypt_success(self, mock_data_key, capture_and_mock_http_client_request):
        # First encrypt some data to get a valid encrypted payload
        mock_data_key_pair = {
            "context": {"key": "test-key"},
            "id": "key_01234567890abcdef",
            "data_key": "MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY=",
            "encrypted_keys": "ZW5jcnlwdGVkX2tleXNfZGF0YQ==",
        }

        # Mock create_data_key for encryption
        capture_and_mock_http_client_request(self.http_client, mock_data_key_pair, 200)

        plaintext = "Hello, World!"
        context = KeyContext({"key": "test-key"})
        encrypted_data = self.vault.encrypt(data=plaintext, key_context=context)

        # Now mock decrypt_data_key for decryption
        capture_and_mock_http_client_request(self.http_client, mock_data_key, 200)

        # Decrypt the data
        decrypted_text = self.vault.decrypt(encrypted_data=encrypted_data)

        # Verify decryption worked
        assert decrypted_text == plaintext

    def test_decrypt_with_associated_data(
        self, mock_data_key, capture_and_mock_http_client_request
    ):
        # First encrypt some data with associated data
        mock_data_key_pair = {
            "context": {"key": "test-key"},
            "id": "key_01234567890abcdef",
            "data_key": "MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY=",
            "encrypted_keys": "ZW5jcnlwdGVkX2tleXNfZGF0YQ==",
        }

        # Mock create_data_key for encryption
        capture_and_mock_http_client_request(self.http_client, mock_data_key_pair, 200)

        plaintext = "Hello, World!"
        context = KeyContext({"key": "test-key"})
        associated_data = "additional-context"
        encrypted_data = self.vault.encrypt(
            data=plaintext, key_context=context, associated_data=associated_data
        )

        # Now mock decrypt_data_key for decryption
        capture_and_mock_http_client_request(self.http_client, mock_data_key, 200)

        # Decrypt the data with the same associated data
        decrypted_text = self.vault.decrypt(
            encrypted_data=encrypted_data, associated_data=associated_data
        )

        # Verify decryption worked
        assert decrypted_text == plaintext

    def test_encrypt_decrypt_roundtrip(
        self, mock_data_key_pair, mock_data_key, capture_and_mock_http_client_request
    ):
        """Test that encrypt/decrypt works correctly together"""

        # Mock create_data_key for encryption
        capture_and_mock_http_client_request(self.http_client, mock_data_key_pair, 200)

        plaintext = "This is a test message for encryption!"
        context = KeyContext({"env": "test", "service": "vault"})

        # Encrypt the data
        encrypted_data = self.vault.encrypt(data=plaintext, key_context=context)

        # Mock decrypt_data_key for decryption
        capture_and_mock_http_client_request(self.http_client, mock_data_key, 200)

        # Decrypt the data
        decrypted_text = self.vault.decrypt(encrypted_data=encrypted_data)

        # Verify roundtrip worked
        assert decrypted_text == plaintext
