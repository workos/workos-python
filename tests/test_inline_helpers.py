import json

import pytest
from cryptography.fernet import Fernet

from workos.session import (
    AsyncSession,
    AuthenticateWithSessionCookieErrorResponse,
    AuthenticateWithSessionCookieFailureReason,
    Session,
)
from workos.sso.models import SSOTokenResponse
from workos.user_management.models import AuthenticateResponse
from tests.generated_helpers import load_fixture

COOKIE_PASSWORD = Fernet.generate_key().decode("utf-8")


class TestSessionCookieInline:
    def test_load_sealed_session(self, workos):
        session = workos.user_management.load_sealed_session(
            session_data="sealed-data", cookie_password=COOKIE_PASSWORD
        )
        assert isinstance(session, Session)

    def test_authenticate_with_session_cookie_no_data(self, workos):
        result = workos.user_management.authenticate_with_session_cookie(
            session_data="", cookie_password=COOKIE_PASSWORD
        )
        assert isinstance(result, AuthenticateWithSessionCookieErrorResponse)
        assert (
            result.reason
            == AuthenticateWithSessionCookieFailureReason.NO_SESSION_COOKIE_PROVIDED
        )

    def test_authenticate_with_session_cookie_invalid(self, workos):
        result = workos.user_management.authenticate_with_session_cookie(
            session_data="garbage", cookie_password=COOKIE_PASSWORD
        )
        assert isinstance(result, AuthenticateWithSessionCookieErrorResponse)
        assert (
            result.reason
            == AuthenticateWithSessionCookieFailureReason.INVALID_SESSION_COOKIE
        )


@pytest.mark.asyncio
class TestAsyncSessionCookieInline:
    async def test_load_sealed_session(self, async_workos):
        session = async_workos.user_management.load_sealed_session(
            session_data="sealed-data", cookie_password=COOKIE_PASSWORD
        )
        assert isinstance(session, AsyncSession)

    async def test_authenticate_with_session_cookie_no_data(self, async_workos):
        result = async_workos.user_management.authenticate_with_session_cookie(
            session_data="", cookie_password=COOKIE_PASSWORD
        )
        assert isinstance(result, AuthenticateWithSessionCookieErrorResponse)


class TestAuthKitPKCEAuthorizationUrl:
    def test_returns_required_keys(self, workos):
        result = workos.user_management.get_authorization_url_with_pkce(
            redirect_uri="https://example.com/callback"
        )
        assert "url" in result
        assert "state" in result
        assert "code_verifier" in result

    def test_url_contains_pkce_params(self, workos):
        result = workos.user_management.get_authorization_url_with_pkce(
            redirect_uri="https://example.com/callback"
        )
        assert "code_challenge=" in result["url"]
        assert "code_challenge_method=S256" in result["url"]

    def test_code_verifier_length(self, workos):
        result = workos.user_management.get_authorization_url_with_pkce(
            redirect_uri="https://example.com/callback"
        )
        assert len(result["code_verifier"]) == 43
        assert len(result["state"]) == 43

    def test_with_provider(self, workos):
        result = workos.user_management.get_authorization_url_with_pkce(
            redirect_uri="https://example.com/callback", provider="GoogleOAuth"
        )
        assert "provider=GoogleOAuth" in result["url"]

    def test_with_organization_id(self, workos):
        result = workos.user_management.get_authorization_url_with_pkce(
            redirect_uri="https://example.com/callback", organization_id="org_01"
        )
        assert "organization_id=org_01" in result["url"]


@pytest.mark.asyncio
class TestAsyncAuthKitPKCEAuthorizationUrl:
    async def test_returns_required_keys(self, async_workos):
        result = await async_workos.user_management.get_authorization_url_with_pkce(
            redirect_uri="https://example.com/callback"
        )
        assert "url" in result
        assert "state" in result
        assert "code_verifier" in result

    async def test_url_contains_pkce_params(self, async_workos):
        result = await async_workos.user_management.get_authorization_url_with_pkce(
            redirect_uri="https://example.com/callback"
        )
        assert "code_challenge=" in result["url"]
        assert "code_challenge_method=S256" in result["url"]


class TestAuthKitPKCECodeExchange:
    def test_sends_code_verifier(self, workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("authenticate_response.json"))
        result = workos.user_management.authenticate_with_code_pkce(
            code="auth_code_123", code_verifier="test_verifier_abc"
        )
        assert isinstance(result, AuthenticateResponse)
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body["code"] == "auth_code_123"
        assert body["code_verifier"] == "test_verifier_abc"
        assert body["grant_type"] == "authorization_code"

    def test_includes_client_secret_when_api_key_present(self, workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("authenticate_response.json"))
        workos.user_management.authenticate_with_code_pkce(
            code="auth_code_123", code_verifier="test_verifier_abc"
        )
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert "client_secret" in body

    def test_forwards_radar_context(self, workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("authenticate_response.json"))
        workos.user_management.authenticate_with_code_pkce(
            code="auth_code_123",
            code_verifier="test_verifier_abc",
            ip_address="203.0.113.42",
            device_id="device_01HXYZ",
            user_agent="Mozilla/5.0",
        )
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body["ip_address"] == "203.0.113.42"
        assert body["device_id"] == "device_01HXYZ"
        assert body["user_agent"] == "Mozilla/5.0"

    def test_omits_radar_context_when_not_provided(self, workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("authenticate_response.json"))
        workos.user_management.authenticate_with_code_pkce(
            code="auth_code_123", code_verifier="test_verifier_abc"
        )
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert "ip_address" not in body
        assert "device_id" not in body
        assert "user_agent" not in body


