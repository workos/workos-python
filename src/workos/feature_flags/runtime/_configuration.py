# @oagen-ignore-file
# This file is hand-maintained. It parses the feature flags runtime payload
# (`GET /sdk/feature-flags?payload_version=2`), which is not part of the
# OpenAPI spec.
# pyright: strict, reportPrivateUsage=false

from __future__ import annotations

import json
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Iterator, Mapping, Sequence, TypeGuard, cast

from ..._errors import WorkOSError

PAYLOAD_VERSION = 2

_CONDITIONS_KIND = "conditions"
_ONE_OF_OPERATOR = "one_of"


class FeatureFlagsConfigurationError(WorkOSError, ValueError):
    """A feature flags payload that this SDK cannot read.

    Raised by :meth:`FeatureFlagsConfiguration.from_dict` and
    :meth:`FeatureFlagsConfiguration.from_json`. When a background poll returns
    such a payload, the runtime client keeps its last good configuration and
    reports this error instead.
    """


@dataclass(frozen=True, slots=True)
class ConditionDefinition:
    """One condition of a rule, as received.

    The SDK evaluates only the ``one_of`` operator. A rule containing any other
    operator never matches. ``target_type`` and ``operator`` are ``None`` only
    when a condition the SDK does not evaluate omits them.
    """

    target_type: str | None
    operator: str | None
    values: tuple[str, ...]
    """Exact, case-sensitive IDs in the order received."""


@dataclass(frozen=True, slots=True)
class RuleDefinition:
    """One rule of a flag, as received.

    The SDK evaluates only ``conditions`` rules. A rule of any other kind, such
    as one added by a newer server, never matches.
    """

    id: str
    kind: str
    value: bool | None
    """Served when the rule matches. ``None`` when the served value is not a boolean."""
    conditions: tuple[ConditionDefinition, ...]
    """Conditions that must all match. Best effort for kinds the SDK does not evaluate."""


@dataclass(frozen=True, slots=True)
class FlagDefinition:
    """One flag's configuration as the runtime client received it.

    For inspection and debugging only. Use the runtime client's ``is_enabled``
    for decisions.
    """

    slug: str
    enabled: bool
    """Whether the flag is on in this environment."""
    default_value: bool | None
    """Served when the flag is on and no rule matches. ``None`` when not a boolean."""
    off_value: bool | None
    """Served when the flag is off. ``None`` when not a boolean."""
    rules: tuple[RuleDefinition, ...]
    """Rules in evaluation order. The first matching rule wins."""


@dataclass(frozen=True, slots=True)
class _CompiledCondition:
    target_type: str
    ids: frozenset[str]


@dataclass(frozen=True, slots=True)
class _CompiledRule:
    # Empty when the rule can never match: an unknown kind, an unknown
    # operator, a condition without a target type, or no conditions at all.
    conditions: tuple[_CompiledCondition, ...]
    value: bool | None


@dataclass(frozen=True, slots=True)
class _CompiledFlag:
    definition: FlagDefinition
    rules: tuple[_CompiledRule, ...]
    canonical: str

    def evaluate(self, targets: Mapping[str, str]) -> bool | None:
        """Return the served boolean, or ``None`` when the flag has no answer."""
        definition = self.definition
        if not definition.enabled:
            return definition.off_value
        for rule in self.rules:
            if rule.conditions and all(
                targets.get(condition.target_type) in condition.ids
                for condition in rule.conditions
            ):
                return rule.value
        return definition.default_value


_NEVER_MATCHES = _CompiledRule(conditions=(), value=None)


