from typing import Literal, Optional
from workos.types.workos_model import WorkOSModel


class FeatureFlag(WorkOSModel):
    id: str
    object: Literal["feature_flag"]
    slug: str
    name: str
    description: Optional[str]
    created_at: str
    updated_at: str
