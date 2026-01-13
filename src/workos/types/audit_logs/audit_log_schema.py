from typing import Dict, Literal, Optional, Sequence

from workos.types.workos_model import WorkOSModel


class AuditLogSchemaMetadataProperty(WorkOSModel):
    """A property definition within an audit log schema metadata object."""

    type: Literal["string", "boolean", "number"]


class AuditLogSchemaMetadata(WorkOSModel):
    """The metadata definition for an audit log schema.

    Represents a JSON Schema object type with property definitions.
    """

    type: Literal["object"]
    properties: Optional[Dict[str, AuditLogSchemaMetadataProperty]] = None


class AuditLogSchemaTarget(WorkOSModel):
    """A target definition within an audit log schema."""

    type: str
    metadata: Optional[AuditLogSchemaMetadata] = None


class AuditLogSchemaActor(WorkOSModel):
    """The actor definition within an audit log schema."""

    metadata: AuditLogSchemaMetadata


class AuditLogSchema(WorkOSModel):
    """Representation of a WorkOS audit log schema.

    Audit log schemas define the structure and validation rules
    for audit log events, including the allowed targets, actor metadata,
    and event-level metadata.
    """

    object: Literal["audit_log_schema"] = "audit_log_schema"
    version: int
    targets: Sequence[AuditLogSchemaTarget]
    actor: AuditLogSchemaActor
    metadata: Optional[AuditLogSchemaMetadata] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
