# @oagen-ignore-file
# This file is hand-maintained. The vault API endpoints are not yet in the
# OpenAPI spec, so this module provides the functionality until they are.
# The encrypt/decrypt methods use client-side AES-GCM and will always be
# hand-maintained regardless of spec coverage.

from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Optional,
    Sequence,
    Tuple,
)

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

if TYPE_CHECKING:
    from ._client import AsyncWorkOSClient, WorkOSClient

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

KeyContext = Dict[str, str]


@dataclass(slots=True)
class DataKey:
    """A plaintext data key used for local encryption operations."""

    id: str
    """The unique identifier for this data key."""
    key: str
    """The base64-encoded plaintext key material."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DataKey":
        return cls(id=data["id"], key=data["key"])

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "key": self.key}


@dataclass(slots=True)
class DataKeyPair:
    """A data key pair containing both the plaintext key and its encrypted form."""

    context: KeyContext
    """The key context used to generate this key pair."""
    data_key: DataKey
    """The plaintext data key for local encryption."""
    encrypted_keys: str
    """The encrypted form of the data key, for storage alongside ciphertext."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DataKeyPair":
        return cls(
            context=data["context"],
            data_key=DataKey.from_dict(data["data_key"]),
            encrypted_keys=data["encrypted_keys"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "context": self.context,
            "data_key": self.data_key.to_dict(),
            "encrypted_keys": self.encrypted_keys,
        }


@dataclass(slots=True)
class DecodedKeys:
    """Decoded components of an encrypted payload."""

    iv: bytes
    """The initialization vector for AES-GCM decryption."""
    tag: bytes
    """The authentication tag for AES-GCM verification."""
    keys: str
    """Base64-encoded encrypted key material."""
    ciphertext: bytes
    """The encrypted data."""


@dataclass(slots=True)
class ObjectUpdateBy:
    """The user or system that last updated a Vault object."""

    id: str
    """The unique identifier of the updater."""
    name: str
    """The display name of the updater."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ObjectUpdateBy":
        return cls(id=data["id"], name=data["name"])

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name}


@dataclass(slots=True)
class ObjectMetadata:
    """Metadata for a Vault encrypted object, returned after create or update."""

    context: KeyContext
    """The key context associated with this object."""
    environment_id: str
    """The WorkOS environment ID."""
    id: str
    """The unique identifier of the Vault object."""
    key_id: str
    """The encryption key ID used for this object."""
    updated_at: str
    """ISO 8601 timestamp of the last update."""
    updated_by: ObjectUpdateBy
    """The user or system that last updated this object."""
    version_id: str
    """The version identifier for this object revision."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ObjectMetadata":
        return cls(
            context=data["context"],
            environment_id=data["environment_id"],
            id=data["id"],
            key_id=data["key_id"],
            updated_at=data["updated_at"],
            updated_by=ObjectUpdateBy.from_dict(data["updated_by"]),
            version_id=data["version_id"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "context": self.context,
            "environment_id": self.environment_id,
            "id": self.id,
            "key_id": self.key_id,
            "updated_at": self.updated_at,
            "updated_by": self.updated_by.to_dict(),
            "version_id": self.version_id,
        }


@dataclass(slots=True)
class VaultObject:
    """A Vault encrypted object with its metadata and optionally decrypted value."""

    id: str
    """The unique identifier of the Vault object."""
    metadata: ObjectMetadata
    """The object's metadata including key context and version info."""
    name: str
    """The name of the Vault object."""
    value: Optional[str] = None
    """The decrypted value, present only when explicitly requested."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VaultObject":
        return cls(
            id=data["id"],
            metadata=ObjectMetadata.from_dict(data["metadata"]),
            name=data["name"],
            value=data.get("value"),
        )

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "id": self.id,
            "metadata": self.metadata.to_dict(),
            "name": self.name,
        }
        if self.value is not None:
            result["value"] = self.value
        return result


@dataclass(slots=True)
class ObjectDigest:
    """A summary of a Vault object returned in list operations."""

    id: str
    """The unique identifier of the Vault object."""
    name: str
    """The name of the Vault object."""
    updated_at: str
    """ISO 8601 timestamp of the last update."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ObjectDigest":
        return cls(id=data["id"], name=data["name"], updated_at=data["updated_at"])

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "name": self.name, "updated_at": self.updated_at}


@dataclass(slots=True)
class ObjectVersion:
    """A version entry for a Vault object."""

    created_at: str
    """ISO 8601 timestamp when this version was created."""
    current_version: bool
    """Whether this is the current (latest) version."""
    id: str
    """The unique identifier of this version."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ObjectVersion":
        return cls(
            created_at=data["created_at"],
            current_version=data["current_version"],
            id=data["id"],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "created_at": self.created_at,
            "current_version": self.current_version,
            "id": self.id,
        }


# ---------------------------------------------------------------------------
# Crypto helpers (AES-GCM, LEB128)
# ---------------------------------------------------------------------------


def _aes_gcm_encrypt(
    plaintext: bytes, key: bytes, iv: bytes, aad: Optional[bytes]
) -> Dict[str, bytes]:
    encryptor = Cipher(
        algorithms.AES(key), modes.GCM(iv), backend=default_backend()
    ).encryptor()
    if aad:
        encryptor.authenticate_additional_data(aad)
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    return {"ciphertext": ciphertext, "iv": iv, "tag": encryptor.tag}


def _aes_gcm_decrypt(
    ciphertext: bytes,
    key: bytes,
    iv: bytes,
    tag: bytes,
    aad: Optional[bytes] = None,
) -> bytes:
    decryptor = Cipher(
        algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend()
    ).decryptor()
    if aad:
        decryptor.authenticate_additional_data(aad)
    return decryptor.update(ciphertext) + decryptor.finalize()


def _encode_u32_leb128(value: int) -> bytes:
    """Encode a 32-bit unsigned integer as LEB128."""
    if value < 0 or value > 0xFFFFFFFF:
        raise ValueError("Value must be a 32-bit unsigned integer")
    encoded = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value != 0:
            byte |= 0x80
        encoded.append(byte)
        if value == 0:
            break
    return bytes(encoded)


def _decode_u32_leb128(buf: bytes) -> Tuple[int, int]:
    """Decode an unsigned LEB128-encoded 32-bit integer. Returns (value, bytes_consumed)."""
    res = 0
    bit = 0
    for i, b in enumerate(buf):
        if i >= 4 and (b & 0x80) != 0:
            raise ValueError("LEB128 integer overflow (was more than 4 bytes)")
        res |= (b & 0x7F) << (7 * bit)
        if (b & 0x80) == 0:
            if res > 0xFFFFFFFF:
                raise ValueError("LEB128 integer overflow (exceeds 32 bits)")
            return res, i + 1
        bit += 1
    raise ValueError("LEB128 integer not found")


def _decode_encrypted_payload(encrypted_data_b64: str) -> DecodedKeys:
    """Extract IV, tag, keyBlobLength, keyBlob, and ciphertext from a base64 payload.

    Format: [IV:12b][TAG:16b][LEB128 Length][keyBlob][ciphertext]
    """
    try:
        payload = base64.b64decode(encrypted_data_b64)
    except Exception as e:
        raise ValueError("Base64 decoding failed") from e

    iv = payload[0:12]
    tag = payload[12:28]
    key_len, leb_len = _decode_u32_leb128(payload[28:])
    keys_index = 28 + leb_len
    keys_end = keys_index + key_len
    keys_slice = payload[keys_index:keys_end]
    keys = base64.b64encode(keys_slice).decode("utf-8")
    ciphertext = payload[keys_end:]
    return DecodedKeys(iv=iv, tag=tag, keys=keys, ciphertext=ciphertext)


DEFAULT_RESPONSE_LIMIT = 10


# ---------------------------------------------------------------------------
# Sync Vault
# ---------------------------------------------------------------------------


class Vault:
    """WorkOS Vault service — encryption, key management, and secret storage."""

    def __init__(self, client: "WorkOSClient") -> None:
        self._client = client

    # -- KV operations --

    def read_object(self, *, object_id: str) -> VaultObject:
        """Get a Vault object with the value decrypted."""
        response = self._client.request(
            method="get",
            path=f"vault/v1/kv/{object_id}",
            model=VaultObject,
        )
        return response

    def read_object_by_name(self, *, name: str) -> VaultObject:
        """Get a Vault object by name with the value decrypted."""
        response = self._client.request(
            method="get",
            path=f"vault/v1/kv/name/{name}",
            model=VaultObject,
        )
        return response

    def get_object_metadata(self, *, object_id: str) -> VaultObject:
        """Get a Vault object's metadata without decrypting the value."""
        response = self._client.request(
            method="get",
            path=f"vault/v1/kv/{object_id}/metadata",
            model=VaultObject,
        )
        return response

    def list_objects(
        self,
        *,
        limit: int = DEFAULT_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> Sequence[ObjectDigest]:
        """Gets a list of encrypted Vault objects."""
        params: Dict[str, Any] = {"limit": limit}
        if before is not None:
            params["before"] = before
        if after is not None:
            params["after"] = after

        response = self._client.request_raw(
            method="get",
            path="vault/v1/kv",
            params=params,
        )
        data: List[Dict[str, Any]] = response.get("data", [])
        return [ObjectDigest.from_dict(item) for item in data]

    def list_object_versions(self, *, object_id: str) -> Sequence[ObjectVersion]:
        """Gets a list of versions for a specific Vault object."""
        response = self._client.request_raw(
            method="get",
            path=f"vault/v1/kv/{object_id}/versions",
        )
        data: List[Dict[str, Any]] = response.get("data", [])
        return [ObjectVersion.from_dict(v) for v in data]

    def create_object(
        self,
        *,
        name: str,
        value: str,
        key_context: KeyContext,
    ) -> ObjectMetadata:
        """Create a new Vault encrypted object."""
        response = self._client.request(
            method="post",
            path="vault/v1/kv",
            body={"name": name, "value": value, "key_context": key_context},
            model=ObjectMetadata,
        )
        return response

    def update_object(
        self,
        *,
        object_id: str,
        value: str,
        version_check: Optional[str] = None,
    ) -> VaultObject:
        """Update an existing Vault object."""
        body: Dict[str, Any] = {"value": value}
        if version_check is not None:
            body["version_check"] = version_check

        response = self._client.request(
            method="put",
            path=f"vault/v1/kv/{object_id}",
            body=body,
            model=VaultObject,
        )
        return response

    def delete_object(self, *, object_id: str) -> None:
        """Permanently delete a Vault encrypted object."""
        self._client.request(
            method="delete",
            path=f"vault/v1/kv/{object_id}",
        )

    # -- Key operations --

    def create_data_key(self, *, key_context: KeyContext) -> DataKeyPair:
        """Generate a data key for local encryption."""
        response = self._client.request_raw(
            method="post",
            path="vault/v1/keys/data-key",
            body={"context": key_context},
        )
        return DataKeyPair(
            context=response["context"],
            data_key=DataKey(id=response["id"], key=response["data_key"]),
            encrypted_keys=response["encrypted_keys"],
        )

    def decrypt_data_key(self, *, keys: str) -> DataKey:
        """Decrypt encrypted data keys previously generated by create_data_key."""
        response = self._client.request_raw(
            method="post",
            path="vault/v1/keys/decrypt",
            body={"keys": keys},
        )
        return DataKey(id=response["id"], key=response["data_key"])

    # -- Client-side encryption --

    def encrypt(
        self,
        *,
        data: str,
        key_context: KeyContext,
        associated_data: Optional[str] = None,
    ) -> str:
        """Encrypt data locally using AES-GCM with a data key derived from the context."""
        key_pair = self.create_data_key(key_context=key_context)

        key = base64.b64decode(key_pair.data_key.key)
        key_blob = base64.b64decode(key_pair.encrypted_keys)
        prefix_len_buffer = _encode_u32_leb128(len(key_blob))
        aad_buffer = associated_data.encode("utf-8") if associated_data else None
        iv = os.urandom(12)

        result = _aes_gcm_encrypt(data.encode("utf-8"), key, iv, aad_buffer)

        combined = (
            result["iv"]
            + result["tag"]
            + prefix_len_buffer
            + key_blob
            + result["ciphertext"]
        )
        return base64.b64encode(combined).decode("utf-8")

    def decrypt(
        self, *, encrypted_data: str, associated_data: Optional[str] = None
    ) -> str:
        """Decrypt data that was previously encrypted using the encrypt method."""
        decoded = _decode_encrypted_payload(encrypted_data)
        data_key = self.decrypt_data_key(keys=decoded.keys)

        key = base64.b64decode(data_key.key)
        aad_buffer = associated_data.encode("utf-8") if associated_data else None

        decrypted_bytes = _aes_gcm_decrypt(
            ciphertext=decoded.ciphertext,
            key=key,
            iv=decoded.iv,
            tag=decoded.tag,
            aad=aad_buffer,
        )
        return decrypted_bytes.decode("utf-8")


# ---------------------------------------------------------------------------
# Async Vault
# ---------------------------------------------------------------------------


class AsyncVault:
    """Async WorkOS Vault service."""

    def __init__(self, client: "AsyncWorkOSClient") -> None:
        self._client = client

    async def read_object(self, *, object_id: str) -> VaultObject:
        """Get a Vault object with the value decrypted."""
        response = await self._client.request(
            method="get",
            path=f"vault/v1/kv/{object_id}",
            model=VaultObject,
        )
        return response

    async def read_object_by_name(self, *, name: str) -> VaultObject:
        """Get a Vault object by name with the value decrypted."""
        response = await self._client.request(
            method="get",
            path=f"vault/v1/kv/name/{name}",
            model=VaultObject,
        )
        return response

    async def get_object_metadata(self, *, object_id: str) -> VaultObject:
        """Get a Vault object's metadata without decrypting the value."""
        response = await self._client.request(
            method="get",
            path=f"vault/v1/kv/{object_id}/metadata",
            model=VaultObject,
        )
        return response

    async def list_objects(
        self,
        *,
        limit: int = DEFAULT_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
    ) -> Sequence[ObjectDigest]:
        """Gets a list of encrypted Vault objects."""
        params: Dict[str, Any] = {"limit": limit}
        if before is not None:
            params["before"] = before
        if after is not None:
            params["after"] = after
        response = await self._client.request_raw(
            method="get",
            path="vault/v1/kv",
            params=params,
        )
        data: List[Dict[str, Any]] = response.get("data", [])
        return [ObjectDigest.from_dict(item) for item in data]

    async def list_object_versions(self, *, object_id: str) -> Sequence[ObjectVersion]:
        """Gets a list of versions for a specific Vault object."""
        response = await self._client.request_raw(
            method="get",
            path=f"vault/v1/kv/{object_id}/versions",
        )
        data: List[Dict[str, Any]] = response.get("data", [])
        return [ObjectVersion.from_dict(v) for v in data]

    async def create_object(
        self,
        *,
        name: str,
        value: str,
        key_context: KeyContext,
    ) -> ObjectMetadata:
        """Create a new Vault encrypted object."""
        response = await self._client.request(
            method="post",
            path="vault/v1/kv",
            body={"name": name, "value": value, "key_context": key_context},
            model=ObjectMetadata,
        )
        return response

    async def update_object(
        self,
        *,
        object_id: str,
        value: str,
        version_check: Optional[str] = None,
    ) -> VaultObject:
        """Update an existing Vault object."""
        body: Dict[str, Any] = {"value": value}
        if version_check is not None:
            body["version_check"] = version_check
        response = await self._client.request(
            method="put",
            path=f"vault/v1/kv/{object_id}",
            body=body,
            model=VaultObject,
        )
        return response

    async def delete_object(self, *, object_id: str) -> None:
        """Permanently delete a Vault encrypted object."""
        await self._client.request(
            method="delete",
            path=f"vault/v1/kv/{object_id}",
        )

    async def create_data_key(self, *, key_context: KeyContext) -> DataKeyPair:
        """Generate a data key for local encryption."""
        response = await self._client.request_raw(
            method="post",
            path="vault/v1/keys/data-key",
            body={"context": key_context},
        )
        return DataKeyPair(
            context=response["context"],
            data_key=DataKey(id=response["id"], key=response["data_key"]),
            encrypted_keys=response["encrypted_keys"],
        )

    async def decrypt_data_key(self, *, keys: str) -> DataKey:
        """Decrypt encrypted data keys previously generated by create_data_key."""
        response = await self._client.request_raw(
            method="post",
            path="vault/v1/keys/decrypt",
            body={"keys": keys},
        )
        return DataKey(id=response["id"], key=response["data_key"])

    async def encrypt(
        self,
        *,
        data: str,
        key_context: KeyContext,
        associated_data: Optional[str] = None,
    ) -> str:
        """Encrypt data locally using AES-GCM with a data key derived from the context."""
        key_pair = await self.create_data_key(key_context=key_context)

        key = base64.b64decode(key_pair.data_key.key)
        key_blob = base64.b64decode(key_pair.encrypted_keys)
        prefix_len_buffer = _encode_u32_leb128(len(key_blob))
        aad_buffer = associated_data.encode("utf-8") if associated_data else None
        iv = os.urandom(12)

        result = _aes_gcm_encrypt(data.encode("utf-8"), key, iv, aad_buffer)
        combined = (
            result["iv"]
            + result["tag"]
            + prefix_len_buffer
            + key_blob
            + result["ciphertext"]
        )
        return base64.b64encode(combined).decode("utf-8")

    async def decrypt(
        self, *, encrypted_data: str, associated_data: Optional[str] = None
    ) -> str:
        """Decrypt data that was previously encrypted using the encrypt method."""
        decoded = _decode_encrypted_payload(encrypted_data)
        data_key = await self.decrypt_data_key(keys=decoded.keys)

        key = base64.b64decode(data_key.key)
        aad_buffer = associated_data.encode("utf-8") if associated_data else None

        decrypted_bytes = _aes_gcm_decrypt(
            ciphertext=decoded.ciphertext,
            key=key,
            iv=decoded.iv,
            tag=decoded.tag,
            aad=aad_buffer,
        )
        return decrypted_bytes.decode("utf-8")
