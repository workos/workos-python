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
            "data": events,
            "metadata": {
                "params": {
                    "events": ["dsync.user.created"],
                    "limit": 10,
                    "organization_id": None,
                    "after": None,
                    "range_start": None,
                    "range_end": None,
                },
                "method": Events.list_events,
            },
        }

    def test_list_events(self, mock_events, mock_http_client_with_response):
        mock_http_client_with_response(
            http_client=self.http_client,
            status_code=200,
            response_dict={"data": mock_events["data"]},
        )

        events = self.events.list_events(events=["dsync.user.created"])

        assert events == mock_events

    def test_list_events_returns_metadata(
        self, mock_events, mock_http_client_with_response
    ):
        mock_http_client_with_response(
            http_client=self.http_client,
            status_code=200,
            response_dict={"data": mock_events["data"]},
        )

        events = self.events.list_events(
            events=["dsync.user.created"],
        )

        assert events["metadata"]["params"]["events"] == ["dsync.user.created"]

    def test_list_events_with_organization_id_returns_metadata(
        self, mock_events, mock_http_client_with_response
    ):
        mock_http_client_with_response(
            http_client=self.http_client,
            status_code=200,
            response_dict={"data": mock_events["data"]},
        )

        events = self.events.list_events(
            events=["dsync.user.created"],
            organization_id="org_1234",
        )

        assert events["metadata"]["params"]["organization_id"] == "org_1234"
        assert events["metadata"]["params"]["events"] == ["dsync.user.created"]


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
            "data": events,
            "metadata": {
                "params": {
                    "events": ["dsync.user.created"],
                    "limit": 10,
                    "organization_id": None,
                    "after": None,
                    "range_start": None,
                    "range_end": None,
                },
                "method": AsyncEvents.list_events,
            },
        }

    async def test_list_events(self, mock_events, mock_http_client_with_response):
        mock_http_client_with_response(
            http_client=self.http_client,
            status_code=200,
            response_dict={"data": mock_events["data"]},
        )

        events = await self.events.list_events(events=["dsync.user.created"])

        assert events == mock_events

    async def test_list_events_returns_metadata(
        self, mock_events, mock_http_client_with_response
    ):
        mock_http_client_with_response(
            http_client=self.http_client,
            status_code=200,
            response_dict={"data": mock_events["data"]},
        )

        events = await self.events.list_events(
            events=["dsync.user.created"],
        )

        assert events["metadata"]["params"]["events"] == ["dsync.user.created"]

    async def test_list_events_with_organization_id_returns_metadata(
        self, mock_events, mock_http_client_with_response
    ):
        mock_http_client_with_response(
            http_client=self.http_client,
            status_code=200,
            response_dict={"data": mock_events["data"]},
        )

        events = await self.events.list_events(
            events=["dsync.user.created"],
            organization_id="org_1234",
        )

        assert events["metadata"]["params"]["organization_id"] == "org_1234"
        assert events["metadata"]["params"]["events"] == ["dsync.user.created"]
