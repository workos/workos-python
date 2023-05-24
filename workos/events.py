from warnings import warn
import workos
from workos.utils.request import (
    RequestHelper,
    REQUEST_METHOD_GET,
)

from workos.utils.validation import EVENTS_MODULE, validate_settings
from workos.resources.list import WorkOSListResource
import time

RESPONSE_LIMIT = 10


class Events(WorkOSListResource):
    """Offers methods through the WorkOS Events service."""

    @validate_settings(EVENTS_MODULE)
    def __init__(self):
        self.handler = None
        self.events = None
        pass

    @property
    def request_helper(self):
        if not getattr(self, "_request_helper", None):
            self._request_helper = RequestHelper()
        return self._request_helper

    def subscribe(
        self,
        handler=None,
        events=None
    ):
       """ Subscribe handler for events
       """
       self.handler = handler
       self.events = events 

    def start(
        self,
        limit=None,
        after=None,
        rangeStart=None,
        rangeEnd=None,
    ):
        """Gets a list of Events .
        Kwargs:
            events (list): Filter to only return events of particular types. (Optional)
            limit (int): Maximum number of records to return. (Optional)
            after (str): Pagination cursor to receive records after a provided Event ID. (Optional)
            rangeStart (str): Date range start for stream of events. (Optional)
            rangeEnd (str): Date range end for stream of events. (Optional)


        Returns:
            dict: Events response from WorkOS.
        """

        if limit is None:
            limit = RESPONSE_LIMIT

        params = {
            "events": self.events,
            "limit": limit,
            "after": after,
            "rangeStart": rangeStart,
            "rangeEnd": rangeEnd,
        }

        while True: 
            response = self.request_helper.request(
                "events",
                method=REQUEST_METHOD_GET,
                params=params,
                token=workos.api_key,
            )

            if self.handler:
                self.handler(response)

            params["after"] = response["list_metadata"]["after"]

            time.sleep(5)
