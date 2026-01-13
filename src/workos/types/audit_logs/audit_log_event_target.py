from typing_extensions import NotRequired, TypedDict

from workos.types.audit_logs.audit_log_metadata import AuditLogMetadata


class AuditLogEventTarget(TypedDict):
    """Describes the entity that was targeted by the event."""

    id: str
    metadata: NotRequired[AuditLogMetadata]
    name: NotRequired[str]
    type: str
