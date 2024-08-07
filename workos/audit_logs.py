from typing import Dict, Optional, Protocol, Sequence
from typing_extensions import TypedDict, NotRequired

import workos
from workos.resources.audit_logs import AuditLogExport, AuditLogMetadata
from workos.utils.http_client import SyncHTTPClient
from workos.utils.request_helper import REQUEST_METHOD_GET, REQUEST_METHOD_POST
from workos.utils.validation import Module, validate_settings

EVENTS_PATH = "audit_logs/events"
EXPORTS_PATH = "audit_logs/exports"


class AuditLogEventTarget(TypedDict):
    """Describes the entity that was targeted by the event."""

    id: str
    metadata: NotRequired[AuditLogMetadata]
    name: NotRequired[str]
    type: str


class AuditLogEventActor(TypedDict):
    """Describes the entity that generated the event."""

    id: str
    metadata: NotRequired[AuditLogMetadata]
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
    targets: Sequence[AuditLogEventTarget]
    context: AuditLogEventContext
    metadata: NotRequired[AuditLogMetadata]


class AuditLogsModule(Protocol):
    def create_event(
        self,
        organization_id: str,
        event: AuditLogEvent,
        idempotency_key: Optional[str] = None,
    ) -> None: ...

    def create_export(
        self,
        organization_id: str,
        range_start: str,
        range_end: str,
        actions: Optional[Sequence[str]] = None,
        targets: Optional[Sequence[str]] = None,
        actor_names: Optional[Sequence[str]] = None,
        actor_ids: Optional[Sequence[str]] = None,
    ) -> AuditLogExport: ...

    def get_export(self, audit_log_export_id: str) -> AuditLogExport: ...


class AuditLogs(AuditLogsModule):
    """Offers methods through the WorkOS Audit Logs service."""

    _http_client: SyncHTTPClient

    @validate_settings(Module.AUDIT_LOGS)
    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def create_event(
        self,
        organization_id: str,
        event: AuditLogEvent,
        idempotency_key: Optional[str] = None,
    ) -> None:
        """Create an Audit Logs event.

        Args:
            organization (str) - Organization's unique identifier
            event (AuditLogEvent) - An AuditLogEvent object
            idempotency_key (str) - Optional idempotency key
        """
        json = {"organization_id": organization_id, "event": event}

        headers = {}
        if idempotency_key:
            headers["idempotency-key"] = idempotency_key

        self._http_client.request(
            EVENTS_PATH,
            method=REQUEST_METHOD_POST,
            json=json,
            headers=headers,
            token=workos.api_key,
        )

    def create_export(
        self,
        organization_id: str,
        range_start: str,
        range_end: str,
        actions: Optional[Sequence[str]] = None,
        targets: Optional[Sequence[str]] = None,
        actor_names: Optional[Sequence[str]] = None,
        actor_ids: Optional[Sequence[str]] = None,
    ) -> AuditLogExport:
        """Trigger the creation of an export of audit logs.

        Args:
            organization (str) - Organization's unique identifier
            range_start (str) - Start date of the date range filter
            range_end (str) - End date of the date range filter
            actions (list) - Optional list of actions to filter
            actors (list) - Optional list of actors to filter
            targets (list) - Optional list of targets to filter

        Returns:
            AuditLogExport: Object that describes the audit log export
        """

        json = {
            "actions": actions,
            "actor_ids": actor_ids,
            "actor_names": actor_names,
            "organization_id": organization_id,
            "range_start": range_start,
            "range_end": range_end,
            "targets": targets,
        }

        response = self._http_client.request(
            EXPORTS_PATH,
            method=REQUEST_METHOD_POST,
            json=json,
            token=workos.api_key,
        )

        return AuditLogExport.model_validate(response)

    def get_export(self, audit_log_export_id: str) -> AuditLogExport:
        """Retrieve an created export.

        Returns:
            AuditLogExport: Object that describes the audit log export
        """

        response = self._http_client.request(
            "{0}/{1}".format(EXPORTS_PATH, audit_log_export_id),
            method=REQUEST_METHOD_GET,
            token=workos.api_key,
        )

        return AuditLogExport.model_validate(response)
