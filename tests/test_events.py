import pytest
from workos.events import Events
from tests.utils.fixtures.mock_event import MockEvent


class TestEvents(object):
    @pytest.fixture(autouse=True)
    def setup(self, set_api_key, set_client_id):
        self.events = Events()

    @pytest.fixture
    def mock_events(self):
        events = [MockEvent(id=str(i)).to_dict() for i in range(100)]

        return {
            "data": events,
            "list_metadata": {"after": None},
            "metadata": {
                "params": {
                    "events": None,
                    "limit": None,
                    "after": None,
                    "rangeStart": None,
                    "rangeEnd": None,
                    "default_limit": True,
                },
                "method": Events.get_events,
            },
        }

    def test_get_events(self, mock_events, mock_request_method):
        mock_request_method("get", mock_events, 200)

        events = self.events.get_events()

        assert events == mock_events

    def test_get_events_returns_metadata(self, mock_events, mock_request_method):
        mock_request_method("get", mock_events, 200)

        events = self.events.get_events(
            events=["dsync.user.created"],
        )

        assert events["metadata"]["params"]["events"] == ["dsync.user.created"]
