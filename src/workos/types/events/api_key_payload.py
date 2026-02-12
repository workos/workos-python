from typing import Literal, Optional, Sequence
from workos.types.workos_model import WorkOSModel


class ApiKeyOwner(WorkOSModel):
    id: str
    type: str


class ApiKeyPayload(WorkOSModel):
    object: Literal["api_key"]
    id: str
    name: str
    owner: ApiKeyOwner
    obfuscated_value: str
    permissions: Sequence[str]
    last_used_at: Optional[str] = None
    created_at: str
    updated_at: str