class FeatureFlagsConfiguration:
    """An immutable, validated snapshot of an environment's feature flags.

    Persist :meth:`to_json` in your own storage and pass
    ``FeatureFlagsConfiguration.from_json(cached)`` as ``bootstrap`` to make a
    new runtime client usable before its first successful poll.
    """

    __slots__ = ("_json", "_fingerprint", "_flags")

    _json: str
    # The payload serialized with sorted keys: equal for equal content, so an
    # unchanged poll can keep this snapshot without parsing it again.
    _fingerprint: str
    _flags: Mapping[str, _CompiledFlag]

    def __init__(self, payload: Mapping[str, Any]) -> None:
        """Validate a complete version 2 payload.

        Raises:
            FeatureFlagsConfigurationError: If the payload is malformed or uses
                another payload version. Unknown rule kinds and operators are
                accepted and never match, and a served value that is not a
                boolean leaves the flag without an answer.
        """
        self._initialize(payload, _fingerprint(payload))

    def _initialize(self, payload: object, fingerprint: str) -> None:
        self._json = _dumps(payload, sort_keys=False)
        self._fingerprint = fingerprint
        self._flags = MappingProxyType(_parse_payload(json.loads(self._json)))

    def __reduce__(self) -> tuple[Any, ...]:
        # MappingProxyType cannot be pickled; the JSON rebuilds an equal snapshot.
        return (_restore, (self._json,))

    def __copy__(self) -> FeatureFlagsConfiguration:
        return self

    def __deepcopy__(self, memo: dict[int, Any]) -> FeatureFlagsConfiguration:
        return self

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> FeatureFlagsConfiguration:
        """Validate a decoded version 2 payload, e.g. one you cached with :meth:`to_dict`."""
        return cls(data)

    @classmethod
    def from_json(cls, text: str | bytes) -> FeatureFlagsConfiguration:
        """Validate a version 2 payload serialized as JSON, e.g. one you cached with :meth:`to_json`."""
        try:
            data: object = json.loads(text)
        except ValueError as error:
            raise FeatureFlagsConfigurationError(
                f"Feature flags configuration is not valid JSON: {error}"
            ) from error
        if not _is_mapping(data):
            raise FeatureFlagsConfigurationError(
                "Expected an object for the feature flags configuration."
            )
        return cls(data)

    def to_dict(self) -> dict[str, Any]:
        """Return a copy of the complete payload, including fields this SDK ignores."""
        return cast(dict[str, Any], json.loads(self._json))

    def to_json(self) -> str:
        """Return the complete payload as JSON, including fields this SDK ignores."""
        return self._json

    def get_flag(self, slug: str) -> FlagDefinition | None:
        """Return one flag's configuration, or ``None`` if the snapshot does not contain it."""
        flag = self._compiled(slug)
        return flag.definition if flag is not None else None

    @property
    def slugs(self) -> tuple[str, ...]:
        """Every flag slug in this snapshot, in payload order."""
        return tuple(self._flags)

    def __len__(self) -> int:
        return len(self._flags)

    def __contains__(self, slug: object) -> bool:
        return isinstance(slug, str) and slug in self._flags

    def __iter__(self) -> Iterator[str]:
        return iter(self._flags)

    def __repr__(self) -> str:
        return f"FeatureFlagsConfiguration(flags={len(self._flags)})"

    def _compiled(self, slug: object) -> _CompiledFlag | None:
        return self._flags.get(slug) if _is_string(slug) else None

    def _compiled_items(self) -> Iterator[tuple[str, _CompiledFlag]]:
        return iter(self._flags.items())


def configuration_for(
    payload: object, current: FeatureFlagsConfiguration | None
) -> FeatureFlagsConfiguration:
    """``current`` when ``payload`` has the same content, otherwise a new snapshot.

    Most polls return an unchanged configuration; reusing the snapshot skips
    validating it again. Key order does not count as a change.
    """
    fingerprint = _fingerprint(payload)
    if current is not None and current._fingerprint == fingerprint:
        return current
    configuration = FeatureFlagsConfiguration.__new__(FeatureFlagsConfiguration)
    configuration._initialize(payload, fingerprint)
    return configuration


def changed_flags(
    previous: FeatureFlagsConfiguration | None, current: FeatureFlagsConfiguration
) -> frozenset[str]:
    """Slugs added, removed or modified between two snapshots.

    Every slug counts as changed on a first load. A flag's complete content is
    compared, including fields this SDK does not interpret, so a cache kept
    fresh from change notifications never misses a newer server's fields.
    """
    if previous is None:
        return frozenset(current.slugs)
    if previous is current:
        return frozenset()
    changed = {
        slug
        for slug, flag in current._compiled_items()
        if (before := previous._compiled(slug)) is None
        or before.canonical != flag.canonical
    }
    changed.update(slug for slug in previous.slugs if slug not in current)
    return frozenset(changed)


def _restore(text: str) -> FeatureFlagsConfiguration:
    return FeatureFlagsConfiguration.from_json(text)


