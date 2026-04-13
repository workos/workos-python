# @oagen-ignore-file
import json

import pytest
from workos import WorkOSClient, AsyncWorkOSClient
from tests.generated_helpers import load_fixture

from workos.vault import (
    DataKey,
    DataKeyPair,
    ObjectDigest,
    ObjectMetadata,
    ObjectVersion,
    VaultObject,
)
from workos._errors import (
    AuthenticationError,
    NotFoundError,
    RateLimitExceededError,
    ServerError,
)


class TestVault:
    def test_read_object(self, workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("vault_object.json"))
        result = workos.vault.read_object(
            object_id="vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C"
        )
        assert isinstance(result, VaultObject)
        assert result.id == "vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C"
        assert result.name == "my-secret"
        assert result.value == "super-secret-value"
        request = httpx_mock.get_request()
        assert request.method == "GET"
        assert request.url.path.endswith(
            "/vault/v1/kv/vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C"
        )

    def test_read_object_by_name(self, workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("vault_object.json"))
        result = workos.vault.read_object_by_name(name="my-secret")
        assert isinstance(result, VaultObject)
        assert result.name == "my-secret"
        request = httpx_mock.get_request()
        assert request.method == "GET"
        assert request.url.path.endswith("/vault/v1/kv/name/my-secret")

    def test_get_object_metadata(self, workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("vault_object_metadata.json"))
        result = workos.vault.get_object_metadata(
            object_id="vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C"
        )
        assert isinstance(result, VaultObject)
        assert result.id == "vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C"
        assert result.name == "my-secret"
        assert result.value is None
        request = httpx_mock.get_request()
        assert request.method == "GET"
        assert request.url.path.endswith(
            "/vault/v1/kv/vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C/metadata"
        )

    def test_list_objects(self, workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("vault_list_objects.json"))
        result = workos.vault.list_objects()
        assert len(result) == 1
        assert isinstance(result[0], ObjectDigest)
        assert result[0].id == "vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C"
        request = httpx_mock.get_request()
        assert request.method == "GET"
        assert request.url.path.endswith("/vault/v1/kv")

    def test_list_objects_with_params(self, workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("vault_list_objects.json"))
        workos.vault.list_objects(limit=5, after="cursor_abc")
        request = httpx_mock.get_request()
        assert "limit=5" in str(request.url)
        assert "after=cursor_abc" in str(request.url)

    def test_list_object_versions(self, workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("vault_list_object_versions.json"))
        result = workos.vault.list_object_versions(
            object_id="vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C"
        )
        assert len(result) == 1
        assert isinstance(result[0], ObjectVersion)
        assert result[0].current_version is True
        request = httpx_mock.get_request()
        assert request.method == "GET"
        assert request.url.path.endswith(
            "/vault/v1/kv/vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C/versions"
        )

    def test_create_object(self, workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("vault_create_object.json"))
        result = workos.vault.create_object(
            name="my-secret",
            value="super-secret-value",
            key_context={"tenant": "acme"},
        )
        assert isinstance(result, ObjectMetadata)
        assert result.id == "vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C"
        request = httpx_mock.get_request()
        assert request.method == "POST"
        assert request.url.path.endswith("/vault/v1/kv")
        body = json.loads(request.content)
        assert body["name"] == "my-secret"
        assert body["value"] == "super-secret-value"
        assert body["key_context"] == {"tenant": "acme"}

    def test_update_object(self, workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("vault_object.json"))
        result = workos.vault.update_object(
            object_id="vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C",
            value="new-secret-value",
        )
        assert isinstance(result, VaultObject)
        request = httpx_mock.get_request()
        assert request.method == "PUT"
        assert request.url.path.endswith(
            "/vault/v1/kv/vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C"
        )
        body = json.loads(request.content)
        assert body["value"] == "new-secret-value"

    def test_update_object_with_version_check(self, workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("vault_object.json"))
        workos.vault.update_object(
            object_id="vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C",
            value="new-secret-value",
            version_check="vault_ver_01EHDAK2BFGWCSZXP9HGZ3VK8C",
        )
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body["version_check"] == "vault_ver_01EHDAK2BFGWCSZXP9HGZ3VK8C"

    def test_delete_object(self, workos, httpx_mock):
        httpx_mock.add_response(status_code=204)
        workos.vault.delete_object(object_id="vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C")
        request = httpx_mock.get_request()
        assert request.method == "DELETE"
        assert request.url.path.endswith(
            "/vault/v1/kv/vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C"
        )

    def test_create_data_key(self, workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("vault_data_key.json"))
        result = workos.vault.create_data_key(key_context={"tenant": "acme"})
        assert isinstance(result, DataKeyPair)
        assert isinstance(result.data_key, DataKey)
        assert result.data_key.id == "vault_key_01EHDAK2BFGWCSZXP9HGZ3VK8C"
        assert result.context == {"tenant": "acme"}
        request = httpx_mock.get_request()
        assert request.method == "POST"
        assert request.url.path.endswith("/vault/v1/keys/data-key")

    def test_decrypt_data_key(self, workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("vault_decrypt_key.json"))
        result = workos.vault.decrypt_data_key(keys="dGVzdC1lbmNyeXB0ZWQta2V5cw==")
        assert isinstance(result, DataKey)
        assert result.id == "vault_key_01EHDAK2BFGWCSZXP9HGZ3VK8C"
        request = httpx_mock.get_request()
        assert request.method == "POST"
        assert request.url.path.endswith("/vault/v1/keys/decrypt")

    def test_encrypt_decrypt_round_trip(self, workos, httpx_mock):
        # Mock create_data_key for encrypt
        httpx_mock.add_response(json=load_fixture("vault_data_key.json"))
        # Mock decrypt_data_key for decrypt
        httpx_mock.add_response(json=load_fixture("vault_decrypt_key.json"))

        encrypted = workos.vault.encrypt(
            data="hello world", key_context={"tenant": "acme"}
        )
        assert isinstance(encrypted, str)
        assert encrypted != "hello world"

        decrypted = workos.vault.decrypt(encrypted_data=encrypted)
        assert decrypted == "hello world"

    def test_read_object_unauthorized(self, workos, httpx_mock):
        httpx_mock.add_response(
            status_code=401,
            json={"message": "Unauthorized"},
        )
        with pytest.raises(AuthenticationError):
            workos.vault.read_object(object_id="vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C")

    def test_read_object_not_found(self, httpx_mock):
        workos = WorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        try:
            httpx_mock.add_response(status_code=404, json={"message": "Not found"})
            with pytest.raises(NotFoundError):
                workos.vault.read_object(
                    object_id="vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C"
                )
        finally:
            workos.close()

    def test_read_object_rate_limited(self, httpx_mock):
        workos = WorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        try:
            httpx_mock.add_response(
                status_code=429,
                headers={"Retry-After": "0"},
                json={"message": "Slow down"},
            )
            with pytest.raises(RateLimitExceededError):
                workos.vault.read_object(
                    object_id="vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C"
                )
        finally:
            workos.close()

    def test_read_object_server_error(self, httpx_mock):
        workos = WorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        try:
            httpx_mock.add_response(status_code=500, json={"message": "Server error"})
            with pytest.raises(ServerError):
                workos.vault.read_object(
                    object_id="vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C"
                )
        finally:
            workos.close()


