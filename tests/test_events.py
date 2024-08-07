import pytest

from tests.utils.fixtures.mock_event import MockEvent
from workos.events import AsyncEvents, Events


class TestEvents(object):
    @pytest.fixture(autouse=True)
    def setup(self, sync_http_client_for_test):
        self.http_client = sync_http_client_for_test
        self.events = Events(http_client=self.http_client)

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

    def test_list_events(self, mock_events, mock_http_client_with_response):
        mock_http_client_with_response(
            http_client=self.http_client,
            status_code=200,
            response_dict=mock_events,
        )

        events = self.events.list_events(events=["dsync.activated"])

        assert events.dict() == mock_events


@pytest.mark.asyncio
class TestAsyncEvents(object):
    @pytest.fixture(autouse=True)
    def setup(self, async_http_client_for_test):
        self.http_client = async_http_client_for_test
        self.events = AsyncEvents(http_client=self.http_client)

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

    async def test_list_events(self, mock_events, mock_http_client_with_response):
        mock_http_client_with_response(
            http_client=self.http_client,
            status_code=200,
            response_dict=mock_events,
        )

        events = await self.events.list_events(events=["dsync.activated"])

        assert events.dict() == mock_events
