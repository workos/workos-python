from typing import Optional, Protocol, Sequence

from workos.types.events.list_filters import EventsListFilters
from workos.typing.sync_or_async import SyncOrAsync
from workos.utils.request_helper import DEFAULT_LIST_RESPONSE_LIMIT, REQUEST_METHOD_GET
from workos.types.events import Event, EventType
from workos.utils.http_client import AsyncHTTPClient, SyncHTTPClient
from workos.types.list_resource import ListAfterMetadata, ListPage, WorkOSListResource


EventsListResource = WorkOSListResource[Event, EventsListFilters, ListAfterMetadata]


class EventsModule(Protocol):
    """Offers methods through the WorkOS Events service."""

    def list_events(
        self,
        *,
        events: Sequence[EventType],
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        organization_id: Optional[str] = None,
        after: Optional[str] = None,
        range_start: Optional[str] = None,
        range_end: Optional[str] = None,
    ) -> SyncOrAsync[EventsListResource]:
        """Gets a list of Events.

        Kwargs:
            events (Sequence[EventType]): Filter to only return events of particular types.
            limit (int): Maximum number of records to return. (Optional)
            organization_id (str): Organization ID limits scope of events to a single organization. (Optional)
            after (str): Pagination cursor to receive records after a provided Event ID. (Optional)
            range_start (str): Date range start for stream of events. (Optional)
            range_end (str): Date range end for stream of events. (Optional)

        Returns:
            EventsListResource: Events response from WorkOS.
        """
        ...


class Events(EventsModule):
    _http_client: SyncHTTPClient

    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def list_events(
        self,
        *,
        events: Sequence[EventType],
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        organization_id: Optional[str] = None,
        after: Optional[str] = None,
        range_start: Optional[str] = None,
        range_end: Optional[str] = None,
    ) -> EventsListResource:
        params: EventsListFilters = {
            "events": events,
            "limit": limit,
            "after": after,
            "organization_id": organization_id,
            "range_start": range_start,
            "range_end": range_end,
        }

        response = self._http_client.request(
            "events", method=REQUEST_METHOD_GET, params=params
        )
        return WorkOSListResource[Event, EventsListFilters, ListAfterMetadata](
            list_method=self.list_events,
            list_args=params,
            **ListPage[Event](**response).model_dump(exclude_unset=True),
        )


class AsyncEvents(EventsModule):
    _http_client: AsyncHTTPClient

    def __init__(self, http_client: AsyncHTTPClient):
        self._http_client = http_client

    async def list_events(
        self,
        *,
        events: Sequence[EventType],
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        organization_id: Optional[str] = None,
        after: Optional[str] = None,
        range_start: Optional[str] = None,
        range_end: Optional[str] = None,
    ) -> EventsListResource:
        params: EventsListFilters = {
            "events": events,
            "limit": limit,
            "after": after,
            "organization_id": organization_id,
            "range_start": range_start,
            "range_end": range_end,
        }

        response = await self._http_client.request(
            "events", method=REQUEST_METHOD_GET, params=params
        )

        return WorkOSListResource[Event, EventsListFilters, ListAfterMetadata](
            list_method=self.list_events,
            list_args=params,
            **ListPage[Event](**response).model_dump(exclude_unset=True),
        )
