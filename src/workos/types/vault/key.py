from typing import Dict
from pydantic import BaseModel, RootModel
from workos.types.workos_model import WorkOSModel


class KeyContext(RootModel[Dict[str, str]]):
    pass


class DataKey(WorkOSModel):
    id: str
    key: str


class DataKeyPair(WorkOSModel):
    context: KeyContext
    data_key: DataKey
    encrypted_keys: str


class DecodedKeys(BaseModel):
    iv: bytes
    tag: bytes
    keys: str  # Base64-encoded string
    ciphertext: bytes
