# @oagen-ignore-file

from __future__ import annotations

import sys
from datetime import datetime
from enum import Enum
from typing import Any, Dict, NoReturn, Protocol, TypeVar
from typing_extensions import Self, TypedDict


class RequestOptions(TypedDict, total=False):
    """Per-request options that can be passed to any API method."""

    extra_headers: Dict[str, str]
    timeout: float
    idempotency_key: str
    max_retries: int
    base_url: str


class Deserializable(Protocol):
    """Protocol for types that can be deserialized from a dict."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Self: ...


def enum_value(value: Any) -> Any:
    """Serialize enum-like values without rejecting raw string inputs."""
    return value.value if isinstance(value, Enum) else value


D = TypeVar("D", bound=Deserializable)


def _parse_datetime(value: str) -> datetime:
    """Parse an ISO 8601 datetime string, handling 'Z' suffix.

    On Python 3.11+ fromisoformat handles 'Z' natively;
    on older versions we replace 'Z' with '+00:00'.
    """
    if sys.version_info >= (3, 11):
        return datetime.fromisoformat(value)
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _raise_deserialize_error(cls_name: str, error: Exception) -> NoReturn:
    """Raise a WorkOSError wrapping a deserialization failure.

    Centralizes the error-wrapping logic used by all model from_dict methods.
    This function always raises and never returns.
    """
    from ._errors import WorkOSError

    raise WorkOSError(
        f"Unexpected API response while parsing {cls_name}: {error!s}"
    ) from error


def _format_datetime(dt: datetime) -> str:
    """Format a datetime as an ISO 8601 string with 'Z' suffix for UTC.

    Inverse of _parse_datetime: produces millisecond-precision ISO strings
    with '+00:00' replaced by 'Z' for consistency with the API.
    """
    return dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")
