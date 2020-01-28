import workos
from workos.exceptions import ConfigurationException
from workos.utils.request import RequestHelper, REQUEST_METHOD_POST
from workos.utils.validation import validate_api_key_and_project_id

EVENTS_PATH = "events"
METADATA_LIMIT = 50


class AuditLog(object):
    """Offers methods through the WorkOS Audit Log service."""

    @validate_api_key_and_project_id("Audit Log")
    def __init__(self):
        pass

    @property
    def request_helper(self):
        if not getattr(self, "_request_helper", None):
            self._request_helper = RequestHelper()
        return self._request_helper

    def create_event(self, event, idempotency_key=None):
        """Create an Audit Log event.

        Args:
            event (dict) - An event object
                event[action] (str) - Specific activity performed by the actor.
                event[action_type] (str) - Corresponding CRUD category of the 
                    event. Can be one of C, R, U, or D.
                event[actor_name] (str) - Display name of the entity performing the action
                event[actor_id] (str) - Unique identifier of the entity performing the action
                event[group] (str) - A single organization containing related .
                    members. This will normally be the customer of a vendor's application
                event[location] (str) - Identifier for where the event 
                    originated. This will be an IP address (IPv4 or IPv6),
                    hostname, or device ID.
                event[occurred_at] (str) - ISO-8601 datetime at which the event
                    happened, with millisecond precision.
                event[metadata] (str) - Arbitrary key-value data containing
                    information associated with the event. Note: There is a limit of 50
                    keys. Key names can be up to 40 characters long, and values can be up
                    to 500 characters long.
                event[target_id] (str) - Unique identifier of the object or
                    resource being acted upon.
                event[target_name] (str) - Display name of the object or
                    resource that is being acted upon.
            idempotency_key (str) - An idempotency key

        Returns:
            dict: Response from WorkOS
        """
        if len(event.get("metadata", {})) > METADATA_LIMIT:
            raise Exception("Number of metadata keys exceeds %d." % METADATA_LIMIT)

        headers = {
            "Authorization": "Bearer %s" % workos.api_key,
            "idempotency_key": idempotency_key,
        }

        return self.request_helper.request(
            EVENTS_PATH, method=REQUEST_METHOD_POST, params=event, headers=headers
        )
