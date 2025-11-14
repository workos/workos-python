from typing import Literal, Optional, Sequence

from workos.types.workos_model import WorkOSModel


class ApiKeyOwner(WorkOSModel):
    type: str
    id: str


class ApiKey(WorkOSModel):
    object: Literal["api_key"]
    id: str
    owner: ApiKeyOwner
    name: str
    obfuscated_value: str
    last_used_at: Optional[str] = None
    permissions: Sequence[str]
    created_at: str
    updated_at: str
