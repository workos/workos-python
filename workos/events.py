from warnings import warn
import workos
from workos.utils.request import (
    RequestHelper,
    REQUEST_METHOD_GET,
)

from workos.utils.validation import EVENTS_MODULE, validate_settings
from workos.utils.types import JsonDict
from workos.resources.list import WorkOSListResource
from typing import Optional, Dict, TypedDict, List, Any
from workos.event_objects.directory import (
    DirectoryActivatedEvent,
    DirectoryDeletedEvent,
)
from workos.event_objects.directory_group import (
    DirectoryGroupCreatedEvent,
    DirectoryGroupDeletedEvent,
    DirectoryGroupUpdatedEvent,
)
from workos.event_objects.directory_user import (
    DirectoryUserCreatedEvent,
    DirectoryUserDeletedEvent,
    DirectoryUserUpdatedEvent,
)

DSYNC_EVENT_TYPES = Dict[
    DirectoryUserUpdatedEvent.event : DirectoryUserUpdatedEvent,
    DirectoryUserCreatedEvent.event : DirectoryUserCreatedEvent,
    DirectoryUserDeletedEvent.event : DirectoryUserDeletedEvent,
    DirectoryGroupCreatedEvent.event : DirectoryGroupCreatedEvent,
    DirectoryGroupDeletedEvent.event : DirectoryGroupDeletedEvent,
    DirectoryGroupUpdatedEvent.event : DirectoryGroupUpdatedEvent,
    DirectoryActivatedEvent.event : DirectoryActivatedEvent,
    DirectoryActivatedEvent.event : DirectoryDeletedEvent,
]


class ListDsyncEventsResponse(TypedDict):
    object: str
    data: List[DSYNC_EVENT_TYPES.values()]
    metadata: JsonDict


RESPONSE_LIMIT = 10


class Events(WorkOSListResource):
    """Offers methods through the WorkOS Events service."""

    @validate_settings(EVENTS_MODULE)
    def __init__(self):
        pass

    @property
    def request_helper(self):
        if not getattr(self, "_request_helper", None):
            self._request_helper = RequestHelper()
        return self._request_helper

    def list_dsync_events(
        self,
        limit: Optional[int] = None,
        organization_id: Optional[str] = None,
        after: Optional[str] = None,
        range_start: Optional[str] = None,
        range_end: Optional[str] = None,
    ) -> ListDsyncEventsResponse:
        if limit is None:
            limit = RESPONSE_LIMIT
            default_limit = True

        params = {
            "events": DSYNC_EVENT_TYPES.keys(),
            "limit": limit,
            "after": after,
            "organization_id": organization_id,
            "range_start": range_start,
            "range_end": range_end,
        }

        response = self.request_helper.request(
            "events",
            method=REQUEST_METHOD_GET,
            params=params,
            token=workos.api_key,
        )

        response = {
            "object": "list",
            "params": params,
        }

        data = []
        for list_data in response["data"]:
            data.push(DSYNC_EVENT_TYPES[list_data["event"]](list_data))
        response["data"] = data
        return response

    def list_events(
        self,
        events=None,
        limit=None,
        organization_id=None,
        after=None,
        range_start=None,
        range_end=None,
    ):
        """Gets a list of Events .
        Kwargs:
            events (list): Filter to only return events of particular types. (Optional)
            limit (int): Maximum number of records to return. (Optional)
            organization_id(str): Organization ID limits scope of events to a single organization. (Optional)
            after (str): Pagination cursor to receive records after a provided Event ID. (Optional)
            range_start (str): Date range start for stream of events. (Optional)
            range_end (str): Date range end for stream of events. (Optional)


        Returns:
            dict: Events response from WorkOS.
        """

        if limit is None:
            limit = RESPONSE_LIMIT
            default_limit = True

        params = {
            "events": events,
            "limit": limit,
            "after": after,
            "organization_id": organization_id,
            "range_start": range_start,
            "range_end": range_end,
        }

        response = self.request_helper.request(
            "events",
            method=REQUEST_METHOD_GET,
            params=params,
            token=workos.api_key,
        )

        if "default_limit" in locals():
            if "metadata" in response and "params" in response["metadata"]:
                response["metadata"]["params"]["default_limit"] = default_limit
            else:
                response["metadata"] = {"params": {"default_limit": default_limit}}

        response["metadata"] = {
            "params": params,
            "method": Events.list_events,
        }

        return response
