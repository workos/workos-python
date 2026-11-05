# @oagen-ignore-file
"""FeatureFlagsConfiguration: persistence and flag inspection."""

from __future__ import annotations

import copy
import json
import pickle
from collections import UserDict
from datetime import datetime, timezone
from types import MappingProxyType

import pytest

from workos._errors import AuthenticationError
from workos.feature_flags.runtime import (
    ConditionDefinition,
    FeatureFlagsConfiguration,
    FeatureFlagsConfigurationError,
    FlagDefinition,
    FlagsChangedEvent,
    RuleDefinition,
    RuntimeStatus,
)

from tests.feature_flags_runtime.helpers import flag, payload, rule

PAYLOAD = {
    **payload(
        checkout=flag(
            "checkout",
            default_value=True,
            rules=[
                rule("flag_rule_1", False, "organization", "org_2", "org_1"),
                {
                    "id": "flag_rule_2",
                    "kind": "rollout",
                    "value": "variant-b",
                    "percentage": 10,
                    "conditions": [{"attribute": "plan", "values": ["pro", 3]}],
                },
                {
                    "id": "flag_rule_3",
                    "kind": "conditions",
                    "value": True,
                    "conditions": [
                        {
                            "operator": "segment",
                            "target_type": "user",
                            "values": ["seg"],
                        }
                    ],
                },
            ],
        )
    ),
    "future_top_level": {"anything": [1, 2]},
}


def test_round_trips_through_json_and_dict_with_unknown_fields() -> None:
    configuration = FeatureFlagsConfiguration.from_dict(PAYLOAD)
    restored = FeatureFlagsConfiguration.from_json(configuration.to_json())

    assert configuration.to_dict() == PAYLOAD
    assert restored.to_dict() == PAYLOAD
    assert json.loads(restored.to_json()) == PAYLOAD


def test_owns_a_copy_of_the_payload() -> None:
    source = json.loads(json.dumps(PAYLOAD))
    configuration = FeatureFlagsConfiguration.from_dict(source)
    source["flags"]["checkout"]["enabled"] = False
    exported = configuration.to_dict()
    exported["flags"].clear()

    assert configuration.get_flag("checkout").enabled is True  # type: ignore[union-attr]
    assert len(configuration) == 1


def test_inspects_flags_as_received_including_rules_it_cannot_evaluate() -> None:
    configuration = FeatureFlagsConfiguration.from_dict(PAYLOAD)

    assert configuration.get_flag("checkout") == FlagDefinition(
        slug="checkout",
        enabled=True,
        default_value=True,
        off_value=False,
        rules=(
            RuleDefinition(
                id="flag_rule_1",
                kind="conditions",
                value=False,
                conditions=(
                    ConditionDefinition("organization", "one_of", ("org_2", "org_1")),
                ),
            ),
            RuleDefinition(
                id="flag_rule_2",
                kind="rollout",
                value=None,
                conditions=(ConditionDefinition(None, None, ("pro",)),),
            ),
            RuleDefinition(
                id="flag_rule_3",
                kind="conditions",
                value=True,
                conditions=(ConditionDefinition("user", "segment", ("seg",)),),
            ),
        ),
    )
    assert configuration.get_flag("missing") is None
    assert configuration.slugs == ("checkout",)
    assert "checkout" in configuration and 1 not in configuration
    assert list(configuration) == ["checkout"]


def test_invalid_json_is_a_configuration_error() -> None:
    with pytest.raises(FeatureFlagsConfigurationError, match="not valid JSON"):
        FeatureFlagsConfiguration.from_json("{not json")
    with pytest.raises(FeatureFlagsConfigurationError, match="(?i)expected an object"):
        FeatureFlagsConfiguration.from_json("[]")


def test_configuration_errors_are_value_errors() -> None:
    with pytest.raises(ValueError):
        FeatureFlagsConfiguration.from_dict({"version": 1, "flags": {}})


def test_values_that_are_not_json_are_rejected() -> None:
    with pytest.raises(FeatureFlagsConfigurationError, match="JSON-serializable"):
        FeatureFlagsConfiguration.from_dict(
            {"version": 2, "flags": {}, "when": object()}
        )


def test_accepts_any_mapping_type() -> None:
    read_only = MappingProxyType({**PAYLOAD, "flags": UserDict(PAYLOAD["flags"])})
    configuration = FeatureFlagsConfiguration.from_dict(read_only)

    assert configuration.to_dict() == PAYLOAD
    assert configuration.get_flag("checkout") is not None


def test_snapshots_pickle_and_copy() -> None:
    configuration = FeatureFlagsConfiguration.from_dict(PAYLOAD)

    restored = pickle.loads(pickle.dumps(configuration))
    assert restored is not configuration
    assert restored.to_json() == configuration.to_json()
    assert restored.get_flag("checkout") == configuration.get_flag("checkout")
    # Immutable, so copies can share the instance.
    assert copy.copy(configuration) is configuration
    assert copy.deepcopy(configuration) is configuration


def test_status_and_change_events_pickle_and_copy() -> None:
    configuration = FeatureFlagsConfiguration.from_dict(PAYLOAD)
    error = AuthenticationError(
        "Invalid API key", request_id="req_1", response_json={"message": "x"}
    )
    status = RuntimeStatus(
        configuration=configuration,
        last_successful_refresh_at=datetime(2026, 11, 2, tzinfo=timezone.utc),
        last_error=error,
        refresh_count=3,
        failed_refresh_count=1,
    )
    event = FlagsChangedEvent(None, configuration, frozenset({"checkout"}))

    for clone in (pickle.loads(pickle.dumps(status)), copy.deepcopy(status)):
        assert clone.refresh_count == 3
        assert clone.flag_count == 1
        assert clone.configuration is not None
        assert clone.configuration.to_json() == configuration.to_json()
        assert isinstance(clone.last_error, AuthenticationError)
        assert clone.last_error.request_id == "req_1"
    for clone_event in (pickle.loads(pickle.dumps(event)), copy.deepcopy(event)):
        assert clone_event.changed_flags == {"checkout"}
        assert clone_event.current.slugs == ("checkout",)
