from typing import Literal, Optional, Sequence

from workos.types.workos_model import WorkOSModel

AccessType = Literal["none", "some", "all"]


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


class FlagRuleActor(WorkOSModel):
    id: str
    source: Literal["api", "dashboard", "system"]
    name: Optional[str] = None


class FlagRuleOrganizationTarget(WorkOSModel):
    id: str
    name: str


class FlagRuleUserTarget(WorkOSModel):
    id: str
    email: str


class FlagRuleConfiguredTargets(WorkOSModel):
    organizations: Sequence[FlagRuleOrganizationTarget]
    users: Sequence[FlagRuleUserTarget]


class FlagRulePreviousDataAttributes(WorkOSModel):
    enabled: Optional[bool] = None
    default_value: Optional[bool] = None


class FlagRulePreviousContextAttributes(WorkOSModel):
    access_type: Optional[AccessType] = None
    configured_targets: Optional[FlagRuleConfiguredTargets] = None


class FlagRulePreviousAttributes(WorkOSModel):
    data: Optional[FlagRulePreviousDataAttributes] = None
    context: Optional[FlagRulePreviousContextAttributes] = None


class FlagRuleUpdatedContext(WorkOSModel):
    client_id: str
    actor: FlagRuleActor
    access_type: AccessType
    configured_targets: FlagRuleConfiguredTargets
    previous_attributes: FlagRulePreviousAttributes
