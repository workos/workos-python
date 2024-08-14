from typing import Optional, Protocol, Sequence

from workos.types.audit_logs import AuditLogExport
from workos.types.audit_logs.audit_log_event import AuditLogEvent
from workos.utils.http_client import SyncHTTPClient
from workos.utils.request_helper import REQUEST_METHOD_GET, REQUEST_METHOD_POST

EVENTS_PATH = "audit_logs/events"
EXPORTS_PATH = "audit_logs/exports"


class AuditLogsModule(Protocol):
    """Offers methods through the WorkOS Audit Logs service."""

    def create_event(
        self,
        *,
        organization_id: str,
        event: AuditLogEvent,
        idempotency_key: Optional[str] = None,
    ) -> None:
        """Create an Audit Logs event.

        Kwargs:
            organization_id (str): Organization's unique identifier.
            event (AuditLogEvent): An AuditLogEvent object.
            idempotency_key (str): Idempotency key. (Optional)
        Returns:
            None
        """
        ...

    def create_export(
        self,
        *,
        organization_id: str,
        range_start: str,
        range_end: str,
        actions: Optional[Sequence[str]] = None,
        targets: Optional[Sequence[str]] = None,
        actor_names: Optional[Sequence[str]] = None,
        actor_ids: Optional[Sequence[str]] = None,
    ) -> AuditLogExport:
        """Trigger the creation of an export of audit logs.

        Kwargs:
            organization_id (str): Organization's unique identifier.
            range_start (str): Start date of the date range filter.
            range_end (str): End date of the date range filter.
            actions (list): Optional list of actions to filter. (Optional)
            actor_names (list): Optional list of actors to filter by name. (Optional)
            targets (list): Optional list of targets to filter. (Optional)

        Returns:
            AuditLogExport: Object that describes the audit log export
        """
        ...

    def get_export(self, audit_log_export_id: str) -> AuditLogExport:
        """Retrieve an created export.
        Args:
            audit_log_export_id (str): Audit log export unique identifier.
        Returns:
            AuditLogExport: Object that describes the audit log export
        """
        ...


class AuditLogs(AuditLogsModule):
    _http_client: SyncHTTPClient

    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def create_event(
        self,
        *,
        organization_id: str,
        event: AuditLogEvent,
        idempotency_key: Optional[str] = None,
    ) -> None:
        json = {"organization_id": organization_id, "event": event}

        headers = {}
        if idempotency_key:
            headers["idempotency-key"] = idempotency_key

        self._http_client.request(
            EVENTS_PATH, method=REQUEST_METHOD_POST, json=json, headers=headers
        )

    def create_export(
        self,
        *,
        organization_id: str,
        range_start: str,
        range_end: str,
        actions: Optional[Sequence[str]] = None,
        targets: Optional[Sequence[str]] = None,
        actor_names: Optional[Sequence[str]] = None,
        actor_ids: Optional[Sequence[str]] = None,
    ) -> AuditLogExport:
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
            EXPORTS_PATH, method=REQUEST_METHOD_POST, json=json
        )

        return AuditLogExport.model_validate(response)

    def get_export(self, audit_log_export_id: str) -> AuditLogExport:
        response = self._http_client.request(
            "{0}/{1}".format(EXPORTS_PATH, audit_log_export_id),
            method=REQUEST_METHOD_GET,
        )

        return AuditLogExport.model_validate(response)
