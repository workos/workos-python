from datetime import datetime
import json
from unittest.mock import Mock
from requests import Response

import pytest

import workos
from workos.audit_logs import AuditLogs
from workos.exceptions import AuthenticationException, BadRequestException


class TestAuditLogs(object):
    @pytest.fixture(autouse=True)
    def setup(self, set_api_key):
        self.audit_logs = AuditLogs()

    def test_create_audit_logs_event_succeeds(self, capture_and_mock_request):
        organization_id = "org_123456789"

        event = {
            "action": 'document.updated',
            "occurred_at": datetime.now().isoformat(),
            "actor": {
                "id": "user_1",
                "name": "Jon Smith",
                "type": "user",
            },
            "targets": [
                {
                    "id": 'document_39127',
                    "type": 'document',
                },
            ],
            "context": {
                "location": "192.0.0.8",
                "user_agent": "Firefox",
            },
            "metadata": {
                "successful": True,
            }
        }
        
        _, request_kwargs = capture_and_mock_request("post", {"success": True}, 200)

        response = self.audit_logs.create_event(
            organization_id, event, "test_123456")

        assert request_kwargs["json"] == {"organization_id": organization_id, "event": event}
        assert response == True

    def test_create_audit_logs_event_sends_idempotency_key(self, capture_and_mock_request):
        idempotency_key = "test_123456789"

        organization_id = "org_123456789"

        event = {
            "action": 'document.updated',
            "occurred_at": datetime.now().isoformat(),
            "actor": {
                "id": "user_1",
                "name": "Jon Smith",
                "type": "user",
            },
            "targets": [
                {
                    "id": 'document_39127',
                    "type": 'document',
                },
            ],
            "context": {
                "location": "192.0.0.8",
                "user_agent": "Firefox",
            },
            "metadata": {
                "successful": True,
            }
        }
        
        _, request_kwargs = capture_and_mock_request("post", {"success": True}, 200)

        response = self.audit_logs.create_event(
            organization_id, event, idempotency_key)

        assert request_kwargs["headers"]["idempotency-key"] == idempotency_key
        assert response == True


    def test_create_audit_logs_event_throws_unauthorized_excpetion(self, capture_and_mock_request):
            organization_id = "org_123456789"
            event = {
                "any_event": "event"
            }
            
            _, request_kwargs = capture_and_mock_request("post", {"message": "Unauthorized"}, 401)
            
            with pytest.raises(AuthenticationException) as excinfo:
                self.audit_logs.create_event(
                    organization_id, event)
            assert '(message=Unauthorized)' == str(excinfo.value)


    def test_create_audit_logs_event_throws_badrequest_excpetion(self, mock_request_method):
        organization_id = "org_123456789"
        event = {
            "any_event": "any_event"
        }

        mock_request_method("post", {"message": "Audit Log could not be processed due to missing or incorrect data.",
                                     "code": "invalid_audit_log"}, 400)

        with pytest.raises(BadRequestException) as excinfo:
            self.audit_logs.create_event(
                organization_id, event)
        assert '(message=Audit Log could not be processed due to missing or incorrect data.)' == str(excinfo.value)
