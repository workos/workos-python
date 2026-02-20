from typing import Union
import pytest

from tests.utils.fixtures.mock_event import MockEvent
from tests.utils.syncify import syncify
from workos.events import AsyncEvents, Events, EventsListResource
from workos.types.events import OrganizationMembershipCreatedEvent


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

    @pytest.fixture
    def mock_organization_membership_event_with_null_custom_attributes(self):
        return {
            "object": "list",
            "data": [
                {
                    "object": "event",
                    "id": "event_01234",
                    "event": "organization_membership.created",
                    "data": {
                        "object": "organization_membership",
                        "id": "om_01234",
                        "user_id": "user_01234",
                        "organization_id": "org_01234",
                        "role": {"slug": "member"},
                        "status": "active",
                        "custom_attributes": None,
                        "created_at": "2024-01-01T00:00:00.000Z",
                        "updated_at": "2024-01-01T00:00:00.000Z",
                    },
                    "created_at": "2024-01-01T00:00:00.000Z",
                }
            ],
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

    def test_list_events_organization_membership_null_custom_attributes(
        self,
        module_instance: Union[Events, AsyncEvents],
        mock_organization_membership_event_with_null_custom_attributes,
        capture_and_mock_http_client_request,
    ):
        capture_and_mock_http_client_request(
            http_client=module_instance._http_client,
            status_code=200,
            response_dict=mock_organization_membership_event_with_null_custom_attributes,
        )

        events: EventsListResource = syncify(
            module_instance.list_events(
                events=["organization_membership.created"]
            )
        )

        event = events.data[0]
        assert isinstance(event, OrganizationMembershipCreatedEvent)
        assert event.data.custom_attributes == {}
