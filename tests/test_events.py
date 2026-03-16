from typing import Union

import pytest

from tests.utils.fixtures.mock_event import MockEvent
from tests.utils.syncify import syncify
from workos.events import AsyncEvents, Events, EventsListResource
from workos.types.events import OrganizationMembershipCreatedEvent
from workos.types.events.event import (
    VaultDataCreatedEvent,
    VaultDataDeletedEvent,
    VaultDataReadEvent,
    VaultDataUpdatedEvent,
    VaultDekDecryptedEvent,
    VaultDekReadEvent,
    VaultKekCreatedEvent,
    VaultMetadataReadEvent,
    VaultNamesListedEvent,
)


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

    def test_list_events_organization_membership_missing_custom_attributes(
        self,
        module_instance: Union[Events, AsyncEvents],
        capture_and_mock_http_client_request,
    ):
        mock_response = {
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
                        "organization_name": "Foo Corp",
                        "role": {"slug": "member"},
                        "status": "active",
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

        capture_and_mock_http_client_request(
            http_client=module_instance._http_client,
            status_code=200,
            response_dict=mock_response,
        )

        events: EventsListResource = syncify(
            module_instance.list_events(events=["organization_membership.created"])
        )

        event = events.data[0]
        assert isinstance(event, OrganizationMembershipCreatedEvent)
        assert event.data.custom_attributes == {}

    def test_list_events_organization_membership_missing_organization_name(
        self,
        module_instance: Union[Events, AsyncEvents],
        capture_and_mock_http_client_request,
    ):
        mock_response = {
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

        capture_and_mock_http_client_request(
            http_client=module_instance._http_client,
            status_code=200,
            response_dict=mock_response,
        )

        events: EventsListResource = syncify(
            module_instance.list_events(events=["organization_membership.created"])
        )

        event = events.data[0]
        assert isinstance(event, OrganizationMembershipCreatedEvent)
        assert event.data.organization_name is None
        assert event.data.custom_attributes == {}

    def test_list_events_vault_data_created(
        self,
        module_instance: Union[Events, AsyncEvents],
        capture_and_mock_http_client_request,
    ):
        mock_response = {
            "object": "list",
            "data": [
                {
                    "object": "event",
                    "id": "event_vault_01",
                    "event": "vault.data.created",
                    "data": {
                        "actor_id": "user_01234",
                        "actor_source": "dashboard",
                        "actor_name": "Test User",
                        "kv_name": "my-secret",
                        "key_id": "key_01234",
                        "key_context": {"env": "production"},
                    },
                    "created_at": "2024-01-01T00:00:00.000Z",
                }
            ],
            "list_metadata": {
                "after": None,
            },
        }

        capture_and_mock_http_client_request(
            http_client=module_instance._http_client,
            status_code=200,
            response_dict=mock_response,
        )

        events: EventsListResource = syncify(
            module_instance.list_events(events=["vault.data.created"])
        )

        event = events.data[0]
        assert isinstance(event, VaultDataCreatedEvent)
        assert event.data.actor_id == "user_01234"
        assert event.data.actor_source == "dashboard"
        assert event.data.actor_name == "Test User"
        assert event.data.kv_name == "my-secret"
        assert event.data.key_id == "key_01234"
        assert event.data.key_context.root == {"env": "production"}

    def test_list_events_vault_dek_read(
        self,
        module_instance: Union[Events, AsyncEvents],
        capture_and_mock_http_client_request,
    ):
        mock_response = {
            "object": "list",
            "data": [
                {
                    "object": "event",
                    "id": "event_vault_02",
                    "event": "vault.dek.read",
                    "data": {
                        "actor_id": "user_01234",
                        "actor_source": "api",
                        "actor_name": "API Client",
                        "key_ids": ["key_01", "key_02"],
                        "key_context": {"tenant": "acme"},
                    },
                    "created_at": "2024-01-01T00:00:00.000Z",
                }
            ],
            "list_metadata": {
                "after": None,
            },
        }

        capture_and_mock_http_client_request(
            http_client=module_instance._http_client,
            status_code=200,
            response_dict=mock_response,
        )

        events: EventsListResource = syncify(
            module_instance.list_events(events=["vault.dek.read"])
        )

        event = events.data[0]
        assert isinstance(event, VaultDekReadEvent)
        assert event.data.key_ids == ["key_01", "key_02"]
        assert event.data.key_context is not None
        assert event.data.key_context.root == {"tenant": "acme"}
        assert event.data.actor_name == "API Client"

    def test_list_events_vault_names_listed(
        self,
        module_instance: Union[Events, AsyncEvents],
        capture_and_mock_http_client_request,
    ):
        mock_response = {
            "object": "list",
            "data": [
                {
                    "object": "event",
                    "id": "event_vault_03",
                    "event": "vault.names.listed",
                    "data": {
                        "actor_id": "user_01234",
                        "actor_source": "api",
                        "actor_name": "Service Account",
                    },
                    "created_at": "2024-01-01T00:00:00.000Z",
                }
            ],
            "list_metadata": {
                "after": None,
            },
        }

        capture_and_mock_http_client_request(
            http_client=module_instance._http_client,
            status_code=200,
            response_dict=mock_response,
        )

        events: EventsListResource = syncify(
            module_instance.list_events(events=["vault.names.listed"])
        )

        event = events.data[0]
        assert isinstance(event, VaultNamesListedEvent)
        assert event.data.actor_id == "user_01234"
        assert event.data.actor_source == "api"
        assert event.data.actor_name == "Service Account"

    def test_list_events_vault_data_read(
        self,
        module_instance: Union[Events, AsyncEvents],
        capture_and_mock_http_client_request,
    ):
        mock_response = {
            "object": "list",
            "data": [
                {
                    "object": "event",
                    "id": "event_vault_09",
                    "event": "vault.data.read",
                    "data": {
                        "actor_id": "user_01234",
                        "actor_source": "api",
                        "actor_name": "Read Service",
                        "kv_name": "db-password",
                        "key_id": "key_55",
                    },
                    "created_at": "2024-01-01T00:00:00.000Z",
                }
            ],
            "list_metadata": {"after": None},
        }

        capture_and_mock_http_client_request(
            http_client=module_instance._http_client,
            status_code=200,
            response_dict=mock_response,
        )

        events: EventsListResource = syncify(
            module_instance.list_events(events=["vault.data.read"])
        )

        event = events.data[0]
        assert isinstance(event, VaultDataReadEvent)
        assert event.data.kv_name == "db-password"
        assert event.data.key_id == "key_55"

    def test_list_events_vault_dek_decrypted(
        self,
        module_instance: Union[Events, AsyncEvents],
        capture_and_mock_http_client_request,
    ):
        mock_response = {
            "object": "list",
            "data": [
                {
                    "object": "event",
                    "id": "event_vault_04",
                    "event": "vault.dek.decrypted",
                    "data": {
                        "actor_id": "user_01234",
                        "actor_source": "api",
                        "actor_name": "Decryption Service",
                        "key_id": "key_99",
                    },
                    "created_at": "2024-01-01T00:00:00.000Z",
                }
            ],
            "list_metadata": {"after": None},
        }

        capture_and_mock_http_client_request(
            http_client=module_instance._http_client,
            status_code=200,
            response_dict=mock_response,
        )

        events: EventsListResource = syncify(
            module_instance.list_events(events=["vault.dek.decrypted"])
        )

        event = events.data[0]
        assert isinstance(event, VaultDekDecryptedEvent)
        assert event.data.key_id == "key_99"
        assert event.data.actor_name == "Decryption Service"

    def test_list_events_vault_kek_created(
        self,
        module_instance: Union[Events, AsyncEvents],
        capture_and_mock_http_client_request,
    ):
        mock_response = {
            "object": "list",
            "data": [
                {
                    "object": "event",
                    "id": "event_vault_05",
                    "event": "vault.kek.created",
                    "data": {
                        "actor_id": "user_01234",
                        "actor_source": "dashboard",
                        "actor_name": "Admin",
                        "key_name": "production-kek",
                        "key_id": "kek_01",
                    },
                    "created_at": "2024-01-01T00:00:00.000Z",
                }
            ],
            "list_metadata": {"after": None},
        }

        capture_and_mock_http_client_request(
            http_client=module_instance._http_client,
            status_code=200,
            response_dict=mock_response,
        )

        events: EventsListResource = syncify(
            module_instance.list_events(events=["vault.kek.created"])
        )

        event = events.data[0]
        assert isinstance(event, VaultKekCreatedEvent)
        assert event.data.key_name == "production-kek"
        assert event.data.key_id == "kek_01"

    def test_list_events_vault_data_deleted(
        self,
        module_instance: Union[Events, AsyncEvents],
        capture_and_mock_http_client_request,
    ):
        mock_response = {
            "object": "list",
            "data": [
                {
                    "object": "event",
                    "id": "event_vault_06",
                    "event": "vault.data.deleted",
                    "data": {
                        "actor_id": "user_01234",
                        "actor_source": "api",
                        "actor_name": "Cleanup Job",
                        "kv_name": "old-secret",
                    },
                    "created_at": "2024-01-01T00:00:00.000Z",
                }
            ],
            "list_metadata": {"after": None},
        }

        capture_and_mock_http_client_request(
            http_client=module_instance._http_client,
            status_code=200,
            response_dict=mock_response,
        )

        events: EventsListResource = syncify(
            module_instance.list_events(events=["vault.data.deleted"])
        )

        event = events.data[0]
        assert isinstance(event, VaultDataDeletedEvent)
        assert event.data.kv_name == "old-secret"

    def test_list_events_vault_data_updated(
        self,
        module_instance: Union[Events, AsyncEvents],
        capture_and_mock_http_client_request,
    ):
        mock_response = {
            "object": "list",
            "data": [
                {
                    "object": "event",
                    "id": "event_vault_07",
                    "event": "vault.data.updated",
                    "data": {
                        "actor_id": "user_01234",
                        "actor_source": "api",
                        "actor_name": "Rotation Job",
                        "kv_name": "api-key",
                        "key_id": "key_02",
                        "key_context": {"env": "staging"},
                    },
                    "created_at": "2024-01-01T00:00:00.000Z",
                }
            ],
            "list_metadata": {"after": None},
        }

        capture_and_mock_http_client_request(
            http_client=module_instance._http_client,
            status_code=200,
            response_dict=mock_response,
        )

        events: EventsListResource = syncify(
            module_instance.list_events(events=["vault.data.updated"])
        )

        event = events.data[0]
        assert isinstance(event, VaultDataUpdatedEvent)
        assert event.data.kv_name == "api-key"
        assert event.data.key_id == "key_02"

    def test_list_events_vault_metadata_read(
        self,
        module_instance: Union[Events, AsyncEvents],
        capture_and_mock_http_client_request,
    ):
        mock_response = {
            "object": "list",
            "data": [
                {
                    "object": "event",
                    "id": "event_vault_08",
                    "event": "vault.metadata.read",
                    "data": {
                        "actor_id": "user_01234",
                        "actor_source": "api",
                        "actor_name": "Audit Service",
                        "kv_name": "config-store",
                    },
                    "created_at": "2024-01-01T00:00:00.000Z",
                }
            ],
            "list_metadata": {"after": None},
        }

        capture_and_mock_http_client_request(
            http_client=module_instance._http_client,
            status_code=200,
            response_dict=mock_response,
        )

        events: EventsListResource = syncify(
            module_instance.list_events(events=["vault.metadata.read"])
        )

        event = events.data[0]
        assert isinstance(event, VaultMetadataReadEvent)
        assert event.data.kv_name == "config-store"
