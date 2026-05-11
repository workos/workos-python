# @oagen-ignore-file

"""Client tests: retries, errors, context manager, idempotency."""

import httpx
import pytest

from workos import WorkOSClient, AsyncWorkOSClient
from workos import _base_client as generated_client_module
from workos._errors import (
    AuthenticationError,
    AuthenticationFlowError,
    AuthenticationMethodNotAllowedError,
    BadRequestError,
    AuthorizationError,
    EmailPasswordAuthDisabledError,
    EmailVerificationRequiredError,
    MfaChallengeError,
    MfaEnrollmentError,
    NotFoundError,
    ConflictError,
    OrganizationAuthMethodsRequiredError,
    OrganizationSelectionRequiredError,
    PasskeyProgressiveEnrollmentError,
    RadarChallengeError,
    RadarSignUpChallengeError,
    SsoRequiredError,
    UnprocessableEntityError,
    RateLimitExceededError,
    ServerError,
)


class TestWorkOSClient:
    def test_missing_credentials_raise(self):
        with pytest.raises(ValueError):
            WorkOSClient()

    def test_context_manager(self):
        with WorkOSClient(api_key="sk_test_123", client_id="client_test") as client:
            assert client._api_key == "sk_test_123"

    def test_api_key_only_initializes(self):
        client = WorkOSClient(api_key="sk_test_123")
        assert client._api_key == "sk_test_123"
        assert client.client_id is None
        client.close()

    def test_client_id_from_constructor(self):
        client = WorkOSClient(client_id="client_test_456")
        assert client.client_id == "client_test_456"
        assert client._api_key is None
        client.close()

    def test_raises_400(self, httpx_mock):
        httpx_mock.add_response(
            status_code=400,
            json={"message": "Error"},
        )
        client = WorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(BadRequestError):
            client.request("GET", ("test",))
        client.close()

    def test_raises_401(self, httpx_mock):
        httpx_mock.add_response(
            status_code=401,
            json={"message": "Error"},
        )
        client = WorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(AuthenticationError):
            client.request("GET", ("test",))
        client.close()

    def test_raises_403(self, httpx_mock):
        httpx_mock.add_response(
            status_code=403,
            json={"message": "Error"},
        )
        client = WorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(AuthorizationError):
            client.request("GET", ("test",))
        client.close()

    def test_raises_email_verification_required(self, httpx_mock):
        httpx_mock.add_response(
            status_code=403,
            json={
                "code": "email_verification_required",
                "message": "Email verification required",
                "pending_authentication_token": "pat_123",
                "email_verification_id": "ev_123",
                "email": "user@example.com",
            },
        )
        client = WorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(EmailVerificationRequiredError) as exc_info:
            client.request("GET", ("test",))
        assert exc_info.value.pending_authentication_token == "pat_123"
        assert exc_info.value.email_verification_id == "ev_123"
        assert exc_info.value.email == "user@example.com"
        client.close()

    def test_raises_mfa_enrollment(self, httpx_mock):
        httpx_mock.add_response(
            status_code=403,
            json={
                "code": "mfa_enrollment",
                "message": "MFA enrollment required",
                "pending_authentication_token": "pat_456",
                "user": {"id": "user_123", "email": "user@example.com"},
            },
        )
        client = WorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(MfaEnrollmentError) as exc_info:
            client.request("GET", ("test",))
        assert exc_info.value.pending_authentication_token == "pat_456"
        assert exc_info.value.user == {"id": "user_123", "email": "user@example.com"}
        client.close()

    def test_raises_mfa_challenge(self, httpx_mock):
        httpx_mock.add_response(
            status_code=403,
            json={
                "code": "mfa_challenge",
                "message": "MFA challenge required",
                "pending_authentication_token": "pat_789",
                "user": {"id": "user_123"},
                "authentication_factors": [{"id": "af_1", "type": "totp"}],
            },
        )
        client = WorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(MfaChallengeError) as exc_info:
            client.request("GET", ("test",))
        assert exc_info.value.pending_authentication_token == "pat_789"
        assert exc_info.value.user == {"id": "user_123"}
        assert exc_info.value.authentication_factors == [{"id": "af_1", "type": "totp"}]
        client.close()

    def test_raises_organization_selection_required(self, httpx_mock):
        httpx_mock.add_response(
            status_code=403,
            json={
                "code": "organization_selection_required",
                "message": "Organization selection required",
                "pending_authentication_token": "pat_org",
                "user": {"id": "user_123"},
                "organizations": [{"id": "org_1", "name": "Acme"}],
            },
        )
        client = WorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(OrganizationSelectionRequiredError) as exc_info:
            client.request("GET", ("test",))
        assert exc_info.value.pending_authentication_token == "pat_org"
        assert exc_info.value.organizations == [{"id": "org_1", "name": "Acme"}]
        client.close()

    def test_raises_sso_required(self, httpx_mock):
        httpx_mock.add_response(
            status_code=403,
            json={
                "error": "sso_required",
                "error_description": "SSO is required",
                "pending_authentication_token": "pat_sso",
                "email": "user@example.com",
                "connection_ids": ["conn_1", "conn_2"],
            },
        )
        client = WorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(SsoRequiredError) as exc_info:
            client.request("GET", ("test",))
        assert exc_info.value.pending_authentication_token == "pat_sso"
        assert exc_info.value.email == "user@example.com"
        assert exc_info.value.connection_ids == ["conn_1", "conn_2"]
        client.close()

    def test_raises_org_auth_methods_required(self, httpx_mock):
        httpx_mock.add_response(
            status_code=403,
            json={
                "error": "organization_authentication_methods_required",
                "error_description": "Org auth methods required",
                "pending_authentication_token": "pat_oam",
                "email": "user@example.com",
                "sso_connection_ids": ["conn_1"],
                "auth_methods": {"google_oauth": True, "password": False},
            },
        )
        client = WorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(OrganizationAuthMethodsRequiredError) as exc_info:
            client.request("GET", ("test",))
        assert exc_info.value.pending_authentication_token == "pat_oam"
        assert exc_info.value.sso_connection_ids == ["conn_1"]
        assert exc_info.value.auth_methods == {"google_oauth": True, "password": False}
        client.close()

    def test_raises_simple_auth_flow_errors(self, httpx_mock):
        """Codes with no extra fields beyond pending_authentication_token."""
        cases = [
            ("authentication_method_not_allowed", AuthenticationMethodNotAllowedError),
            ("email_password_auth_disabled", EmailPasswordAuthDisabledError),
            ("passkey_progressive_enrollment", PasskeyProgressiveEnrollmentError),
            ("radar_challenge", RadarChallengeError),
            ("radar_sign_up_challenge", RadarSignUpChallengeError),
        ]
        for error_code, expected_class in cases:
            httpx_mock.reset()
            httpx_mock.add_response(
                status_code=403,
                json={
                    "code": error_code,
                    "message": "Error",
                    "pending_authentication_token": "pat_tok",
                },
            )
            client = WorkOSClient(
                api_key="sk_test_123", client_id="client_test", max_retries=0
            )
            with pytest.raises(expected_class) as exc_info:
                client.request("GET", ("test",))
            assert exc_info.value.pending_authentication_token == "pat_tok"
            client.close()

    def test_auth_flow_errors_are_catchable_as_authorization_error(self, httpx_mock):
        httpx_mock.add_response(
            status_code=403,
            json={
                "code": "email_verification_required",
                "message": "Error",
                "pending_authentication_token": "pat_123",
            },
        )
        client = WorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(AuthorizationError):
            client.request("GET", ("test",))
        client.close()

    def test_auth_flow_errors_are_catchable_as_authentication_flow_error(
        self, httpx_mock
    ):
        httpx_mock.add_response(
            status_code=403,
            json={
                "code": "mfa_challenge",
                "message": "Error",
                "pending_authentication_token": "pat_123",
            },
        )
        client = WorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(AuthenticationFlowError):
            client.request("GET", ("test",))
        client.close()

    def test_unknown_403_code_raises_authorization_error(self, httpx_mock):
        httpx_mock.add_response(
            status_code=403,
            json={"code": "some_future_code", "message": "Unknown"},
        )
        client = WorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(AuthorizationError) as exc_info:
            client.request("GET", ("test",))
        assert not isinstance(exc_info.value, AuthenticationFlowError)
        client.close()

    def test_raises_404(self, httpx_mock):
        httpx_mock.add_response(
            status_code=404,
            json={"message": "Error"},
        )
        client = WorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(NotFoundError):
            client.request("GET", ("test",))
        client.close()

    def test_raises_409(self, httpx_mock):
        httpx_mock.add_response(
            status_code=409,
            json={"message": "Error"},
        )
        client = WorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(ConflictError):
            client.request("GET", ("test",))
        client.close()

    def test_raises_422(self, httpx_mock):
        httpx_mock.add_response(
            status_code=422,
            json={"message": "Error"},
        )
        client = WorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(UnprocessableEntityError):
            client.request("GET", ("test",))
        client.close()

    def test_raises_429(self, httpx_mock):
        httpx_mock.add_response(
            status_code=429,
            json={"message": "Error"},
        )
        client = WorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(RateLimitExceededError):
            client.request("GET", ("test",))
        client.close()

    def test_raises_500(self, httpx_mock):
        httpx_mock.add_response(
            status_code=500,
            json={"message": "Error"},
        )
        client = WorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(ServerError):
            client.request("GET", ("test",))
        client.close()

    def test_idempotency_key_on_post(self, httpx_mock):
        httpx_mock.add_response(json={})
        client = WorkOSClient(api_key="sk_test_123", client_id="client_test")
        client.request("POST", ("test",))
        request = httpx_mock.get_request()
        assert "Idempotency-Key" in request.headers
        client.close()

    def test_no_idempotency_key_on_get(self, httpx_mock):
        httpx_mock.add_response(json={})
        client = WorkOSClient(api_key="sk_test_123", client_id="client_test")
        client.request("GET", ("test",))
        request = httpx_mock.get_request()
        assert "Idempotency-Key" not in request.headers
        client.close()

    def test_no_authorization_header_without_api_key(self, httpx_mock):
        httpx_mock.add_response(json={})
        client = WorkOSClient(client_id="client_test")
        client.request("GET", ("test",))
        request = httpx_mock.get_request()
        assert "Authorization" not in request.headers
        client.close()

    def test_empty_body_sends_json(self, httpx_mock):
        httpx_mock.add_response(json={})
        client = WorkOSClient(api_key="sk_test_123", client_id="client_test")
        client.request("PUT", ("test",), body={})
        request = httpx_mock.get_request()
        assert request.content == b"{}"
        client.close()

    def test_calculate_retry_delay_uses_retry_after_seconds(self):
        assert WorkOSClient._calculate_retry_delay(1, "30") == 30.0

    def test_retry_exhaustion_raises_rate_limit(self, httpx_mock, monkeypatch):
        monkeypatch.setattr(generated_client_module.time, "sleep", lambda _: None)
        for _ in range(4):
            httpx_mock.add_response(
                status_code=429,
                headers={"Retry-After": "0"},
                json={"message": "Slow down"},
            )
        client = WorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=3
        )
        with pytest.raises(RateLimitExceededError):
            client.request("GET", ("test",))
        client.close()

    def test_rate_limit_retry_after_is_parsed(self, httpx_mock):
        httpx_mock.add_response(
            status_code=429,
            headers={"Retry-After": "30"},
            json={"message": "Slow down"},
        )
        client = WorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(RateLimitExceededError) as exc_info:
            client.request("GET", ("test",))
        assert exc_info.value.retry_after == 30.0
        client.close()

    def test_timeout_error_is_wrapped(self, httpx_mock, monkeypatch):
        monkeypatch.setattr(generated_client_module.time, "sleep", lambda _: None)
        httpx_mock.add_exception(httpx.TimeoutException("timed out"))
        client = WorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(generated_client_module.WorkOSTimeoutError):
            client.request("GET", ("test",))
        client.close()

    def test_connection_error_is_wrapped(self, httpx_mock, monkeypatch):
        monkeypatch.setattr(generated_client_module.time, "sleep", lambda _: None)
        httpx_mock.add_exception(httpx.ConnectError("connect failed"))
        client = WorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(generated_client_module.WorkOSConnectionError):
            client.request("GET", ("test",))
        client.close()

    def test_documented_import_surface_exposes_resources(self):
        client = WorkOSClient(api_key="sk_test_123", client_id="client_test")
        assert client.admin_portal is not None
        assert client.api_keys is not None
        assert client.audit_logs is not None
        assert client.authorization is not None
        assert client.connect is not None
        assert client.directory_sync is not None
        assert client.events is not None
        assert client.feature_flags is not None
        assert client.multi_factor_auth is not None
        assert client.organization_domains is not None
        assert client.organizations is not None
        assert client.pipes is not None
        assert client.radar is not None
        assert client.sso is not None
        assert client.user_management is not None
        assert client.webhooks is not None
        assert client.widgets is not None
        client.close()

    def test_request_raw_preserves_json_dict_response(self, httpx_mock):
        httpx_mock.add_response(json={"ok": True})
        client = WorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        result = client.request_raw("GET", ("test",))
        assert result == {"ok": True}
        client.close()

    def test_request_list_preserves_json_array_response(self, httpx_mock):
        httpx_mock.add_response(json=[{"id": "item_123"}])
        client = WorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        result = client.request_list("GET", ("test",))
        assert result == [{"id": "item_123"}]
        client.close()

    def test_request_returns_none_for_non_json_success_without_model(self, httpx_mock):
        httpx_mock.add_response(status_code=202, content=b"\n")
        client = WorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        result = client.request("DELETE", ("test",))
        assert result is None
        client.close()