@pytest.mark.asyncio
class TestAsyncAuthKitPKCECodeExchange:
    async def test_sends_code_verifier(self, async_workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("authenticate_response.json"))
        result = await async_workos.user_management.authenticate_with_code_pkce(
            code="auth_code_123", code_verifier="test_verifier_abc"
        )
        assert isinstance(result, AuthenticateResponse)
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body["code_verifier"] == "test_verifier_abc"

    async def test_forwards_radar_context(self, async_workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("authenticate_response.json"))
        await async_workos.user_management.authenticate_with_code_pkce(
            code="auth_code_123",
            code_verifier="test_verifier_abc",
            ip_address="203.0.113.42",
            device_id="device_01HXYZ",
            user_agent="Mozilla/5.0",
        )
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body["ip_address"] == "203.0.113.42"
        assert body["device_id"] == "device_01HXYZ"
        assert body["user_agent"] == "Mozilla/5.0"

    async def test_omits_radar_context_when_not_provided(
        self, async_workos, httpx_mock
    ):
        httpx_mock.add_response(json=load_fixture("authenticate_response.json"))
        await async_workos.user_management.authenticate_with_code_pkce(
            code="auth_code_123", code_verifier="test_verifier_abc"
        )
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert "ip_address" not in body
        assert "device_id" not in body
        assert "user_agent" not in body


class TestSSOPKCEAuthorizationUrl:
    def test_returns_required_keys(self, workos):
        result = workos.sso.get_authorization_url_with_pkce(
            redirect_uri="https://example.com/callback"
        )
        assert "url" in result
        assert "state" in result
        assert "code_verifier" in result

    def test_url_contains_pkce_params(self, workos):
        result = workos.sso.get_authorization_url_with_pkce(
            redirect_uri="https://example.com/callback"
        )
        assert "code_challenge=" in result["url"]
        assert "code_challenge_method=S256" in result["url"]
        assert "sso/authorize" in result["url"]

    def test_with_connection(self, workos):
        result = workos.sso.get_authorization_url_with_pkce(
            redirect_uri="https://example.com/callback", connection="conn_01"
        )
        assert "connection=conn_01" in result["url"]


@pytest.mark.asyncio
class TestAsyncSSOPKCEAuthorizationUrl:
    async def test_returns_required_keys(self, async_workos):
        result = await async_workos.sso.get_authorization_url_with_pkce(
            redirect_uri="https://example.com/callback"
        )
        assert "url" in result
        assert "state" in result
        assert "code_verifier" in result


class TestSSOPKCECodeExchange:
    def test_sends_code_verifier(self, workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("sso_token_response.json"))
        result = workos.sso.get_profile_and_token_pkce(
            code="auth_code_123", code_verifier="test_verifier_abc"
        )
        assert isinstance(result, SSOTokenResponse)
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body["code"] == "auth_code_123"
        assert body["code_verifier"] == "test_verifier_abc"

    def test_includes_client_secret_when_api_key_present(self, workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("sso_token_response.json"))
        workos.sso.get_profile_and_token_pkce(
            code="auth_code_123", code_verifier="test_verifier_abc"
        )
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert "client_secret" in body


@pytest.mark.asyncio
class TestAsyncSSOPKCECodeExchange:
    async def test_sends_code_verifier(self, async_workos, httpx_mock):
        httpx_mock.add_response(json=load_fixture("sso_token_response.json"))
        result = await async_workos.sso.get_profile_and_token_pkce(
            code="auth_code_123", code_verifier="test_verifier_abc"
        )
        assert isinstance(result, SSOTokenResponse)
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body["code_verifier"] == "test_verifier_abc"


class TestGetJwksUrl:
    def test_uses_configured_client_id(self, workos):
        url = workos.user_management.get_jwks_url()
        assert url == "https://api.workos.com/sso/jwks/client_test"

    def test_explicit_client_id_overrides_default(self, workos):
        url = workos.user_management.get_jwks_url("client_other")
        assert url == "https://api.workos.com/sso/jwks/client_other"

    def test_raises_when_no_client_id_configured(self):
        from workos import WorkOSClient
        from workos._errors import ConfigurationError

        client = WorkOSClient(api_key="sk_test_abc")
        try:
            with pytest.raises(ConfigurationError):
                client.user_management.get_jwks_url()
        finally:
            client.close()


@pytest.mark.asyncio
class TestAsyncGetJwksUrl:
    async def test_uses_configured_client_id(self, async_workos):
        url = async_workos.user_management.get_jwks_url()
        assert url == "https://api.workos.com/sso/jwks/client_test"

    async def test_explicit_client_id_overrides_default(self, async_workos):
        url = async_workos.user_management.get_jwks_url("client_other")
        assert url == "https://api.workos.com/sso/jwks/client_other"
