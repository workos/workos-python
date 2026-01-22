from typing import Dict, Literal, Optional, Protocol, Sequence

from workos.types.audit_logs import (
    AuditLogAction,
    AuditLogConfiguration,
    AuditLogExport,
    AuditLogRetention,
    AuditLogSchema,
    AuditLogSchemaListFilters,
    AuditLogActionListFilters,
)
from workos.types.audit_logs.audit_log_schema_input import (
    AuditLogSchemaActorInput,
    AuditLogSchemaTargetInput,
    MetadataSchemaInput,
    serialize_schema_options,
)
from workos.types.audit_logs.audit_log_event import AuditLogEvent
from workos.types.list_resource import ListMetadata, ListPage, WorkOSListResource
from workos.typing.sync_or_async import SyncOrAsync
from workos.utils.http_client import AsyncHTTPClient, SyncHTTPClient
from workos.utils.pagination_order import PaginationOrder
from workos.utils.request_helper import (
    DEFAULT_LIST_RESPONSE_LIMIT,
    REQUEST_METHOD_GET,
    REQUEST_METHOD_POST,
    REQUEST_METHOD_PUT,
)

EVENTS_PATH = "audit_logs/events"
EXPORTS_PATH = "audit_logs/exports"
ACTIONS_PATH = "audit_logs/actions"


AuditLogActionsListResource = WorkOSListResource[
    AuditLogAction, AuditLogActionListFilters, ListMetadata
]

AuditLogSchemasListResource = WorkOSListResource[
    AuditLogSchema, AuditLogSchemaListFilters, ListMetadata
]


