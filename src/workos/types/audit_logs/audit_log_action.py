from typing import Literal

from pydantic import ConfigDict, Field

from workos.types.audit_logs.audit_log_schema import AuditLogSchema
from workos.types.workos_model import WorkOSModel


class AuditLogAction(WorkOSModel):
    """Representation of a WorkOS audit log action.

    An audit log action represents a configured action type that can be
    used in audit log events. Each action has an associated schema that
    defines the structure of events for that action.
    """

    model_config = ConfigDict(populate_by_name=True)

    object: Literal["audit_log_action"]
    name: str
    action_schema: AuditLogSchema = Field(alias="schema")
    created_at: str
    updated_at: str