# --- Parsing ------------------------------------------------------------------


def _dumps(payload: object, *, sort_keys: bool) -> str:
    try:
        return json.dumps(
            payload,
            sort_keys=sort_keys,
            ensure_ascii=False,
            separators=(",", ":"),
            default=_mapping_as_dict,
        )
    except (TypeError, ValueError) as error:
        raise FeatureFlagsConfigurationError(
            f"Feature flags configuration is not JSON-serializable: {error}"
        ) from error


def _mapping_as_dict(value: object) -> object:
    # json only serializes dicts, but the payload may be any mapping, such as a
    # read-only MappingProxyType of a cached configuration.
    if isinstance(value, Mapping):
        return dict(cast(Mapping[object, object], value))
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def _fingerprint(payload: object) -> str:
    return _dumps(payload, sort_keys=True)


def _invalid(message: str) -> FeatureFlagsConfigurationError:
    return FeatureFlagsConfigurationError(
        f"Invalid feature flags configuration: {message}"
    )


def _is_mapping(value: object) -> TypeGuard[Mapping[str, Any]]:
    return isinstance(value, Mapping)


def _is_list(value: object) -> TypeGuard[list[Any]]:
    return isinstance(value, list)


def _is_string(value: object) -> TypeGuard[str]:
    return isinstance(value, str)


def _is_nonempty_string(value: object) -> TypeGuard[str]:
    return isinstance(value, str) and value != ""


def _served_value(value: object) -> bool | None:
    # Mirrors the server: a served value that is not a boolean, such as a
    # future multivariate variant, means "no answer" rather than false, so the
    # caller's own default applies.
    return value if isinstance(value, bool) else None


def _parse_payload(payload: object) -> dict[str, _CompiledFlag]:
    if not _is_mapping(payload):
        raise _invalid("expected an object.")
    version = payload.get("version")
    # `bool` is a subclass of `int`, and `2.0 == 2`, so compare the exact type.
    if type(version) is not int or version != PAYLOAD_VERSION:
        raise _invalid(f"expected SDK payload version {PAYLOAD_VERSION}.")
    flags = payload.get("flags")
    if not _is_mapping(flags):
        raise _invalid("expected an object for flags.")
    return {slug: _parse_flag(slug, entry) for slug, entry in flags.items()}


def _parse_flag(slug: str, entry: object) -> _CompiledFlag:
    if not _is_mapping(entry):
        raise _invalid(f"expected an object for flag {slug!r}.")
    # The map key is the flag's identity. A `slug` that differs from it is
    # tolerated, as the Node SDK does, rather than failing the whole refresh.
    if not isinstance(entry.get("slug"), str):
        raise _invalid(f"expected a string slug for flag {slug!r}.")
    enabled = entry.get("enabled")
    if not isinstance(enabled, bool):
        raise _invalid(f"expected a boolean for {slug!r}.enabled.")
    raw_rules = entry.get("rules")
    if not _is_list(raw_rules):
        raise _invalid(f"expected an array for {slug!r}.rules.")
    parsed = [_parse_rule(slug, rule) for rule in raw_rules]
    definition = FlagDefinition(
        slug=slug,
        enabled=enabled,
        default_value=_served_value(entry.get("default_value")),
        off_value=_served_value(entry.get("off_value")),
        rules=tuple(definition for definition, _ in parsed),
    )
    return _CompiledFlag(
        definition=definition,
        rules=tuple(compiled for _, compiled in parsed),
        canonical=_canonical_flag(entry),
    )