class AuditLogsModule(Protocol):
    """Offers methods through the WorkOS Audit Logs service."""

    def create_event(
        self,
        *,
        organization_id: str,
        event: AuditLogEvent,
        idempotency_key: Optional[str] = None,
    ) -> SyncOrAsync[None]:
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
    ) -> SyncOrAsync[AuditLogExport]:
        """Trigger the creation of an export of audit logs.

        Kwargs:
            organization_id (str): Organization's unique identifier.
            range_start (str): Start date of the date range filter.
            range_end (str): End date of the date range filter.
            actions (list): Optional list of actions to filter. (Optional)
            actor_names (list): Optional list of actors to filter by name. (Optional)
            actor_ids (list): Optional list of actors to filter by ID. (Optional)
            targets (list): Optional list of targets to filter. (Optional)

        Returns:
            AuditLogExport: Object that describes the audit log export
        """
        ...

    def get_export(self, audit_log_export_id: str) -> SyncOrAsync[AuditLogExport]:
        """Retrieve a created export.

        Args:
            audit_log_export_id (str): Audit log export unique identifier.

        Returns:
            AuditLogExport: Object that describes the audit log export
        """
        ...

    def create_schema(
        self,
        *,
        action: str,
        targets: Sequence[AuditLogSchemaTargetInput],
        actor: Optional[AuditLogSchemaActorInput] = None,
        metadata: Optional[MetadataSchemaInput] = None,
        idempotency_key: Optional[str] = None,
    ) -> SyncOrAsync[AuditLogSchema]:
        """Create an Audit Log schema for an action.

        Kwargs:
            action (str): The action name for the schema (e.g., 'user.signed_in').
            targets (list): List of target definitions with type and optional metadata.
                Each target has a 'type' and optional 'metadata' mapping property
                names to types (e.g., {"status": "string"}).
            actor (dict): Optional actor definition with metadata schema. (Optional)
                The metadata maps property names to types (e.g., {"role": "string"}).
            metadata (dict): Optional event-level metadata schema. (Optional)
                Maps property names to types (e.g., {"invoice_id": "string"}).
            idempotency_key (str): Idempotency key. (Optional)

        Returns:
            AuditLogSchema: The created audit log schema
        """
        ...

    def list_schemas(
        self,
        *,
        action: str,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> SyncOrAsync[AuditLogSchemasListResource]:
        """List all schemas for an Audit Log action.

        Kwargs:
            action (str): The action name to list schemas for.
            limit (int): Maximum number of records to return. (Optional)
            before (str): Pagination cursor to receive records before a provided ID. (Optional)
            after (str): Pagination cursor to receive records after a provided ID. (Optional)
            order (Literal["asc","desc"]): Sort order by created_at timestamp. (Optional)

        Returns:
            AuditLogSchemasListResource: Paginated list of audit log schemas
        """
        ...

    def list_actions(
        self,
        *,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> SyncOrAsync[AuditLogActionsListResource]:
        """List all registered Audit Log actions.

        Kwargs:
            limit (int): Maximum number of records to return. (Optional)
            before (str): Pagination cursor to receive records before a provided ID. (Optional)
            after (str): Pagination cursor to receive records after a provided ID. (Optional)
            order (Literal["asc","desc"]): Sort order by created_at timestamp. (Optional)

        Returns:
            AuditLogActionsListResource: Paginated list of audit log actions
        """
        ...

    def get_retention(self, organization_id: str) -> SyncOrAsync[AuditLogRetention]:
        """Get the event retention period for an organization.

        Args:
            organization_id (str): Organization's unique identifier.

        Returns:
            AuditLogRetention: The retention configuration
        """
        ...

    def set_retention(
        self,
        *,
        organization_id: str,
        retention_period_in_days: Literal[30, 365],
    ) -> SyncOrAsync[AuditLogRetention]:
        """Set the event retention period for an organization.

        Kwargs:
            organization_id (str): Organization's unique identifier.
            retention_period_in_days (int): The number of days to retain events (30 or 365).

        Returns:
            AuditLogRetention: The updated retention configuration
        """
        ...

    def get_configuration(
        self, organization_id: str
    ) -> SyncOrAsync[AuditLogConfiguration]:
        """Get the audit log configuration for an organization.

        Args:
            organization_id (str): Organization's unique identifier.

        Returns:
            AuditLogConfiguration: The complete audit log configuration
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

        headers: Dict[str, str] = {}
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
            f"{EXPORTS_PATH}/{audit_log_export_id}",
            method=REQUEST_METHOD_GET,
        )

        return AuditLogExport.model_validate(response)

    def create_schema(
        self,
        *,
        action: str,
        targets: Sequence[AuditLogSchemaTargetInput],
        actor: Optional[AuditLogSchemaActorInput] = None,
        metadata: Optional[MetadataSchemaInput] = None,
        idempotency_key: Optional[str] = None,
    ) -> AuditLogSchema:
        json = serialize_schema_options(targets, actor, metadata)

        headers: Dict[str, str] = {}
        if idempotency_key:
            headers["idempotency-key"] = idempotency_key

        response = self._http_client.request(
            f"{ACTIONS_PATH}/{action}/schemas",
            method=REQUEST_METHOD_POST,
            json=json,
            headers=headers,
        )

        return AuditLogSchema.model_validate(response)

    def list_schemas(
        self,
        *,
        action: str,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> AuditLogSchemasListResource:
        list_params: AuditLogSchemaListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        response = self._http_client.request(
            f"{ACTIONS_PATH}/{action}/schemas",
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        return WorkOSListResource[
            AuditLogSchema, AuditLogSchemaListFilters, ListMetadata
        ](
            list_method=lambda **kwargs: self.list_schemas(action=action, **kwargs),
            list_args=list_params,
            **ListPage[AuditLogSchema](**response).model_dump(),
        )

    def list_actions(
        self,
        *,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> AuditLogActionsListResource:
        list_params: AuditLogActionListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        response = self._http_client.request(
            ACTIONS_PATH,
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        return WorkOSListResource[
            AuditLogAction, AuditLogActionListFilters, ListMetadata
        ](
            list_method=self.list_actions,
            list_args=list_params,
            **ListPage[AuditLogAction](**response).model_dump(),
        )

    def get_retention(self, organization_id: str) -> AuditLogRetention:
        response = self._http_client.request(
            f"organizations/{organization_id}/audit_logs_retention",
            method=REQUEST_METHOD_GET,
        )

        return AuditLogRetention.model_validate(response)

    def set_retention(
        self,
        *,
        organization_id: str,
        retention_period_in_days: Literal[30, 365],
    ) -> AuditLogRetention:
        json = {"retention_period_in_days": retention_period_in_days}

        response = self._http_client.request(
            f"organizations/{organization_id}/audit_logs_retention",
            method=REQUEST_METHOD_PUT,
            json=json,
        )

        return AuditLogRetention.model_validate(response)

    def get_configuration(self, organization_id: str) -> AuditLogConfiguration:
        response = self._http_client.request(
            f"organizations/{organization_id}/audit_log_configuration",
            method=REQUEST_METHOD_GET,
        )

        return AuditLogConfiguration.model_validate(response)


class AsyncAuditLogs(AuditLogsModule):
    _http_client: AsyncHTTPClient

    def __init__(self, http_client: AsyncHTTPClient):
        self._http_client = http_client

    async def create_event(
        self,
        *,
        organization_id: str,
        event: AuditLogEvent,
        idempotency_key: Optional[str] = None,
    ) -> None:
        json = {"organization_id": organization_id, "event": event}

        headers: Dict[str, str] = {}
        if idempotency_key:
            headers["idempotency-key"] = idempotency_key

        await self._http_client.request(
            EVENTS_PATH, method=REQUEST_METHOD_POST, json=json, headers=headers
        )

    async def create_export(
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

        response = await self._http_client.request(
            EXPORTS_PATH, method=REQUEST_METHOD_POST, json=json
        )

        return AuditLogExport.model_validate(response)

    async def get_export(self, audit_log_export_id: str) -> AuditLogExport:
        response = await self._http_client.request(
            f"{EXPORTS_PATH}/{audit_log_export_id}",
            method=REQUEST_METHOD_GET,
        )

        return AuditLogExport.model_validate(response)

    async def create_schema(
        self,
        *,
        action: str,
        targets: Sequence[AuditLogSchemaTargetInput],
        actor: Optional[AuditLogSchemaActorInput] = None,
        metadata: Optional[MetadataSchemaInput] = None,
        idempotency_key: Optional[str] = None,
    ) -> AuditLogSchema:
        json = serialize_schema_options(targets, actor, metadata)

        headers: Dict[str, str] = {}
        if idempotency_key:
            headers["idempotency-key"] = idempotency_key

        response = await self._http_client.request(
            f"{ACTIONS_PATH}/{action}/schemas",
            method=REQUEST_METHOD_POST,
            json=json,
            headers=headers,
        )

        return AuditLogSchema.model_validate(response)

    async def list_schemas(
        self,
        *,
        action: str,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> AuditLogSchemasListResource:
        list_params: AuditLogSchemaListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        response = await self._http_client.request(
            f"{ACTIONS_PATH}/{action}/schemas",
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        return WorkOSListResource[
            AuditLogSchema, AuditLogSchemaListFilters, ListMetadata
        ](
            list_method=lambda **kwargs: self.list_schemas(action=action, **kwargs),
            list_args=list_params,
            **ListPage[AuditLogSchema](**response).model_dump(),
        )

    async def list_actions(
        self,
        *,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> AuditLogActionsListResource:
        list_params: AuditLogActionListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        response = await self._http_client.request(
            ACTIONS_PATH,
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        return WorkOSListResource[
            AuditLogAction, AuditLogActionListFilters, ListMetadata
        ](
            list_method=self.list_actions,
            list_args=list_params,
            **ListPage[AuditLogAction](**response).model_dump(),
        )

    async def get_retention(self, organization_id: str) -> AuditLogRetention:
        response = await self._http_client.request(
            f"organizations/{organization_id}/audit_logs_retention",
            method=REQUEST_METHOD_GET,
        )

        return AuditLogRetention.model_validate(response)

    async def set_retention(
        self,
        *,
        organization_id: str,
        retention_period_in_days: Literal[30, 365],
    ) -> AuditLogRetention:
        json = {"retention_period_in_days": retention_period_in_days}

        response = await self._http_client.request(
            f"organizations/{organization_id}/audit_logs_retention",
            method=REQUEST_METHOD_PUT,
            json=json,
        )

        return AuditLogRetention.model_validate(response)

    async def get_configuration(self, organization_id: str) -> AuditLogConfiguration:
        response = await self._http_client.request(
            f"organizations/{organization_id}/audit_log_configuration",
            method=REQUEST_METHOD_GET,
        )

        return AuditLogConfiguration.model_validate(response)
