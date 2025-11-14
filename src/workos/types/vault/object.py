from typing import Optional

from workos.types.workos_model import WorkOSModel
from workos.types.vault import KeyContext


class ObjectDigest(WorkOSModel):
    id: str
    name: str
    updated_at: str


class ObjectUpdateBy(WorkOSModel):
    id: str
    name: str


class ObjectMetadata(WorkOSModel):
    context: KeyContext
    environment_id: str
    id: str
    key_id: str
    updated_at: str
    updated_by: ObjectUpdateBy
    version_id: str


class VaultObject(WorkOSModel):
    id: str
    metadata: ObjectMetadata
    name: str
    value: Optional[str] = None


class ObjectVersion(WorkOSModel):
    created_at: str
    current_version: bool
    id: str
