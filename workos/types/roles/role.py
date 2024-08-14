from typing import Literal, Optional, Sequence
from workos.types.workos_model import WorkOSModel


class Role(WorkOSModel):
    object: Literal["role"]
    slug: str
    permissions: Optional[Sequence[str]] = None