def _parse_rule(slug: str, rule: object) -> tuple[RuleDefinition, _CompiledRule]:
    if not _is_mapping(rule):
        raise _invalid(f"expected an object for a rule of {slug!r}.")
    rule_id = rule.get("id")
    kind = rule.get("kind")
    if not _is_nonempty_string(rule_id) or not _is_nonempty_string(kind):
        raise _invalid(f"expected a nonempty id and kind for every rule of {slug!r}.")
    value = _served_value(rule.get("value"))
    if kind != _CONDITIONS_KIND:
        # A future rule kind may have entirely different fields. Record what is
        # recognizable for inspection but never validate or evaluate it, so a
        # newer server can never fail this SDK's refresh.
        return (
            RuleDefinition(
                rule_id, kind, value, _inspect_conditions(rule.get("conditions"))
            ),
            _NEVER_MATCHES,
        )
    raw_conditions = rule.get("conditions")
    if raw_conditions is None:
        return RuleDefinition(rule_id, kind, value, ()), _NEVER_MATCHES
    if not _is_list(raw_conditions):
        raise _invalid(f"expected an array of conditions for rule {rule_id!r}.")
    parsed = [_parse_condition(rule_id, condition) for condition in raw_conditions]
    definitions = tuple(definition for definition, _ in parsed)
    compiled = tuple(condition for _, condition in parsed if condition is not None)
    evaluable = bool(parsed) and len(compiled) == len(parsed)
    return (
        RuleDefinition(rule_id, kind, value, definitions),
        _CompiledRule(compiled, value) if evaluable else _NEVER_MATCHES,
    )


def _parse_condition(
    rule_id: str, condition: object
) -> tuple[ConditionDefinition, _CompiledCondition | None]:
    if not _is_mapping(condition):
        raise _invalid(f"expected an object for a condition of rule {rule_id!r}.")
    operator = condition.get("operator")
    if not isinstance(operator, str):
        raise _invalid(f"expected a string operator in rule {rule_id!r}.")
    if operator != _ONE_OF_OPERATOR:
        # Future operators may carry different operands. They are recorded for
        # inspection but never validated, and the rule containing them never
        # matches.
        return _inspect_condition(condition), None
    target_type = condition.get("target_type")
    if target_type is not None and not isinstance(target_type, str):
        raise _invalid(f"expected a string target_type in rule {rule_id!r}.")
    raw_values = condition.get("values")
    if not _is_list(raw_values):
        raise _invalid(
            f"expected an array of values for a one_of condition in rule {rule_id!r}."
        )
    values = _string_values(raw_values)
    definition = ConditionDefinition(target_type, operator, values)
    if target_type is None:
        return definition, None
    # IDs that are not strings can never equal a context ID, so they are
    # dropped rather than failing the whole refresh.
    return definition, _CompiledCondition(target_type, frozenset(values))


def _inspect_conditions(raw: object) -> tuple[ConditionDefinition, ...]:
    if not _is_list(raw):
        return ()
    return tuple(
        _inspect_condition(condition) for condition in raw if _is_mapping(condition)
    )


def _inspect_condition(condition: Mapping[str, Any]) -> ConditionDefinition:
    target_type = condition.get("target_type")
    operator = condition.get("operator")
    return ConditionDefinition(
        target_type if isinstance(target_type, str) else None,
        operator if isinstance(operator, str) else None,
        _string_values(condition.get("values")),
    )


def _string_values(raw: object) -> tuple[str, ...]:
    if not _is_list(raw):
        return ()
    return tuple(value for value in raw if isinstance(value, str))


# --- Change detection ---------------------------------------------------------


def _canonical_flag(entry: Mapping[str, Any]) -> str:
    # Property order never matters. Rule order does (first match wins), but
    # the conditions of a `conditions` rule must all match, so their order does
    # not, and the IDs of a `one_of` condition form a set. Every other array
    # stays order-sensitive: a spurious change only costs a redundant
    # notification, but a missed one leaves a cache stale.
    canonical = dict(entry)
    rules = canonical.get("rules")
    if _is_list(rules):
        canonical["rules"] = [_canonical_rule(rule) for rule in rules]
    return json.dumps(
        canonical, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    )


def _canonical_rule(rule: object) -> object:
    if not _is_mapping(rule) or rule.get("kind") != _CONDITIONS_KIND:
        return rule
    conditions = rule.get("conditions")
    if not _is_list(conditions):
        return rule
    ordered = sorted(
        (_canonical_condition(condition) for condition in conditions),
        key=lambda condition: json.dumps(condition, sort_keys=True, ensure_ascii=False),
    )
    return {**rule, "conditions": ordered}


def _canonical_condition(condition: object) -> object:
    if not _is_mapping(condition) or condition.get("operator") != _ONE_OF_OPERATOR:
        return condition
    values = condition.get("values")
    if not _is_list(values) or not all(isinstance(value, str) for value in values):
        return condition
    return {**condition, "values": sorted(set(cast(Sequence[str], values)))}
