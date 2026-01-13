from typing_extensions import NotRequired, TypedDict

from workos.types.audit_logs.audit_log_metadata import AuditLogMetadata


class AuditLogEventActor(TypedDict):
    """Describes the entity that generated the event."""

    id: str
    metadata: NotRequired[AuditLogMetadata]
    name: NotRequired[str]
    type: str
