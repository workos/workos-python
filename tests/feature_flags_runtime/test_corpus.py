# @oagen-ignore-file
"""Runs the JSON fixture corpus (shaped for the shared AUTH-7098 corpus)."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

import pytest

from workos import WorkOSClient
from workos.feature_flags.runtime import (
    FeatureFlagsConfiguration,
    FeatureFlagsConfigurationError,
    FeatureFlagsRuntimeClient,
)
from workos.feature_flags.runtime._configuration import changed_flags
from workos.feature_flags.runtime._context import ContextWarnings, normalize_context

from tests.feature_flags_runtime.helpers import API_KEY, load_fixture

EVALUATION = load_fixture("evaluation_cases.json")
PAYLOADS = load_fixture("payload_cases.json")
CHANGES = load_fixture("change_cases.json")
CONTEXTS = load_fixture("context_cases.json")

_CASE_FIELDS = {"name", "source", "key", "flag", "evaluations", "malformed"}
_EVALUATION_FIELDS = {"context", "expect"}


def _runtime(configuration: FeatureFlagsConfiguration) -> FeatureFlagsRuntimeClient:
    return FeatureFlagsRuntimeClient(
        WorkOSClient(api_key=API_KEY), bootstrap=configuration
    )


def _observed(
    runtime: FeatureFlagsRuntimeClient, slug: str, context: Dict[str, Any]
) -> Any:
    with_false = runtime.is_enabled(slug, context, default=False)
    with_true = runtime.is_enabled(slug, context, default=True)
    if with_false == with_true:
        return with_false
    return "absent" if (with_false, with_true) == (False, True) else "inverted"


@pytest.mark.parametrize("case", EVALUATION["cases"], ids=lambda case: case["name"])
def test_evaluation_corpus(case: Dict[str, Any]) -> None:
    # An unrecognized field is a hard failure, never a silent skip.
    assert set(case) <= _CASE_FIELDS, f"unknown case fields: {set(case) - _CASE_FIELDS}"
    flag = case["flag"]
    key = case.get("key", flag["slug"])
    runtime = _runtime(
        FeatureFlagsConfiguration.from_dict({"version": 2, "flags": {key: flag}})
    )
    for evaluation in case["evaluations"]:
        assert set(evaluation) == _EVALUATION_FIELDS
        assert _observed(runtime, key, evaluation["context"]) == evaluation["expect"], (
            evaluation
        )


def test_get_all_flags_agrees_with_is_enabled_and_omits_flags_without_an_answer() -> (
    None
):
    flags = {
        case.get("key", case["flag"]["slug"]) + str(index): {
            **case["flag"],
            "slug": case.get("key", case["flag"]["slug"]) + str(index),
        }
        for index, case in enumerate(EVALUATION["cases"])
    }
    runtime = _runtime(
        FeatureFlagsConfiguration.from_dict({"version": 2, "flags": flags})
    )
    contexts: List[Dict[str, Any]] = [
        {},
        {"user": "user_1", "organization": "org_1"},
        {"organization": "org_acme"},
    ]
    for context in contexts:
        all_flags = runtime.get_all_flags(context)
        for slug in flags:
            answer = _observed(runtime, slug, context)
            if answer == "absent":
                assert slug not in all_flags
            else:
                assert all_flags[slug] is answer


@pytest.mark.parametrize("case", PAYLOADS["cases"], ids=lambda case: case["name"])
def test_payload_corpus(case: Dict[str, Any]) -> None:
    if case["valid"]:
        FeatureFlagsConfiguration(case["payload"])
    else:
        with pytest.raises(FeatureFlagsConfigurationError):
            FeatureFlagsConfiguration(case["payload"])


@pytest.mark.parametrize("case", CHANGES["cases"], ids=lambda case: case["name"])
def test_change_corpus(case: Dict[str, Any]) -> None:
    before = FeatureFlagsConfiguration(case["before"])
    after = FeatureFlagsConfiguration(case["after"])
    assert sorted(changed_flags(before, after)) == case["changed"]


@pytest.mark.parametrize("case", CONTEXTS["cases"], ids=lambda case: case["name"])
def test_context_corpus(case: Dict[str, Any], caplog: pytest.LogCaptureFixture) -> None:
    logger = logging.getLogger("tests.feature_flags_runtime.context")
    with caplog.at_level(logging.WARNING, logger=logger.name):
        targets = normalize_context(case["context"], ContextWarnings(logger))
    assert targets == case["targets"]
    assert bool(caplog.records) is case["warns"]


def test_context_corpus_flag_matches_only_the_surviving_targets() -> None:
    runtime = _runtime(
        FeatureFlagsConfiguration.from_dict(
            {"version": 2, "flags": {"flag": CONTEXTS["flag"]}}
        )
    )
    for case in CONTEXTS["cases"]:
        expected = (
            case["targets"].get("workspace") == "ws_1"
            or case["targets"].get("user") == "user_1"
        )
        assert runtime.is_enabled("flag", case["context"]) is expected, case["name"]
