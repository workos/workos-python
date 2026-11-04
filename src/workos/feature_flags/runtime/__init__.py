# @oagen-ignore-file
# This file is hand-maintained. The feature flags runtime client evaluates
# flags locally from a polled configuration; it is not part of the OpenAPI spec.

"""Local evaluation of WorkOS feature flags from a polled configuration.

Use :class:`FeatureFlagsRuntimeClient` with :class:`workos.WorkOSClient` and
:class:`AsyncFeatureFlagsRuntimeClient` with :class:`workos.AsyncWorkOSClient`.
"""

from ._async import AsyncFeatureFlagsRuntimeClient
from ._configuration import (
    ConditionDefinition,
    FeatureFlagsConfiguration,
    FeatureFlagsConfigurationError,
    FlagDefinition,
    RuleDefinition,
)
from ._context import EvaluationContext
from ._sync import FeatureFlagsRuntimeClient
from ._types import FlagsChangedEvent, RuntimeStatus

__all__ = [
    "AsyncFeatureFlagsRuntimeClient",
    "ConditionDefinition",
    "EvaluationContext",
    "FeatureFlagsConfiguration",
    "FeatureFlagsConfigurationError",
    "FeatureFlagsRuntimeClient",
    "FlagDefinition",
    "FlagsChangedEvent",
    "RuleDefinition",
    "RuntimeStatus",
]
