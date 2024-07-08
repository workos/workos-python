import workos
from workos.utils.request import (
    RequestHelper,
    REQUEST_METHOD_GET,
)

from workos.utils.validation import EVENTS_MODULE, validate_settings
from workos.utils.types import JsonDict
from workos.resources.list import WorkOSListResource
from typing import Optional, TypedDict, List, Union
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

EVENT_TO_OBJECT = {
    DirectoryUserUpdatedEvent.event_name: DirectoryUserUpdatedEvent,
    DirectoryUserCreatedEvent.event_name: DirectoryUserCreatedEvent,
    DirectoryUserDeletedEvent.event_name: DirectoryUserDeletedEvent,
    DirectoryGroupCreatedEvent.event_name: DirectoryGroupCreatedEvent,
    DirectoryGroupDeletedEvent.event_name: DirectoryGroupDeletedEvent,
    DirectoryGroupUpdatedEvent.event_name: DirectoryGroupUpdatedEvent,
    DirectoryActivatedEvent.event_name: DirectoryActivatedEvent,
    DirectoryActivatedEvent.event_name: DirectoryDeletedEvent,
}
EVENT_TYPES = Union[
    DirectoryActivatedEvent,
    DirectoryDeletedEvent,
    DirectoryUserCreatedEvent,
    DirectoryUserDeletedEvent,
    DirectoryUserUpdatedEvent,
    DirectoryGroupCreatedEvent,
    DirectoryGroupDeletedEvent,
    DirectoryGroupUpdatedEvent,
]


class ListEventsResponse(TypedDict):
    object: str
    data: List[EVENT_TYPES]
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

    def list_events(
        self,
        events: Optional[List[EVENT_TYPES]]=None,
        limit: Optional[int] = None,
        organization_id: Optional[str] = None,
        after: Optional[str] = None,
        range_start: Optional[str] = None,
        range_end: Optional[str] = None,
    ) -> ListEventsResponse:
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

        data = []
        for list_data in response["data"]:
            if list_data["event"] in EVENT_TO_OBJECT.keys():
                data.append(EVENT_TO_OBJECT[list_data["event"]](list_data))
            
        response["data"] = data

        return response
