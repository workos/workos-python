from typing import Any, Dict, Literal, Mapping, Optional, Sequence

from typing_extensions import NotRequired, TypedDict

MetadataSchemaInput = Mapping[str, Literal["string", "number", "boolean"]]


class AuditLogSchemaTargetInput(TypedDict):
    """Input type for target definitions when creating an audit log schema.

    Attributes:
        type: The target type identifier (e.g., "team", "user", "document").
        metadata: Optional simplified metadata schema mapping property names to types.
    """

    type: str
    metadata: NotRequired[MetadataSchemaInput]


class AuditLogSchemaActorInput(TypedDict):
    """Input type for actor definition when creating an audit log schema.

    Attributes:
        metadata: Simplified metadata schema mapping property names to types.
    """

    metadata: MetadataSchemaInput


def _serialize_metadata(
    metadata: Optional[MetadataSchemaInput],
) -> Optional[Dict[str, Any]]:
    """Transform simplified metadata to full JSON Schema format.

    Transforms {"role": "string"} to:
    {"type": "object", "properties": {"role": {"type": "string"}}}
    """
    if not metadata:
        return None

    properties: Dict[str, Dict[str, str]] = {}
    for key, type_value in metadata.items():
        properties[key] = {"type": type_value}

    return {"type": "object", "properties": properties}


def serialize_schema_options(
    targets: Sequence[AuditLogSchemaTargetInput],
    actor: Optional[AuditLogSchemaActorInput] = None,
    metadata: Optional[MetadataSchemaInput] = None,
) -> Dict[str, Any]:
    """Serialize schema options from simplified format to API format.

    Transforms the simplified input format (matching JS SDK ergonomics)
    to the full JSON Schema format expected by the API.
    """
    result: Dict[str, Any] = {
        "targets": [
            {
                "type": target["type"],
                **(
                    {"metadata": _serialize_metadata(target.get("metadata"))}
                    if target.get("metadata")
                    else {}
                ),
            }
            for target in targets
        ],
    }

    if actor is not None:
        result["actor"] = {"metadata": _serialize_metadata(actor["metadata"])}

    if metadata is not None:
        result["metadata"] = _serialize_metadata(metadata)

    return result
