from typing import Literal, Optional

from workos.types.workos_model import WorkOSModel


AuditLogExportState = Literal["error", "pending", "ready"]


class AuditLogExport(WorkOSModel):
    """Representation of a WorkOS audit logs export."""

    object: Literal["audit_log_export"]
    id: str
    created_at: str
    updated_at: str
    state: AuditLogExportState
    url: Optional[str] = None
