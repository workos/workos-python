from typing_extensions import NotRequired, Sequence, TypedDict

from workos.types.audit_logs.audit_log_event_actor import AuditLogEventActor
from workos.types.audit_logs.audit_log_event_context import AuditLogEventContext
from workos.types.audit_logs.audit_log_metadata import AuditLogMetadata
from workos.types.audit_logs.audit_log_event_target import AuditLogEventTarget


class AuditLogEvent(TypedDict):
    action: str
    version: NotRequired[int]
    occurred_at: str  # ISO-8601 datetime of when an event occurred
    actor: AuditLogEventActor
    targets: Sequence[AuditLogEventTarget]
    context: AuditLogEventContext
    metadata: NotRequired[AuditLogMetadata]
