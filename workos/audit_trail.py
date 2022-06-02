import workos
from workos.utils.pagiantion_order import Order
from workos.exceptions import ConfigurationException
from workos.resources.event import WorkOSEvent
from workos.utils.request import RequestHelper, REQUEST_METHOD_GET, REQUEST_METHOD_POST
from workos.utils.validation import AUDIT_TRAIL_MODULE, validate_settings

EVENTS_PATH = "events"
METADATA_LIMIT = 50
DEFAULT_EVENT_LIMIT = 10


class AuditTrail(object):
    """Offers methods through the WorkOS Audit Trail service."""

    @validate_settings(AUDIT_TRAIL_MODULE)
    def __init__(self):
        pass

    @property
    def request_helper(self):
        if not getattr(self, "_request_helper", None):
            self._request_helper = RequestHelper()
        return self._request_helper

    def create_event(self, event, idempotency_key=None):
        """Create an Audit Trail event.

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
            boolean: Returns True
        """
        if len(event.get("metadata", {})) > METADATA_LIMIT:
            raise ValueError(
                "Number of metadata keys exceeds {}.".format(METADATA_LIMIT)
            )

        headers = {
            "idempotency-key": idempotency_key,
        }

        response = self.request_helper.request(
            EVENTS_PATH,
            method=REQUEST_METHOD_POST,
            params=event,
            headers=headers,
            token=workos.api_key,
        )

        return response["success"]

    def get_events(
        self,
        before=None,
        after=None,
        limit=DEFAULT_EVENT_LIMIT,
        group=None,
        action=None,
        action_type=None,
        actor_name=None,
        actor_id=None,
        target_name=None,
        target_id=None,
        occurred_at=None,
        occurred_at_gt=None,
        occurred_at_gte=None,
        occurred_at_lt=None,
        occurred_at_lte=None,
        search=None,
        order=None,
    ):
        """Filter for Audit Trail Events.

        Kwargs:
            before (str) - Event ID to look before
            after (str) - Event ID to look after
            limit (int) - Number of Events to return
            order (Order) - Order to paginate records
            group (str|list) - Group or groups to filter for
            action (str|list) - Action or actions to filter for
            action_type (str|list) - Action type or types to filter for
            actor_name (str|list) - Actor name or name to filter for
            actor_id (str|list) - Actor ID or IDs to filter for
            target_name (str|list) - Target name or names to filter for
            target_id (str|list) - Target ID or IDs to filter for
            occurred_at (str) - ISO-8601 datetime of when an event occurred
            occurred_at_gt (str) - ISO-8601 datetime of when an event occurred after
            occurred_at_gte (str) - ISO-8601 datetime of when an event occurred at or after
            occurred_at_lt (str) - ISO-8601 datetime of when an event occurred before
            occurred_at_lte (str) - ISO-8601 datetime of when an event occured at or before
            search (str) - Keyword search

        Returns:
            tuple
                list - List of WorkOSEvent objects
                string - Event ID to use as before cursor
                string - Event ID to use as after cursor
        """
        params = {
            "before": before,
            "after": after,
            "limit": limit,
            "order": order,
        }

        if group is not None:
            params["group[]"] = group

        if action is not None:
            params["action[]"] = action

        if action_type is not None:
            params["action_type[]"] = action_type

        if actor_name is not None:
            params["actor_name[]"] = actor_name

        if actor_id is not None:
            params["actor_id[]"] = actor_id

        if target_name is not None:
            params["target_name[]"] = target_name

        if target_id is not None:
            params["target_id[]"] = target_id

        if occurred_at is not None:
            params["occurred_at"] = occurred_at
        else:
            if occurred_at_gte is not None:
                params["occurred_at_gte"] = occurred_at_gte
            elif occurred_at_gt is not None:
                params["occurred_at_gt"] = occurred_at_gt

            if occurred_at_lte is not None:
                params["occurred_at_lte"] = occurred_at_lte
            elif occurred_at_lt is not None:
                params["occurred_at_lt"] = occurred_at_lt

        if search is not None:
            params["search"] = search

        response = self.request_helper.request(
            EVENTS_PATH,
            method=REQUEST_METHOD_GET,
            params=params,
            token=workos.api_key,
        )

        events = [
            WorkOSEvent.construct_from_response(data) for data in response["data"]
        ]
        before = response["list_metadata"]["before"]
        after = response["list_metadata"]["after"]

        return (events, before, after)
