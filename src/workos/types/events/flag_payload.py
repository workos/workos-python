from typing import Literal, Optional, Sequence

from workos.types.workos_model import WorkOSModel


class FlagOwner(WorkOSModel):
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class FlagPayload(WorkOSModel):
    object: Literal["feature_flag"]
    id: str
    environment_id: str
    slug: str
    name: str
    description: Optional[str] = None
    owner: Optional[FlagOwner] = None
    tags: Sequence[str]
    enabled: bool
    default_value: bool
    created_at: str
    updated_at: str
