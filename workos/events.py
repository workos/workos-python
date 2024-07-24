from typing import List, Optional, Protocol

import workos
from workos.typing.sync_or_async import SyncOrAsync
from workos.utils.request import REQUEST_METHOD_GET
from workos.resources.events import Event, EventType
from workos.utils.http_client import AsyncHTTPClient, SyncHTTPClient
from workos.utils.validation import EVENTS_MODULE, validate_settings
from workos.resources.list import (
    ListArgs,
    ListPage,
    WorkOsListResource,
)

RESPONSE_LIMIT = 10


class EventsListFilters(ListArgs, total=False):
    events: List[EventType]
    organization_id: Optional[str]
    range_start: Optional[str]
    range_end: Optional[str]


EventsListResource = WorkOsListResource[Event, EventsListFilters]


class EventsModule(Protocol):
    def list_events(
        self,
        events: List[EventType],
        limit: int = RESPONSE_LIMIT,
        organization_id: Optional[str] = None,
        after: Optional[str] = None,
        range_start: Optional[str] = None,
        range_end: Optional[str] = None,
    ) -> SyncOrAsync[EventsListResource]:
        ...


class Events(EventsModule):
    """Offers methods through the WorkOS Events service."""

    _http_client: SyncHTTPClient

    @validate_settings(EVENTS_MODULE)
    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def list_events(
        self,
        events: List[EventType],
        limit: int = RESPONSE_LIMIT,
        organization: Optional[str] = None,
        after: Optional[str] = None,
        range_start: Optional[str] = None,
        range_end: Optional[str] = None,
    ) -> EventsListResource:
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

        params: EventsListFilters = {
            "events": events,
            "limit": limit,
            "after": after,
            "organization_id": organization,
            "range_start": range_start,
            "range_end": range_end,
        }

        response = self._http_client.request(
            "events",
            method=REQUEST_METHOD_GET,
            params=params,
            token=workos.api_key,
        )
        return WorkOsListResource(
            list_method=self.list_events,
            list_args=params,
            **ListPage[Event](**response).model_dump(exclude_unset=True),
        )


class AsyncEvents(EventsModule):
    """Offers methods through the WorkOS Events service."""

    _http_client: AsyncHTTPClient

    @validate_settings(EVENTS_MODULE)
    def __init__(self, http_client: AsyncHTTPClient):
        self._http_client = http_client

    async def list_events(
        self,
        events: List[EventType],
        limit: int = RESPONSE_LIMIT,
        organization_id: Optional[str] = None,
        after: Optional[str] = None,
        range_start: Optional[str] = None,
        range_end: Optional[str] = None,
    ) -> EventsListResource:
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
        params: EventsListFilters = {
            "events": events,
            "limit": limit,
            "after": after,
            "organization_id": organization_id,
            "range_start": range_start,
            "range_end": range_end,
        }

        response = await self._http_client.request(
            "events",
            method=REQUEST_METHOD_GET,
            params=params,
            token=workos.api_key,
        )

        return WorkOsListResource(
            list_method=self.list_events,
            list_args=params,
            **ListPage[Event](**response).model_dump(exclude_unset=True),
        )
