from datetime import datetime
import json
from requests import Response

import pytest

import workos
from workos.audit_trail import AuditTrail


class TestAuditTrail(object):
    @pytest.fixture(autouse=True)
    def setup(self, set_api_key_and_environment_id):
        self.audit_trail = AuditTrail()

    def test_create_audit_trail_event_succeeds(self, mock_request_method):
        event = {
            "group": "Terrace House",
            "location": "1.1.1.1",
            "action": "house.created",
            "action_type": "C",
            "actor_name": "Daiki Miyagi",
            "actor_id": "user_12345",
            "target_name": "Ryota Yamasato",
            "target_id": "user_67890",
            "occurred_at": datetime.now().isoformat(),
            "metadata": {"a": "b"},
        }
        mock_response = Response()
        mock_response.status_code = 200
        mock_request_method("post", mock_response, 200)

        result = self.audit_trail.create_event(event)
        assert result == True

    def test_create_audit_trail_event_fails_with_long_metadata(self):
        with pytest.raises(ValueError, match=r"Number of metadata keys exceeds .*"):
            metadata = {str(num): num for num in range(51)}
            event = {
                "group": "Terrace House",
                "location": "1.1.1.1",
                "action": "house.created",
                "action_type": "C",
                "actor_name": "Daiki Miyagi",
                "actor_id": "user_12345",
                "target_name": "Ryota Yamasato",
                "target_id": "user_67890",
                "occurred_at": datetime.utcnow().isoformat(),
                "metadata": metadata,
            }
            self.audit_trail.create_event(event)

    def test_get_events_succeeds(self, mock_request_method):
        event = {
            "id": "evt_123",
            "group": "Terrace House",
            "location": "1.1.1.1",
            "latitude": None,
            "longitude": None,
            "action": {
                "id": "evt_action_123",
                "name": "house.created",
                "environment_id": "environment_123",
            },
            "type": "C",
            "actor_name": "Daiki Miyagi",
            "actor_id": "user_12345",
            "target_name": "Ryota Yamasato",
            "target_id": "user_67890",
            "occurred_at": datetime.now().isoformat(),
            "metadata": {"a": "b"},
        }

        response = {
            "data": [
                event,
            ],
            "listMetadata": {
                "before": None,
                "after": None,
            },
        }
        mock_request_method("get", response, 200)

        events, before, after = self.audit_trail.get_events()
        assert events[0].to_dict() == event

    def test_get_events_correctly_includes_occured_at_filter(
        self, capture_and_mock_request
    ):
        event = {
            "id": "evt_123",
            "group": "Terrace House",
            "location": "1.1.1.1",
            "latitude": None,
            "longitude": None,
            "action": {
                "id": "evt_action_123",
                "name": "house.created",
                "environment_id": "environment_123",
            },
            "type": "C",
            "actor_name": "Daiki Miyagi",
            "actor_id": "user_12345",
            "target_name": "Ryota Yamasato",
            "target_id": "user_67890",
            "occurred_at": datetime.now().isoformat(),
            "metadata": {"a": "b"},
        }

        response = {
            "data": [
                event,
            ],
            "listMetadata": {
                "before": None,
                "after": None,
            },
        }
        request_args, request_kwargs = capture_and_mock_request("get", response, 200)

        self.audit_trail.get_events(
            occurred_at=datetime.now(),
            occurred_at_gte=datetime.now(),
            occurred_at_gt=datetime.now(),
            occurred_at_lte=datetime.now,
            occurred_at_lt=datetime.now(),
        )

        request_params = request_kwargs["params"]
        assert "occurred_at" in request_params
        assert "occurred_at_gte" not in request_params
        assert "occurred_at_gt" not in request_params
        assert "occurred_at_lte" not in request_params
        assert "occurred_at_lt" not in request_params

    def test_get_events_correctly_includes_occurred_at_gte(
        self, capture_and_mock_request
    ):
        event = {
            "id": "evt_123",
            "group": "Terrace House",
            "location": "1.1.1.1",
            "latitude": None,
            "longitude": None,
            "action": {
                "id": "evt_action_123",
                "name": "house.created",
                "environment_id": "environment_123",
            },
            "type": "C",
            "actor_name": "Daiki Miyagi",
            "actor_id": "user_12345",
            "target_name": "Ryota Yamasato",
            "target_id": "user_67890",
            "occurred_at": datetime.now().isoformat(),
            "metadata": {"a": "b"},
        }

        response = {
            "data": [
                event,
            ],
            "listMetadata": {
                "before": None,
                "after": None,
            },
        }
        request_args, request_kwargs = capture_and_mock_request("get", response, 200)

        self.audit_trail.get_events(
            occurred_at_gte=datetime.now(),
            occurred_at_gt=datetime.now(),
        )

        request_params = request_kwargs["params"]
        assert "occurred_at_gte" in request_params
        assert "occurred_at_gt" not in request_params

    def test_get_events_correctly_includes_occured_at_lte(
        self, capture_and_mock_request
    ):
        event = {
            "id": "evt_123",
            "group": "Terrace House",
            "location": "1.1.1.1",
            "latitude": None,
            "longitude": None,
            "action": {
                "id": "evt_action_123",
                "name": "house.created",
                "environment_id": "environment_123",
            },
            "type": "C",
            "actor_name": "Daiki Miyagi",
            "actor_id": "user_12345",
            "target_name": "Ryota Yamasato",
            "target_id": "user_67890",
            "occurred_at": datetime.now().isoformat(),
            "metadata": {"a": "b"},
        }

        response = {
            "data": [
                event,
            ],
            "listMetadata": {
                "before": None,
                "after": None,
            },
        }
        request_args, request_kwargs = capture_and_mock_request("get", response, 200)

        self.audit_trail.get_events(
            occurred_at_lte=datetime.now, occurred_at_lt=datetime.now()
        )

        request_params = request_kwargs["params"]
        assert "occurred_at_lte" in request_params
        assert "occurred_at_lt" not in request_params
