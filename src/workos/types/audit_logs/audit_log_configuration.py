from typing import Literal, Optional

from workos.types.workos_model import WorkOSModel
from workos.typing.literals import LiteralOrUntyped


AuditLogStreamType = Literal[
    "Datadog", "Splunk", "S3", "GoogleCloudStorage", "GenericHttps"
]

AuditLogStreamState = Literal["active", "inactive", "error", "invalid"]

AuditLogTrailState = Literal["active", "inactive", "disabled"]


class AuditLogStream(WorkOSModel):
    """Representation of a WorkOS audit log stream.

    An audit log stream sends audit log events to an external destination
    such as Datadog, Splunk, S3, Google Cloud Storage, or a custom HTTPS endpoint.
    """

    id: str
    type: LiteralOrUntyped[AuditLogStreamType]
    state: LiteralOrUntyped[AuditLogStreamState]
    last_synced_at: Optional[str] = None
    created_at: str


class AuditLogConfiguration(WorkOSModel):
    """Representation of a WorkOS audit log configuration for an organization.

    The audit log configuration provides a single view of an organization's
    audit logging setup, including retention settings, state, and optional
    log stream configuration.
    """

    organization_id: str
    retention_period_in_days: int
    state: LiteralOrUntyped[AuditLogTrailState]
    log_stream: Optional[AuditLogStream] = None
