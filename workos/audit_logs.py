from typing import List, Optional, Protocol

import workos
from workos.resources.audit_logs import AuditLogEvent, AuditLogExport
from workos.utils.http_client import SyncHTTPClient
from workos.utils.request_helper import REQUEST_METHOD_GET, REQUEST_METHOD_POST
from workos.utils.validation import AUDIT_LOGS_MODULE, validate_settings

EVENTS_PATH = "audit_logs/events"
EXPORTS_PATH = "audit_logs/exports"


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
        actions: Optional[List[str]] = None,
        targets: Optional[List[str]] = None,
        actor_names: Optional[List[str]] = None,
        actor_ids: Optional[List[str]] = None,
    ) -> AuditLogExport: ...

    def get_export(self, audit_log_export_id: str) -> AuditLogExport: ...


class AuditLogs(AuditLogsModule):
    """Offers methods through the WorkOS Audit Logs service."""

    _http_client: SyncHTTPClient

    @validate_settings(AUDIT_LOGS_MODULE)
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
        payload = {"organization_id": organization_id, "event": event}

        headers = {}
        if idempotency_key:
            headers["idempotency-key"] = idempotency_key

        self._http_client.request(
            EVENTS_PATH,
            method=REQUEST_METHOD_POST,
            params=payload,
            headers=headers,
            token=workos.api_key,
        )

    def create_export(
        self,
        organization_id: str,
        range_start: str,
        range_end: str,
        actions: Optional[List[str]] = None,
        targets: Optional[List[str]] = None,
        actor_names: Optional[List[str]] = None,
        actor_ids: Optional[List[str]] = None,
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

        payload = {
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
            params=payload,
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
