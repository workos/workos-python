# @oagen-ignore-file
"""Runs the JSON fixture corpus (shaped for the shared AUTH-7098 corpus)."""

from __future__ import annotations

import logging
from typing import Any, Dict

import pytest

from workos.feature_flags.runtime._configuration import (
    FeatureFlagsConfiguration,
    FeatureFlagsConfigurationError,
    changed_flags,
)
from workos.feature_flags.runtime._context import ContextWarnings, normalize_context

from tests.feature_flags_runtime.helpers import load_fixture

EVALUATION = load_fixture("evaluation_cases.json")
PAYLOADS = load_fixture("payload_cases.json")
CHANGES = load_fixture("change_cases.json")
CONTEXTS = load_fixture("context_cases.json")

_CASE_FIELDS = {"name", "source", "key", "flag", "evaluations", "malformed"}
_EVALUATION_FIELDS = {"context", "expect"}
_OPTIONAL_EVALUATION_FIELDS = {"name"}
_CHANGE_FIELDS = {"name", "source", "before", "after", "changed"}
_WARNINGS = ContextWarnings(logging.getLogger("tests.feature_flags_runtime.corpus"))


def _is_enabled(
    configuration: FeatureFlagsConfiguration,
    slug: str,
    context: Dict[str, Any],
    *,
    default: bool,
) -> bool:
    # `default` answers for a missing flag and for one without a boolean answer.
    flag = configuration._compiled(slug)
    if flag is None:
        return default
    answer = flag.evaluate(normalize_context(context, _WARNINGS))
    return default if answer is None else answer


def _observed(
    configuration: FeatureFlagsConfiguration, slug: str, context: Dict[str, Any]
) -> Any:
    with_false = _is_enabled(configuration, slug, context, default=False)
    with_true = _is_enabled(configuration, slug, context, default=True)
    if with_false == with_true:
        return with_false
    return "absent" if (with_false, with_true) == (False, True) else "inverted"


@pytest.mark.parametrize("case", EVALUATION["cases"], ids=lambda case: case["name"])
def test_evaluation_corpus(case: Dict[str, Any]) -> None:
    # An unrecognized field is a hard failure, never a silent skip.
    assert set(case) <= _CASE_FIELDS, f"unknown case fields: {set(case) - _CASE_FIELDS}"
    flag = case["flag"]
    key = case.get("key", flag["slug"])
    configuration = FeatureFlagsConfiguration.from_dict(
        {"version": 2, "flags": {key: flag}}
    )
    for evaluation in case["evaluations"]:
        fields = set(evaluation)
        assert (
            _EVALUATION_FIELDS
            <= fields
            <= _EVALUATION_FIELDS | _OPTIONAL_EVALUATION_FIELDS
        ), f"unexpected evaluation fields: {fields}"
        observed = _observed(configuration, key, evaluation["context"])
        assert observed == evaluation["expect"], evaluation


@pytest.mark.parametrize("case", PAYLOADS["cases"], ids=lambda case: case["name"])
def test_payload_corpus(case: Dict[str, Any]) -> None:
    if case["valid"]:
        FeatureFlagsConfiguration(case["payload"])
    else:
        with pytest.raises(FeatureFlagsConfigurationError):
            FeatureFlagsConfiguration(case["payload"])


@pytest.mark.parametrize("case", CHANGES["cases"], ids=lambda case: case["name"])
def test_change_corpus(case: Dict[str, Any]) -> None:
    assert set(case) <= _CHANGE_FIELDS, (
        f"unknown case fields: {set(case) - _CHANGE_FIELDS}"
    )
    before = FeatureFlagsConfiguration(case.get("before", CHANGES["baseline"]))
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
    configuration = FeatureFlagsConfiguration.from_dict(
        {"version": 2, "flags": {"flag": CONTEXTS["flag"]}}
    )
    for case in CONTEXTS["cases"]:
        expected = (
            case["targets"].get("workspace") == "ws_1"
            or case["targets"].get("user") == "user_1"
        )
        observed = _is_enabled(configuration, "flag", case["context"], default=False)
        assert observed is expected, case["name"]
