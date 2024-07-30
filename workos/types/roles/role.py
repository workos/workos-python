from typing import List, Literal, Optional
from workos.resources.workos_model import WorkOSModel


class Role(WorkOSModel):
    object: Literal["role"]
    slug: str
    permissions: Optional[List[str]] = None
