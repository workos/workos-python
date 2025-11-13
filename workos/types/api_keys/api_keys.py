from typing import Literal

from workos.types.workos_model import WorkOSModel


class ApiKey(WorkOSModel):
    object: Literal["api_key"]
    id: str
    name: str
    last_used_at: str | None = None
    created_at: str
    updated_at: str
