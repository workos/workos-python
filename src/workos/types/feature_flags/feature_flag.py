from typing import Any, Literal, Optional, Sequence
from workos.types.workos_model import WorkOSModel


class FeatureFlag(WorkOSModel):
    id: str
    object: Literal["feature_flag"]
    slug: str
    name: str
    description: Optional[str]
    tags: Sequence[str]
    enabled: bool
    default_value: Optional[Any]
    created_at: str
    updated_at: str
