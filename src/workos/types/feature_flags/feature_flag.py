from typing import Literal, Optional, Sequence
from workos.types.workos_model import WorkOSModel


class FeatureFlagOwner(WorkOSModel):
    email: str
    first_name: Optional[str]
    last_name: Optional[str]


class FeatureFlag(WorkOSModel):
    id: str
    object: Literal["feature_flag"]
    slug: str
    name: str
    description: Optional[str]
    tags: Sequence[str]
    owner: Optional[FeatureFlagOwner]
    enabled: bool
    default_value: bool
    created_at: str
    updated_at: str