@pytest.mark.asyncio
class TestAsyncVault:
    async def test_read_object(self, async_workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("vault_object.json"))
        result = await async_workos.vault.read_object(
            object_id="vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C"
        )
        assert isinstance(result, VaultObject)
        assert result.id == "vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C"
        assert result.name == "my-secret"
        request = httpx_mock.get_request()
        assert request.method == "GET"
        assert request.url.path.endswith(
            "/vault/v1/kv/vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C"
        )

    async def test_read_object_by_name(self, async_workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("vault_object.json"))
        result = await async_workos.vault.read_object_by_name(name="my-secret")
        assert isinstance(result, VaultObject)
        request = httpx_mock.get_request()
        assert request.url.path.endswith("/vault/v1/kv/name/my-secret")

    async def test_get_object_metadata(self, async_workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("vault_object_metadata.json"))
        result = await async_workos.vault.get_object_metadata(
            object_id="vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C"
        )
        assert isinstance(result, VaultObject)
        assert result.value is None
        request = httpx_mock.get_request()
        assert request.method == "GET"
        assert request.url.path.endswith(
            "/vault/v1/kv/vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C/metadata"
        )

    async def test_list_objects(self, async_workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("vault_list_objects.json"))
        result = await async_workos.vault.list_objects()
        assert len(result) == 1
        assert isinstance(result[0], ObjectDigest)
        request = httpx_mock.get_request()
        assert request.method == "GET"
        assert request.url.path.endswith("/vault/v1/kv")

    async def test_list_object_versions(self, async_workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("vault_list_object_versions.json"))
        result = await async_workos.vault.list_object_versions(
            object_id="vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C"
        )
        assert len(result) == 1
        assert isinstance(result[0], ObjectVersion)
        request = httpx_mock.get_request()
        assert request.url.path.endswith(
            "/vault/v1/kv/vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C/versions"
        )

    async def test_create_object(self, async_workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("vault_create_object.json"))
        result = await async_workos.vault.create_object(
            name="my-secret",
            value="super-secret-value",
            key_context={"tenant": "acme"},
        )
        assert isinstance(result, ObjectMetadata)
        request = httpx_mock.get_request()
        assert request.method == "POST"
        assert request.url.path.endswith("/vault/v1/kv")

    async def test_update_object(self, async_workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("vault_object.json"))
        result = await async_workos.vault.update_object(
            object_id="vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C",
            value="new-secret-value",
        )
        assert isinstance(result, VaultObject)
        request = httpx_mock.get_request()
        assert request.method == "PUT"

    async def test_delete_object(self, async_workos, httpx_mock):
        httpx_mock.add_response(status_code=204)
        await async_workos.vault.delete_object(
            object_id="vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C"
        )
        request = httpx_mock.get_request()
        assert request.method == "DELETE"

    async def test_create_data_key(self, async_workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("vault_data_key.json"))
        result = await async_workos.vault.create_data_key(
            key_context={"tenant": "acme"}
        )
        assert isinstance(result, DataKeyPair)
        assert isinstance(result.data_key, DataKey)
        request = httpx_mock.get_request()
        assert request.method == "POST"
        assert request.url.path.endswith("/vault/v1/keys/data-key")

    async def test_decrypt_data_key(self, async_workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("vault_decrypt_key.json"))
        result = await async_workos.vault.decrypt_data_key(
            keys="dGVzdC1lbmNyeXB0ZWQta2V5cw=="
        )
        assert isinstance(result, DataKey)
        request = httpx_mock.get_request()
        assert request.method == "POST"
        assert request.url.path.endswith("/vault/v1/keys/decrypt")

    async def test_encrypt_decrypt_round_trip(self, async_workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("vault_data_key.json"))
        httpx_mock.add_response(json=load_fixture("vault_decrypt_key.json"))

        encrypted = await async_workos.vault.encrypt(
            data="hello world", key_context={"tenant": "acme"}
        )
        assert isinstance(encrypted, str)

        decrypted = await async_workos.vault.decrypt(encrypted_data=encrypted)
        assert decrypted == "hello world"

    async def test_read_object_unauthorized(self, async_workos, httpx_mock):
        httpx_mock.add_response(status_code=401, json={"message": "Unauthorized"})
        with pytest.raises(AuthenticationError):
            await async_workos.vault.read_object(
                object_id="vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C"
            )

    async def test_read_object_not_found(self, httpx_mock):
        workos = AsyncWorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        try:
            httpx_mock.add_response(status_code=404, json={"message": "Not found"})
            with pytest.raises(NotFoundError):
                await workos.vault.read_object(
                    object_id="vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C"
                )
        finally:
            await workos.close()

    async def test_read_object_rate_limited(self, httpx_mock):
        workos = AsyncWorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        try:
            httpx_mock.add_response(
                status_code=429,
                headers={"Retry-After": "0"},
                json={"message": "Slow down"},
            )
            with pytest.raises(RateLimitExceededError):
                await workos.vault.read_object(
                    object_id="vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C"
                )
        finally:
            await workos.close()

    async def test_read_object_server_error(self, httpx_mock):
        workos = AsyncWorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        try:
            httpx_mock.add_response(status_code=500, json={"message": "Server error"})
            with pytest.raises(ServerError):
                await workos.vault.read_object(
                    object_id="vault_obj_01EHDAK2BFGWCSZXP9HGZ3VK8C"
                )
        finally:
            await workos.close()
