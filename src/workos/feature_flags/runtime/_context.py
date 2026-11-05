# @oagen-ignore-file
# This file is hand-maintained. It validates the evaluation context passed to
# the feature flags runtime client.
# pyright: strict

from __future__ import annotations

import logging
import re
import threading
from typing import Mapping, Optional, Union, cast

EvaluationContext = Mapping[str, Optional[str]]
"""Maps a target type to the exact ID being evaluated.

For example ``{"user": "user_123", "organization": "org_123", "workspace": "ws_1"}``.
``user`` and ``organization`` are target types like any custom type. Entries
whose ID is ``None`` are skipped, so optional IDs can be passed directly.
"""

LoggerLike = Union[logging.Logger, "logging.LoggerAdapter[logging.Logger]"]

# Mirrors the API's validation rules for target types and IDs. `fullmatch` is
# required: `$` in `re.match` also matches before a trailing newline.
_TARGET_TYPE = re.compile(r"[a-z][a-z0-9_-]{0,63}")
_TARGET_ID = re.compile(r"[A-Za-z0-9._:-]{1,255}")
_RESERVED_IDS = frozenset({".", ".."})

# Spellings from other SDKs or Python habit that name a built-in target type.
_BUILT_IN_HINTS = {
    "userId": "user",
    "user_id": "user",
    "organizationId": "organization",
    "organization_id": "organization",
}

_MAX_DISTINCT_WARNINGS = 100


class ContextWarnings:
    """Logs each distinct context problem once per runtime client.

    Evaluation runs on hot paths, so a recurring mistake must not log on every
    call. The number of remembered problems is bounded.
    """

    def __init__(self, logger: LoggerLike) -> None:
        self._logger = logger
        self._seen: set[tuple[str, str]] = set()
        self._lock = threading.Lock()
        self._saturated = False

    def warn(self, reason: str, key: str, message: str) -> None:
        with self._lock:
            if (reason, key) in self._seen:
                return
            if len(self._seen) >= _MAX_DISTINCT_WARNINGS:
                if self._saturated:
                    return
                self._saturated = True
                message = (
                    "Too many distinct evaluation context problems; "
                    "further ones are not logged"
                )
            else:
                self._seen.add((reason, key))
        self._logger.warning(message)

    def reinitialize_after_fork(self) -> None:
        self._lock = threading.Lock()


def normalize_context(context: object, warnings: ContextWarnings) -> dict[str, str]:
    """Reduce an evaluation context to valid target type to ID pairs.

    Evaluation must never raise in application code, so every invalid piece of
    context is ignored with a logged warning and the rest is still evaluated.
    """
    if context is None:
        return {}
    if not isinstance(context, Mapping):
        warnings.warn(
            "context",
            type(context).__name__,
            "Ignoring invalid evaluation context: expected a mapping of target type to ID, "
            f"got {type(context).__name__}",
        )
        return {}
    targets: dict[str, str] = {}
    for key, value in cast(Mapping[object, object], context).items():
        if value is None:
            continue
        target_type = _valid_target_type(key, warnings)
        if target_type is not None and _is_valid_id(target_type, value, warnings):
            targets[target_type] = cast(str, value)
    return targets


def _valid_target_type(key: object, warnings: ContextWarnings) -> str | None:
    if not isinstance(key, str) or _TARGET_TYPE.fullmatch(key) is None:
        label = key if isinstance(key, str) else type(key).__name__
        hint = _BUILT_IN_HINTS.get(label)
        suffix = f"; use {hint!r}" if hint else ""
        warnings.warn(
            "type",
            label,
            f"Ignoring invalid target type in evaluation context: {label!r}{suffix}",
        )
        return None
    hint = _BUILT_IN_HINTS.get(key)
    if hint is not None:
        warnings.warn(
            "hint",
            key,
            f"Evaluation context key {key!r} is treated as a custom target type; "
            f"use {hint!r} to match {hint} targets",
        )
    return key


def _is_valid_id(target_type: str, value: object, warnings: ContextWarnings) -> bool:
    if isinstance(value, str):
        if _TARGET_ID.fullmatch(value) is not None and value not in _RESERVED_IDS:
            return True
        warnings.warn(
            "id",
            target_type,
            f"Ignoring invalid target id in evaluation context for type: {target_type!r}",
        )
        return False
    warnings.warn(
        "id-type",
        target_type,
        f"Ignoring target type {target_type!r} in evaluation context: expected a string ID, "
        f"got {type(value).__name__}",
    )
    return False
