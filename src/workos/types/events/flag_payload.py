from typing import Literal, Optional, Sequence

from workos.types.workos_model import WorkOSModel


class FlagPayload(WorkOSModel):
    object: Literal["flag"]
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    tags: Optional[Sequence[str]] = None
    created_at: str
    updated_at: str
