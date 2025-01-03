from datetime import datetime

import pytest

from workos.audit_logs import AuditLogEvent, AuditLogs
from workos.exceptions import AuthenticationException, BadRequestException


class _TestSetup:
    @pytest.fixture(autouse=True)
    def setup(self, sync_http_client_for_test):
        self.http_client = sync_http_client_for_test
        self.audit_logs = AuditLogs(http_client=self.http_client)

    @pytest.fixture
    def mock_audit_log_event(self) -> AuditLogEvent:
        return {
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


class TestAuditLogs:
    class TestCreateEvent(_TestSetup):
        def test_succeeds(self, capture_and_mock_http_client_request):
            organization_id = "org_123456789"

            event: AuditLogEvent = {
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

            request_kwargs = capture_and_mock_http_client_request(
                http_client=self.http_client,
                response_dict={"success": True},
                status_code=200,
            )

            response = self.audit_logs.create_event(
                organization_id=organization_id,
                event=event,
                idempotency_key="test_123456",
            )

            assert request_kwargs["url"].endswith("/audit_logs/events")
            assert request_kwargs["method"] == "post"
            assert request_kwargs["json"] == {
                "organization_id": organization_id,
                "event": event,
            }
            assert response is None

        def test_sends_idempotency_key(
            self, mock_audit_log_event, capture_and_mock_http_client_request
        ):
            idempotency_key = "test_123456789"

            organization_id = "org_123456789"

            request_kwargs = capture_and_mock_http_client_request(
                self.http_client, {"success": True}, 200
            )

            response = self.audit_logs.create_event(
                organization_id=organization_id,
                event=mock_audit_log_event,
                idempotency_key=idempotency_key,
            )

            assert request_kwargs["headers"]["idempotency-key"] == idempotency_key
            assert response is None

        def test_throws_unauthorized_exception(
            self, mock_audit_log_event, mock_http_client_with_response
        ):
            organization_id = "org_123456789"

            mock_http_client_with_response(
                self.http_client,
                {"message": "Unauthorized"},
                401,
                {"X-Request-ID": "a-request-id"},
            )

            with pytest.raises(AuthenticationException) as excinfo:
                self.audit_logs.create_event(
                    organization_id=organization_id, event=mock_audit_log_event
                )
            assert "(message=Unauthorized, request_id=a-request-id)" == str(
                excinfo.value
            )

        def test_throws_badrequest_excpetion(
            self, mock_audit_log_event, mock_http_client_with_response
        ):
            organization_id = "org_123456789"

            mock_http_client_with_response(
                self.http_client,
                {
                    "message": "Audit Log could not be processed due to missing or incorrect data.",
                    "code": "invalid_audit_log",
                    "errors": ["error in a field"],
                },
                400,
            )

            with pytest.raises(BadRequestException) as excinfo:
                self.audit_logs.create_event(
                    organization_id=organization_id, event=mock_audit_log_event
                )
                assert excinfo.code == "invalid_audit_log"
                assert excinfo.errors == ["error in a field"]
                assert (
                    excinfo.message
                    == "Audit Log could not be processed due to missing or incorrect data."
                )

    class TestCreateExport(_TestSetup):
        def test_succeeds(self, mock_http_client_with_response):
            organization_id = "org_123456789"
            now = datetime.now().isoformat()
            range_start = now
            range_end = now

            expected_payload = {
                "object": "audit_log_export",
                "id": "audit_log_export_1234",
                "state": "pending",
                "url": None,
                "created_at": now,
                "updated_at": now,
            }

            mock_http_client_with_response(self.http_client, expected_payload, 201)

            response = self.audit_logs.create_export(
                organization_id=organization_id,
                range_start=range_start,
                range_end=range_end,
            )

            assert response.dict() == expected_payload

        def test_succeeds_with_additional_filters(
            self, capture_and_mock_http_client_request
        ):
            now = datetime.now().isoformat()
            organization_id = "org_123456789"
            range_start = now
            range_end = now
            actions = ["foo", "bar"]
            actor_names = ["Jon", "Smith"]
            actor_ids = ["user_foo", "user_bar"]
            targets = ["user", "team"]

            expected_payload = {
                "object": "audit_log_export",
                "id": "audit_log_export_1234",
                "state": "pending",
                "url": None,
                "created_at": now,
                "updated_at": now,
            }

            request_kwargs = capture_and_mock_http_client_request(
                self.http_client, expected_payload, 201
            )

            response = self.audit_logs.create_export(
                actions=actions,
                organization_id=organization_id,
                range_end=range_end,
                range_start=range_start,
                targets=targets,
                actor_names=actor_names,
                actor_ids=actor_ids,
            )

            assert request_kwargs["url"].endswith("/audit_logs/exports")
            assert request_kwargs["method"] == "post"
            assert request_kwargs["json"] == {
                "actions": actions,
                "organization_id": organization_id,
                "range_end": range_end,
                "range_start": range_start,
                "targets": targets,
                "actor_names": actor_names,
                "actor_ids": actor_ids,
            }
            assert response.dict() == expected_payload

        def test_throws_unauthorized_excpetion(self, mock_http_client_with_response):
            organization_id = "org_123456789"
            range_start = datetime.now().isoformat()
            range_end = datetime.now().isoformat()

            mock_http_client_with_response(
                self.http_client,
                {"message": "Unauthorized"},
                401,
                {"X-Request-ID": "a-request-id"},
            )

            with pytest.raises(AuthenticationException) as excinfo:
                self.audit_logs.create_export(
                    organization_id=organization_id,
                    range_start=range_start,
                    range_end=range_end,
                )
            assert "(message=Unauthorized, request_id=a-request-id)" == str(
                excinfo.value
            )

    class TestGetExport(_TestSetup):
        def test_succeeds(self, capture_and_mock_http_client_request):
            now = datetime.now().isoformat()
            expected_payload = {
                "object": "audit_log_export",
                "id": "audit_log_export_1234",
                "state": "pending",
                "url": None,
                "created_at": now,
                "updated_at": now,
            }

            request_kwargs = capture_and_mock_http_client_request(
                self.http_client, expected_payload, 200
            )

            response = self.audit_logs.get_export(
                expected_payload["id"],
            )

            assert request_kwargs["url"].endswith(
                "/audit_logs/exports/audit_log_export_1234"
            )
            assert request_kwargs["method"] == "get"
            assert response.dict() == expected_payload

        def test_throws_unauthorized_excpetion(self, mock_http_client_with_response):
            mock_http_client_with_response(
                self.http_client,
                {"message": "Unauthorized"},
                401,
                {"X-Request-ID": "a-request-id"},
            )

            with pytest.raises(AuthenticationException) as excinfo:
                self.audit_logs.get_export("audit_log_export_1234")

            assert "(message=Unauthorized, request_id=a-request-id)" == str(
                excinfo.value
            )
