from typing import Union
import pytest

from tests.utils.fixtures.mock_event import MockEvent
from tests.utils.syncify import syncify
from workos.events import AsyncEvents, Events, EventsListResource


@pytest.mark.sync_and_async(Events, AsyncEvents)
class TestEvents(object):
    @pytest.fixture
    def mock_events(self):
        events = [MockEvent(id=str(i)).dict() for i in range(10)]

        return {
            "object": "list",
            "data": events,
            "list_metadata": {
                "after": None,
            },
        }

    def test_list_events(
        self,
        module_instance: Union[Events, AsyncEvents],
        mock_events: EventsListResource,
        capture_and_mock_http_client_request,
    ):
        request_kwargs = capture_and_mock_http_client_request(
            http_client=module_instance._http_client,
            status_code=200,
            response_dict=mock_events,
        )

        events: EventsListResource = syncify(
            module_instance.list_events(events=["dsync.activated"])
        )

        assert request_kwargs["url"].endswith("/events")
        assert request_kwargs["method"] == "get"
        assert request_kwargs["params"] == {"events": ["dsync.activated"], "limit": 10}
        assert events.dict() == mock_events
