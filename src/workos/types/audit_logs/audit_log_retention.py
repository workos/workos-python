from workos.types.workos_model import WorkOSModel


class AuditLogRetention(WorkOSModel):
    """Representation of a WorkOS audit log retention configuration.

    Specifies how long audit log events are retained for an organization.
    Valid values are 30 and 365 days.
    """

    retention_period_in_days: int
