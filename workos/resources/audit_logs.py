from typing import List, Literal, Optional, TypedDict
from typing_extensions import NotRequired

from workos.resources.workos_model import WorkOSModel

AuditLogExportState = Literal["error", "pending", "ready"]


class AuditLogExport(WorkOSModel):
    """Representation of a WorkOS audit logs export."""

    object: Literal["audit_log_export"]
    id: str
    created_at: str
    updated_at: str
    state: AuditLogExportState
    url: Optional[str] = None


class AuditLogEventActor(TypedDict):
    """Describes the entity that generated the event."""

    id: str
    metadata: NotRequired[dict]
    name: NotRequired[str]
    type: str


class AuditLogEventTarget(TypedDict):
    """Describes the entity that was targeted by the event."""

    id: str
    metadata: NotRequired[dict]
    name: NotRequired[str]
    type: str


class AuditLogEventContext(TypedDict):
    """Attributes of audit log event context."""

    location: str
    user_agent: NotRequired[str]


class AuditLogEvent(TypedDict):
    action: str
    version: NotRequired[int]
    occurred_at: str  # ISO-8601 datetime of when an event occurred
    actor: AuditLogEventActor
    targets: List[AuditLogEventTarget]
    context: AuditLogEventContext
    metadata: NotRequired[dict]
