from warnings import warn
import workos
from workos.resources.audit_logs_export import WorkOSAuditLogExport
from workos.utils.request import RequestHelper, REQUEST_METHOD_GET, REQUEST_METHOD_POST
from workos.utils.validation import AUDIT_LOGS_MODULE, validate_settings

EVENTS_PATH = "audit_logs/events"
EXPORTS_PATH = "audit_logs/exports"


class AuditLogs(object):
    """Offers methods through the WorkOS Audit Logs service."""

    @validate_settings(AUDIT_LOGS_MODULE)
    def __init__(self):
        pass

    @property
    def request_helper(self):
        if not getattr(self, "_request_helper", None):
            self._request_helper = RequestHelper()
        return self._request_helper

    def create_event(self, organization, event, idempotency_key=None):
        """Create an Audit Logs event.

        Args:
            organization (str) - Organization's unique identifier
            event (dict) - An event object
                event[action] (string) - The event action
                event[version] (int) - The schema version of the event
                event[occurred_at] (datetime) - ISO-8601 datetime of when an event occurred
                event[actor] (dict) - Describes the entity that generated the event
                    event[actor][id] (str)
                    event[actor][name] (str)
                    event[actor][type] (str)
                    event[actor][metadata] (dict)
                event[targets] (list[dict]) - List of event targets
                event[context] (dict) - Attributes of event context
                    event[context][location] (str)
                    event[context][user_agent] (str)
                event[metadata] (dict) - Extra metadata
            idempotency_key (str) - Optional idempotency key

        Returns:
            boolean: Returns True
        """
        payload = {"organization_id": organization, "event": event}

        headers = {}
        if idempotency_key:
            headers["idempotency-key"] = idempotency_key

        response = self.request_helper.request(
            EVENTS_PATH,
            method=REQUEST_METHOD_POST,
            params=payload,
            headers=headers,
            token=workos.api_key,
        )

    def create_export(
        self,
        organization,
        range_start,
        range_end,
        actions=None,
        actors=None,
        targets=None,
        actor_names=None,
        actor_ids=None,
    ):
        """Trigger the creation of an export of audit logs.

        Args:
            organization (str) - Organization's unique identifier
            range_start (str) - Start date of the date range filter
            range_end (str) - End date of the date range filter
            actions (list) - Optional list of actions to filter
            actors (list) - Optional list of actors to filter
            targets (list) - Optional list of targets to filter

        Returns:
            dict: Object that describes the audit log export
        """

        payload = {
            "organization_id": organization,
            "range_start": range_start,
            "range_end": range_end,
        }

        if actions:
            payload["actions"] = actions

        if actors:
            payload["actors"] = actors
            warn(
                "The 'actors' parameter is deprecated. Please use 'actor_names' instead.",
                DeprecationWarning,
            )

        if actor_names:
            payload["actor_names"] = actor_names

        if actor_ids:
            payload["actor_ids"] = actor_ids

        if targets:
            payload["targets"] = targets

        response = self.request_helper.request(
            EXPORTS_PATH,
            method=REQUEST_METHOD_POST,
            params=payload,
            token=workos.api_key,
        )

        return WorkOSAuditLogExport.construct_from_response(response)

    def get_export(self, export_id):
        """Retrieve an created export.

        Returns:
            dict: Object that describes the audit log export
        """

        response = self.request_helper.request(
            "{0}/{1}".format(EXPORTS_PATH, export_id),
            method=REQUEST_METHOD_GET,
            token=workos.api_key,
        )

        return WorkOSAuditLogExport.construct_from_response(response)
