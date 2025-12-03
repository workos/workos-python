from workos.types.workos_model import WorkOSModel


class AuditLogEventResponse(WorkOSModel):
    """Response from creating an audit log event."""

    success: bool
