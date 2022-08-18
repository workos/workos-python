import workos
from workos.utils.pagiantion_order import Order
from workos.exceptions import ConfigurationException
from workos.resources.event import WorkOSEvent
from workos.utils.request import RequestHelper, REQUEST_METHOD_GET, REQUEST_METHOD_POST
from workos.utils.validation import AUDIT_TRAIL_MODULE, validate_settings

EVENTS_PATH = "audit_logs/events"
EXPORTS_PATH = "audit_logs/exports"


class AuditLogs(object):
    """Offers methods through the WorkOS Audit Logs service."""

    @validate_settings(AUDIT_TRAIL_MODULE)
    def __init__(self):
        pass

    @property
    def request_helper(self):
        if not getattr(self, "_request_helper", None):
            self._request_helper = RequestHelper()
        return self._request_helper

    def create_event(self, organization_id, event, idempotency_key=None):
        """Create an Audit Logs event.

        Args:
            organization_id (str) - Organization's unique identifier
            event (dict) - An event object
                event[action] (string) - The event action
                event[version] (int) - The version of event
                event[occurred_at] (datetime) - ISO-8601 datetime of when an event occurred
                event[actor] (dict) - Describes the entity that generated the event
                    event[actor][id] (str)
                    event[actor][name] (str)
                    event[actor][type] (str)
                    event[actor][metadata] (dict)
                event[targets] (list[dict])
                event[context] (dict)
                    event[context][location] (str)
                    event[context][user_agent] (str)
                event[metadata] (dict)
            idempotency_key (str) - An idempotency key

        Returns:
            boolean: Returns True
        """
        payload = {
            "organization_id": organization_id,
            "event": event
        }

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

        return response["success"]