@pytest.mark.asyncio
class TestAsyncWorkOSClient:
    async def test_documented_import_surface_exposes_resources(self):
        client = AsyncWorkOSClient(api_key="sk_test_123", client_id="client_test")
        assert client.admin_portal is not None
        assert client.api_keys is not None
        assert client.audit_logs is not None
        assert client.authorization is not None
        assert client.connect is not None
        assert client.directory_sync is not None
        assert client.events is not None
        assert client.feature_flags is not None
        assert client.multi_factor_auth is not None
        assert client.organization_domains is not None
        assert client.organizations is not None
        assert client.pipes is not None
        assert client.radar is not None
        assert client.sso is not None
        assert client.user_management is not None
        assert client.webhooks is not None
        assert client.widgets is not None
        await client.close()

    async def test_request_raw_preserves_json_dict_response(self, httpx_mock):
        httpx_mock.add_response(json={"ok": True})
        client = AsyncWorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        result = await client.request_raw("GET", ("test",))
        assert result == {"ok": True}
        await client.close()

    async def test_request_list_preserves_json_array_response(self, httpx_mock):
        httpx_mock.add_response(json=[{"id": "item_123"}])
        client = AsyncWorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        result = await client.request_list("GET", ("test",))
        assert result == [{"id": "item_123"}]
        await client.close()

    async def test_request_returns_none_for_non_json_success_without_model(
        self, httpx_mock
    ):
        httpx_mock.add_response(status_code=202, content=b"\n")
        client = AsyncWorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        result = await client.request("DELETE", ("test",))
        assert result is None
        await client.close()

    async def test_raises_400(self, httpx_mock):
        httpx_mock.add_response(
            status_code=400,
            json={"message": "Error"},
        )
        client = AsyncWorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(BadRequestError):
            await client.request("GET", ("test",))
        await client.close()

    async def test_raises_401(self, httpx_mock):
        httpx_mock.add_response(
            status_code=401,
            json={"message": "Error"},
        )
        client = AsyncWorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(AuthenticationError):
            await client.request("GET", ("test",))
        await client.close()

    async def test_raises_403(self, httpx_mock):
        httpx_mock.add_response(
            status_code=403,
            json={"message": "Error"},
        )
        client = AsyncWorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(AuthorizationError):
            await client.request("GET", ("test",))
        await client.close()

    async def test_raises_email_verification_required(self, httpx_mock):
        httpx_mock.add_response(
            status_code=403,
            json={
                "code": "email_verification_required",
                "message": "Email verification required",
                "pending_authentication_token": "pat_123",
                "email_verification_id": "ev_123",
                "email": "user@example.com",
            },
        )
        client = AsyncWorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(EmailVerificationRequiredError) as exc_info:
            await client.request("GET", ("test",))
        assert exc_info.value.pending_authentication_token == "pat_123"
        assert exc_info.value.email_verification_id == "ev_123"
        assert exc_info.value.email == "user@example.com"
        await client.close()

    async def test_raises_mfa_challenge(self, httpx_mock):
        httpx_mock.add_response(
            status_code=403,
            json={
                "code": "mfa_challenge",
                "message": "MFA challenge required",
                "pending_authentication_token": "pat_789",
                "user": {"id": "user_123"},
                "authentication_factors": [{"id": "af_1", "type": "totp"}],
            },
        )
        client = AsyncWorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(MfaChallengeError) as exc_info:
            await client.request("GET", ("test",))
        assert exc_info.value.pending_authentication_token == "pat_789"
        assert exc_info.value.authentication_factors == [{"id": "af_1", "type": "totp"}]
        await client.close()

    async def test_raises_sso_required(self, httpx_mock):
        httpx_mock.add_response(
            status_code=403,
            json={
                "error": "sso_required",
                "error_description": "SSO is required",
                "pending_authentication_token": "pat_sso",
                "email": "user@example.com",
                "connection_ids": ["conn_1"],
            },
        )
        client = AsyncWorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(SsoRequiredError) as exc_info:
            await client.request("GET", ("test",))
        assert exc_info.value.pending_authentication_token == "pat_sso"
        assert exc_info.value.connection_ids == ["conn_1"]
        await client.close()

    async def test_auth_flow_errors_backward_compat(self, httpx_mock):
        httpx_mock.add_response(
            status_code=403,
            json={
                "code": "organization_selection_required",
                "message": "Error",
                "pending_authentication_token": "pat_123",
            },
        )
        client = AsyncWorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(AuthorizationError):
            await client.request("GET", ("test",))
        await client.close()

    async def test_unknown_403_code_raises_authorization_error(self, httpx_mock):
        httpx_mock.add_response(
            status_code=403,
            json={"code": "some_future_code", "message": "Unknown"},
        )
        client = AsyncWorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(AuthorizationError) as exc_info:
            await client.request("GET", ("test",))
        assert not isinstance(exc_info.value, AuthenticationFlowError)
        await client.close()

    async def test_raises_404(self, httpx_mock):
        httpx_mock.add_response(
            status_code=404,
            json={"message": "Error"},
        )
        client = AsyncWorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(NotFoundError):
            await client.request("GET", ("test",))
        await client.close()

    async def test_raises_409(self, httpx_mock):
        httpx_mock.add_response(
            status_code=409,
            json={"message": "Error"},
        )
        client = AsyncWorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(ConflictError):
            await client.request("GET", ("test",))
        await client.close()

    async def test_raises_422(self, httpx_mock):
        httpx_mock.add_response(
            status_code=422,
            json={"message": "Error"},
        )
        client = AsyncWorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(UnprocessableEntityError):
            await client.request("GET", ("test",))
        await client.close()

    async def test_raises_429(self, httpx_mock):
        httpx_mock.add_response(
            status_code=429,
            json={"message": "Error"},
        )
        client = AsyncWorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(RateLimitExceededError):
            await client.request("GET", ("test",))
        await client.close()

    async def test_raises_500(self, httpx_mock):
        httpx_mock.add_response(
            status_code=500,
            json={"message": "Error"},
        )
        client = AsyncWorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(ServerError):
            await client.request("GET", ("test",))
        await client.close()

    async def test_timeout_error_is_wrapped(self, httpx_mock, monkeypatch):
        async def _sleep(_: float) -> None:
            return None

        monkeypatch.setattr(generated_client_module.asyncio, "sleep", _sleep)
        httpx_mock.add_exception(httpx.TimeoutException("timed out"))
        client = AsyncWorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(generated_client_module.WorkOSTimeoutError):
            await client.request("GET", ("test",))
        await client.close()

    async def test_connection_error_is_wrapped(self, httpx_mock, monkeypatch):
        async def _sleep(_: float) -> None:
            return None

        monkeypatch.setattr(generated_client_module.asyncio, "sleep", _sleep)
        httpx_mock.add_exception(httpx.ConnectError("connect failed"))
        client = AsyncWorkOSClient(
            api_key="sk_test_123", client_id="client_test", max_retries=0
        )
        with pytest.raises(generated_client_module.WorkOSConnectionError):
            await client.request("GET", ("test",))
        await client.close()
