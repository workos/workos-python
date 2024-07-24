import pytest

from tests.utils.fixtures.mock_event import MockEvent
from workos.events import AsyncEvents, Events
from workos.utils.http_client import AsyncHTTPClient, SyncHTTPClient


class TestEvents(object):
    @pytest.fixture(autouse=True)
    def setup(
        self,
        set_api_key,
        set_client_id,
    ):
        self.http_client = SyncHTTPClient(
            base_url="https://api.workos.test", version="test"
        )
        self.events = Events(http_client=self.http_client)

    @pytest.fixture
    def mock_events(self):
        events = [MockEvent(id=str(i)).to_dict() for i in range(10)]

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
    def setup(
        self,
        set_api_key,
        set_client_id,
    ):
        self.http_client = AsyncHTTPClient(
            base_url="https://api.workos.test", version="test"
        )
        self.events = AsyncEvents(http_client=self.http_client)

    @pytest.fixture
    def mock_events(self):
        events = [MockEvent(id=str(i)).to_dict() for i in range(10)]

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
