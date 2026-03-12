from typing import List, Optional

from workos.types.vault.key import KeyContext
from workos.types.workos_model import WorkOSModel


class VaultNamesListedPayload(WorkOSModel):
    actor_id: str
    actor_source: str
    actor_name: Optional[str] = None


class VaultDataDeletedPayload(WorkOSModel):
    actor_id: str
    actor_source: str
    actor_name: Optional[str] = None
    kv_name: str


class VaultDekDecryptedPayload(WorkOSModel):
    actor_id: str
    actor_source: str
    actor_name: Optional[str] = None
    key_id: str


class VaultDataReadPayload(WorkOSModel):
    actor_id: str
    actor_source: str
    actor_name: Optional[str] = None
    kv_name: str
    key_id: str


class VaultDataCreatedPayload(WorkOSModel):
    actor_id: str
    actor_source: str
    actor_name: Optional[str] = None
    kv_name: str
    key_id: str
    key_context: KeyContext


class VaultDekReadPayload(WorkOSModel):
    actor_id: str
    actor_source: str
    actor_name: Optional[str] = None
    key_ids: List[str]
    key_context: KeyContext


class VaultKekCreatedPayload(WorkOSModel):
    actor_id: str
    actor_source: str
    actor_name: Optional[str] = None
    key_name: str
    key_id: str
