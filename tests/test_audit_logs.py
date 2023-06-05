from datetime import datetime
import json
from requests import Response

import pytest

import workos
from workos.audit_logs import AuditLogs
from workos.exceptions import AuthenticationException, BadRequestException
from workos.resources.audit_logs_export import WorkOSAuditLogExport


class _TestSetup:
    @pytest.fixture(autouse=True)
    def setup(self, set_api_key):
        self.audit_logs = AuditLogs()


class TestAuditLogs:
    class TestCreateEvent(_TestSetup):
        def test_succeeds(self, capture_and_mock_request):
            organization_id = "org_123456789"

            event = {
                "action": "document.updated",
                "occurred_at": datetime.now().isoformat(),
                "actor": {
                    "id": "user_1",
                    "name": "Jon Smith",
                    "type": "user",
                },
                "targets": [
                    {
                        "id": "document_39127",
                        "type": "document",
                    },
                ],
                "context": {
                    "location": "192.0.0.8",
                    "user_agent": "Firefox",
                },
                "metadata": {
                    "successful": True,
                },
            }

            _, request_kwargs = capture_and_mock_request("post", {"success": True}, 200)

            response = self.audit_logs.create_event(
                organization_id, event, "test_123456"
            )

            assert request_kwargs["json"] == {
                "organization_id": organization_id,
                "event": event,
            }
            assert response is None

        def test_sends_idempotency_key(self, capture_and_mock_request):
            idempotency_key = "test_123456789"

            organization_id = "org_123456789"

            event = {
                "action": "document.updated",
                "occurred_at": datetime.now().isoformat(),
                "actor": {
                    "id": "user_1",
                    "name": "Jon Smith",
                    "type": "user",
                },
                "targets": [
                    {
                        "id": "document_39127",
                        "type": "document",
                    },
                ],
                "context": {
                    "location": "192.0.0.8",
                    "user_agent": "Firefox",
                },
                "metadata": {
                    "successful": True,
                },
            }

            _, request_kwargs = capture_and_mock_request("post", {"success": True}, 200)

            response = self.audit_logs.create_event(
                organization_id, event, idempotency_key
            )

            assert request_kwargs["headers"]["idempotency-key"] == idempotency_key
            assert response is None

        def test_throws_unauthorized_excpetion(self, mock_request_method):
            organization_id = "org_123456789"
            event = {"any_event": "event"}

            mock_request_method(
                "post",
                {"message": "Unauthorized"},
                401,
                {"X-Request-ID": "a-request-id"},
            )

            with pytest.raises(AuthenticationException) as excinfo:
                self.audit_logs.create_event(organization_id, event)
            assert "(message=Unauthorized, request_id=a-request-id)" == str(
                excinfo.value
            )

        def test_throws_badrequest_excpetion(self, mock_request_method):
            organization_id = "org_123456789"
            event = {"any_event": "any_event"}

            mock_request_method(
                "post",
                {
                    "message": "Audit Log could not be processed due to missing or incorrect data.",
                    "code": "invalid_audit_log",
                    "errors": ["error in a field"],
                },
                400,
            )

            with pytest.raises(BadRequestException) as excinfo:
                self.audit_logs.create_event(organization_id, event)
                assert excinfo.code == "invalid_audit_log"
                assert excinfo.errors == ["error in a field"]
                assert (
                    excinfo.message
                    == "Audit Log could not be processed due to missing or incorrect data."
                )

    class TestCreateExport(_TestSetup):
        def test_succeeds(self, mock_request_method):
            organization_id = "org_123456789"
            range_start = datetime.now().isoformat
            range_end = datetime.now().isoformat

            expected_payload = {
                "object": "audit_log_export",
                "id": "audit_log_export_1234",
                "state": "pending",
                "url": None,
                "created_at": datetime.now().isoformat,
                "updated_at": datetime.now().isoformat,
            }

            mock_request_method("post", expected_payload, 201)

            response = self.audit_logs.create_export(
                organization_id, range_start, range_end
            )

            assert (
                response.to_dict()
                == WorkOSAuditLogExport.construct_from_response(
                    expected_payload
                ).to_dict()
            )

        def test_succeeds_with_additional_filters(self, mock_request_method):
            organization_id = "org_123456789"
            range_start = datetime.now().isoformat
            range_end = datetime.now().isoformat
            actions = ["foo", "bar"]
            actors = ["Jon", "Smith"]
            actor_names = ["Jon", "Smith"]
            actor_ids = ["user_foo", "user_bar"]
            targets = ["user", "team"]

            expected_payload = {
                "object": "audit_log_export",
                "id": "audit_log_export_1234",
                "state": "pending",
                "url": None,
                "created_at": datetime.now().isoformat,
                "updated_at": datetime.now().isoformat,
            }

            mock_request_method("post", expected_payload, 201)

            response = self.audit_logs.create_export(
                actions=actions,
                actors=actors,
                organization=organization_id,
                range_end=range_end,
                range_start=range_start,
                targets=targets,
                actor_names=actor_names,
                actor_ids=actor_ids,
            )

            assert (
                response.to_dict()
                == WorkOSAuditLogExport.construct_from_response(
                    expected_payload
                ).to_dict()
            )

        def test_throws_unauthorized_excpetion(self, mock_request_method):
            organization_id = "org_123456789"
            range_start = datetime.now().isoformat
            range_end = datetime.now().isoformat

            mock_request_method(
                "post",
                {"message": "Unauthorized"},
                401,
                {"X-Request-ID": "a-request-id"},
            )

            with pytest.raises(AuthenticationException) as excinfo:
                self.audit_logs.create_export(organization_id, range_start, range_end)
            assert "(message=Unauthorized, request_id=a-request-id)" == str(
                excinfo.value
            )

    class TestGetExport(_TestSetup):
        def test_succeeds(self, mock_request_method):
            expected_payload = {
                "object": "audit_log_export",
                "id": "audit_log_export_1234",
                "state": "pending",
                "url": None,
                "created_at": datetime.now().isoformat,
                "updated_at": datetime.now().isoformat,
            }

            mock_request_method("get", expected_payload, 200)

            response = self.audit_logs.get_export(
                expected_payload["id"],
            )

            assert (
                response.to_dict()
                == WorkOSAuditLogExport.construct_from_response(
                    expected_payload
                ).to_dict()
            )

        def test_throws_unauthorized_excpetion(self, mock_request_method):
            mock_request_method(
                "get",
                {"message": "Unauthorized"},
                401,
                {"X-Request-ID": "a-request-id"},
            )

            with pytest.raises(AuthenticationException) as excinfo:
                self.audit_logs.get_export("audit_log_export_1234")

            assert "(message=Unauthorized, request_id=a-request-id)" == str(
                excinfo.value
            )
