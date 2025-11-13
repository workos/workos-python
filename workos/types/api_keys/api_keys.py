from typing import Literal

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
    last_used_at: str | None = None
    permissions: list[str]
    created_at: str
    updated_at: str
