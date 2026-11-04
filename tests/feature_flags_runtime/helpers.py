# @oagen-ignore-file
"""Helpers for the feature flags runtime client tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> Dict[str, Any]:
    return json.loads((FIXTURES / name).read_text())


def payload(**flags: Dict[str, Any]) -> Dict[str, Any]:
    return {"version": 2, "flags": flags}


def flag(
    slug: str = "flag",
    *,
    enabled: bool = True,
    default_value: Any = False,
    off_value: Any = False,
    rules: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    return {
        "slug": slug,
        "enabled": enabled,
        "default_value": default_value,
        "off_value": off_value,
        "rules": rules or [],
    }


def rule(
    rule_id: str, value: Any, target_type: str, *ids: str, kind: str = "conditions"
) -> Dict[str, Any]:
    return {
        "id": rule_id,
        "kind": kind,
        "value": value,
        "conditions": [
            {"target_type": target_type, "operator": "one_of", "values": list(ids)}
        ],
    }
