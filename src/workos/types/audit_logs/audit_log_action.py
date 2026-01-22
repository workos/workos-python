import warnings
from typing import Literal

from workos.types.audit_logs.audit_log_schema import AuditLogSchema
from workos.types.workos_model import WorkOSModel

# Suppress Pydantic warning about 'schema' shadowing BaseModel.schema()
# (a deprecated method replaced by model_json_schema() in Pydantic v2)
warnings.filterwarnings(
    "ignore",
    message='Field name "schema" in "AuditLogAction" shadows an attribute',
    category=UserWarning,
)


class AuditLogAction(WorkOSModel):
    """Representation of a WorkOS audit log action.

    An audit log action represents a configured action type that can be
    used in audit log events. Each action has an associated schema that
    defines the structure of events for that action.
    """

    object: Literal["audit_log_action"]
    name: str
    schema: AuditLogSchema  # type: ignore[assignment]
    created_at: str
    updated_at: str
