from typing import List

import workos
from workos.utils.request import (
    REQUEST_METHOD_GET,
)
from workos.utils.http_client import AsyncHTTPClient, SyncHTTPClient
from workos.utils.validation import EVENTS_MODULE, validate_settings
from workos.resources.list import WorkOSListResource

RESPONSE_LIMIT = 10


class Events(WorkOSListResource):
    """Offers methods through the WorkOS Events service."""

    _http_client: SyncHTTPClient

    @validate_settings(EVENTS_MODULE)
    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def list_events(
        self,
        # TODO: Use event Literal type when available
        events: List[str],
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

        response = self._http_client.request(
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


class AsyncEvents(WorkOSListResource):
    """Offers methods through the WorkOS Events service."""

    _http_client: AsyncHTTPClient

    @validate_settings(EVENTS_MODULE)
    def __init__(self, http_client: AsyncHTTPClient):
        self._http_client = http_client

    async def list_events(
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

        response = await self._http_client.request(
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
            "method": AsyncEvents.list_events,
        }

        return response
