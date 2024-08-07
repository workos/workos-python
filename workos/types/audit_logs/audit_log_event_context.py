from typing import NotRequired, TypedDict


class AuditLogEventContext(TypedDict):
    """Attributes of audit log event context."""

    location: str
    user_agent: NotRequired[str]
