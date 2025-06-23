from typing import Dict
from pydantic import RootModel
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
