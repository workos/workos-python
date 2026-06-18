import time
from unittest.mock import MagicMock

import jwt as pyjwt
import pytest
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.asymmetric import rsa

from workos import WorkOSClient
from workos._errors import (
    AuthenticationError,
    AuthenticationMethodNotAllowedError,
    EmailVerificationRequiredError,
    MfaChallengeError,
    MfaEnrollmentError,
    OrganizationAuthMethodsRequiredError,
    OrganizationSelectionRequiredError,
    RadarChallengeError,
    SsoRequiredError,
    WorkOSConnectionError,
    WorkOSTimeoutError,
)
from workos.session import (
    AsyncSession,
    AuthenticateWithSessionCookieErrorResponse,
    AuthenticateWithSessionCookieFailureReason,
    AuthenticateWithSessionCookieSuccessResponse,
    RefreshWithSessionCookieErrorResponse,
    RefreshWithSessionCookieSuccessResponse,
    Session,
    _map_refresh_exception_to_reason,
    seal_data,
    seal_session_from_auth_response,
    unseal_data,
)


def _generate_rsa_key_pair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    return private_key, public_key


def _make_jwt(private_key, claims=None, expired=False):
    now = time.time()
    payload = {
        "sid": "session_01",
        "org_id": "org_01",
        "role": "admin",
        "roles": ["admin"],
        "permissions": ["read", "write"],
        "entitlements": ["premium"],
        "feature_flags": ["beta"],
        "iat": int(now),
        "exp": int(now - 300) if expired else int(now + 3600),
    }
    if claims:
        payload.update(claims)
    return pyjwt.encode(payload, private_key, algorithm="RS256")


COOKIE_PASSWORD = Fernet.generate_key().decode("utf-8")


class TestSealUnseal:
    def test_seal_unseal_roundtrip(self):
        data = {"access_token": "abc", "user": {"id": "user_01"}}
        sealed = seal_data(data, COOKIE_PASSWORD)
        assert isinstance(sealed, str)
        result = unseal_data(sealed, COOKIE_PASSWORD)
        assert result == data

    def test_seal_data_returns_string(self):
        sealed = seal_data({"key": "value"}, COOKIE_PASSWORD)
        assert isinstance(sealed, str)

    def test_unseal_wrong_key(self):
        other_key = Fernet.generate_key().decode("utf-8")
        sealed = seal_data({"key": "value"}, COOKIE_PASSWORD)
        with pytest.raises(InvalidToken):
            unseal_data(sealed, other_key)

    def test_unseal_corrupted_data(self):
        with pytest.raises(Exception):
            unseal_data("not-valid-fernet-data", COOKIE_PASSWORD)


class TestSealSessionFromAuthResponse:
    def test_seal_and_unseal(self):
        sealed = seal_session_from_auth_response(
            access_token="at_123",
            refresh_token="rt_456",
            user={"id": "user_01", "email": "test@example.com"},
            cookie_password=COOKIE_PASSWORD,
        )
        data = unseal_data(sealed, COOKIE_PASSWORD)
        assert data["access_token"] == "at_123"
        assert data["user"]["id"] == "user_01"

    def test_seal_without_impersonator(self):
        sealed = seal_session_from_auth_response(
            access_token="at_123",
            refresh_token="rt_456",
            user={"id": "user_01", "email": "test@example.com"},
            cookie_password=COOKIE_PASSWORD,
        )
        data = unseal_data(sealed, COOKIE_PASSWORD)
        assert "impersonator" not in data

    def test_seal_with_impersonator(self):
        sealed = seal_session_from_auth_response(
            access_token="at_123",
            refresh_token="rt_456",
            user={"id": "user_01", "email": "test@example.com"},
            impersonator={"email": "admin@example.com"},
            cookie_password=COOKIE_PASSWORD,
        )
        data = unseal_data(sealed, COOKIE_PASSWORD)
        assert data["impersonator"]["email"] == "admin@example.com"


class TestSession:
    def setup_method(self):
        self.private_key, self.public_key = _generate_rsa_key_pair()
        self.workos = WorkOSClient(
            api_key="sk_test_123", client_id="client_test_123", max_retries=0
        )

    def teardown_method(self):
        self.workos.close()

    def _make_sealed_session(self, access_token, refresh_token="rt_123", user=None):
        data = {"access_token": access_token, "refresh_token": refresh_token}
        if user:
            data["user"] = user
        return seal_data(data, COOKIE_PASSWORD)

    def _mock_jwks(self):
        mock_jwks = MagicMock()
        mock_signing_key = MagicMock()
        mock_signing_key.key = self.public_key
        mock_jwks.get_signing_key_from_jwt.return_value = mock_signing_key
        return mock_jwks

    def test_session_cookie_password_required(self):
        with pytest.raises(ValueError, match="cookie_password is required"):
            Session(client=self.workos, session_data="anything", cookie_password="")

    def test_session_authenticate_no_session_data(self):
        session = Session(
            client=self.workos, session_data="", cookie_password=COOKIE_PASSWORD
        )
        result = session.authenticate()
        assert isinstance(result, AuthenticateWithSessionCookieErrorResponse)
        assert (
            result.reason
            == AuthenticateWithSessionCookieFailureReason.NO_SESSION_COOKIE_PROVIDED
        )

    def test_session_authenticate_invalid_sealed_data(self):
        session = Session(
            client=self.workos,
            session_data="garbage-data",
            cookie_password=COOKIE_PASSWORD,
        )
        result = session.authenticate()
        assert isinstance(result, AuthenticateWithSessionCookieErrorResponse)
        assert (
            result.reason
            == AuthenticateWithSessionCookieFailureReason.INVALID_SESSION_COOKIE
        )

    def test_session_authenticate_no_access_token(self):
        sealed = seal_data({"refresh_token": "rt"}, COOKIE_PASSWORD)
        session = Session(
            client=self.workos, session_data=sealed, cookie_password=COOKIE_PASSWORD
        )
        result = session.authenticate()
        assert isinstance(result, AuthenticateWithSessionCookieErrorResponse)
        assert (
            result.reason
            == AuthenticateWithSessionCookieFailureReason.INVALID_SESSION_COOKIE
        )

    def test_session_authenticate_success(self):
        token = _make_jwt(self.private_key)
        sealed = self._make_sealed_session(
            access_token=token, user={"id": "user_01", "email": "test@example.com"}
        )
        session = Session(
            client=self.workos, session_data=sealed, cookie_password=COOKIE_PASSWORD
        )
        session.jwks = self._mock_jwks()
        result = session.authenticate()
        assert isinstance(result, AuthenticateWithSessionCookieSuccessResponse)
        assert result.authenticated
        assert result.session_id == "session_01"
        assert result.organization_id == "org_01"
        assert result.role == "admin"
        assert result.permissions == ["read", "write"]

    def test_session_authenticate_expired_jwt(self):
        token = _make_jwt(self.private_key, expired=True)
        sealed = self._make_sealed_session(access_token=token)
        session = Session(
            client=self.workos, session_data=sealed, cookie_password=COOKIE_PASSWORD
        )
        session.jwks = self._mock_jwks()
        result = session.authenticate()
        assert isinstance(result, AuthenticateWithSessionCookieErrorResponse)
        assert result.reason == AuthenticateWithSessionCookieFailureReason.INVALID_JWT

    def test_session_refresh_invalid_session(self):
        session = Session(
            client=self.workos, session_data="garbage", cookie_password=COOKIE_PASSWORD
        )
        result = session.refresh()
        assert isinstance(result, RefreshWithSessionCookieErrorResponse)
        assert not result.authenticated

    def test_session_refresh_missing_refresh_token(self):
        sealed = seal_data({"access_token": "at"}, COOKIE_PASSWORD)
        session = Session(
            client=self.workos, session_data=sealed, cookie_password=COOKIE_PASSWORD
        )
        result = session.refresh()
        assert isinstance(result, RefreshWithSessionCookieErrorResponse)

    def test_session_refresh_success(self):
        new_token = _make_jwt(self.private_key)
        sealed = seal_data(
            {"refresh_token": "rt_old", "user": {"id": "user_01"}}, COOKIE_PASSWORD
        )
        session = Session(
            client=self.workos, session_data=sealed, cookie_password=COOKIE_PASSWORD
        )
        session.jwks = self._mock_jwks()

        api_response = {
            "access_token": new_token,
            "refresh_token": "rt_new",
            "user": {"id": "user_01", "email": "test@example.com"},
            "authentication_method": "Password",
        }
        session._client.request_raw = MagicMock(return_value=api_response)

        result = session.refresh()
        assert isinstance(result, RefreshWithSessionCookieSuccessResponse)
        assert result.authenticated
        assert result.session_id == "session_01"
        assert result.organization_id == "org_01"
        assert result.user == {"id": "user_01", "email": "test@example.com"}

        unsealed = unseal_data(result.sealed_session, COOKIE_PASSWORD)
        assert unsealed["access_token"] == new_token
        assert unsealed["refresh_token"] == "rt_new"
        assert unsealed["user"]["id"] == "user_01"

        assert session.session_data == result.sealed_session

    def test_session_refresh_seals_client_side_without_sealed_session_in_response(self):
        """Regression: API response never contains sealed_session; the SDK must seal locally."""
        new_token = _make_jwt(self.private_key)
        sealed = seal_data(
            {"refresh_token": "rt_old", "user": {"id": "user_01"}}, COOKIE_PASSWORD
        )
        session = Session(
            client=self.workos, session_data=sealed, cookie_password=COOKIE_PASSWORD
        )
        session.jwks = self._mock_jwks()

        api_response = {
            "access_token": new_token,
            "refresh_token": "rt_new",
            "user": {"id": "user_01"},
            "authentication_method": "Password",
        }
        session._client.request_raw = MagicMock(return_value=api_response)

        result = session.refresh()
        assert isinstance(result, RefreshWithSessionCookieSuccessResponse)
        assert result.sealed_session
        unsealed = unseal_data(result.sealed_session, COOKIE_PASSWORD)
        assert unsealed["access_token"] == new_token
        assert unsealed["refresh_token"] == "rt_new"

    def test_session_refresh_with_impersonator(self):
        new_token = _make_jwt(self.private_key)
        sealed = seal_data(
            {"refresh_token": "rt_old", "user": {"id": "user_01"}}, COOKIE_PASSWORD
        )
        session = Session(
            client=self.workos, session_data=sealed, cookie_password=COOKIE_PASSWORD
        )
        session.jwks = self._mock_jwks()

        api_response = {
            "access_token": new_token,
            "refresh_token": "rt_new",
            "user": {"id": "user_01"},
            "impersonator": {"email": "admin@example.com"},
            "authentication_method": "Password",
        }
        session._client.request_raw = MagicMock(return_value=api_response)

        result = session.refresh()
        assert isinstance(result, RefreshWithSessionCookieSuccessResponse)
        assert result.impersonator == {"email": "admin@example.com"}
        unsealed = unseal_data(result.sealed_session, COOKIE_PASSWORD)
        assert unsealed["impersonator"]["email"] == "admin@example.com"

    def test_session_refresh_does_not_send_session_param(self):
        """The session/seal_session param should not be sent to the API."""
        new_token = _make_jwt(self.private_key)
        sealed = seal_data(
            {"refresh_token": "rt_old", "user": {"id": "user_01"}}, COOKIE_PASSWORD
        )
        session = Session(
            client=self.workos, session_data=sealed, cookie_password=COOKIE_PASSWORD
        )
        session.jwks = self._mock_jwks()

        api_response = {
            "access_token": new_token,
            "refresh_token": "rt_new",
            "user": {"id": "user_01"},
            "authentication_method": "Password",
        }
        session._client.request_raw = MagicMock(return_value=api_response)

        session.refresh()

        call_kwargs = session._client.request_raw.call_args
        sent_body = call_kwargs.kwargs.get("body") or call_kwargs[1].get("body")
        assert "session" not in sent_body

    def test_session_refresh_round_trip_authenticate(self):
        """The sealed cookie produced by refresh() must be re-authenticatable."""
        new_token = _make_jwt(self.private_key)
        sealed = seal_data(
            {"refresh_token": "rt_old", "user": {"id": "user_01"}}, COOKIE_PASSWORD
        )
        session = Session(
            client=self.workos, session_data=sealed, cookie_password=COOKIE_PASSWORD
        )
        session.jwks = self._mock_jwks()

        api_response = {
            "access_token": new_token,
            "refresh_token": "rt_new",
            "user": {"id": "user_01", "email": "test@example.com"},
            "authentication_method": "Password",
        }
        session._client.request_raw = MagicMock(return_value=api_response)

        refresh_result = session.refresh()
        assert isinstance(refresh_result, RefreshWithSessionCookieSuccessResponse)

        new_session = Session(
            client=self.workos,
            session_data=refresh_result.sealed_session,
            cookie_password=COOKIE_PASSWORD,
        )
        new_session.jwks = self._mock_jwks()

        auth_result = new_session.authenticate()
        assert isinstance(auth_result, AuthenticateWithSessionCookieSuccessResponse)
        assert auth_result.authenticated
        assert auth_result.session_id == "session_01"
        assert auth_result.user == {"id": "user_01", "email": "test@example.com"}

    def test_session_refresh_maps_auth_error_to_refresh_denied(self):
        """AuthenticationError from request_raw maps to REFRESH_DENIED via except."""
        sealed = seal_data(
            {"refresh_token": "rt_old", "user": {"id": "user_01"}}, COOKIE_PASSWORD
        )
        session = Session(
            client=self.workos, session_data=sealed, cookie_password=COOKIE_PASSWORD
        )
        session._client.request_raw = MagicMock(
            side_effect=AuthenticationError("unauthorized")
        )

        result = session.refresh()
        assert isinstance(result, RefreshWithSessionCookieErrorResponse)
        assert not result.authenticated
        assert (
            result.reason == AuthenticateWithSessionCookieFailureReason.REFRESH_DENIED
        )

    def test_session_refresh_missing_access_token_returns_refresh_denied(self):
        """A malformed 2xx response missing access_token returns REFRESH_DENIED."""
        sealed = seal_data(
            {"refresh_token": "rt_old", "user": {"id": "user_01"}}, COOKIE_PASSWORD
        )
        session = Session(
            client=self.workos, session_data=sealed, cookie_password=COOKIE_PASSWORD
        )
        session._client.request_raw = MagicMock(return_value={})

        result = session.refresh()
        assert isinstance(result, RefreshWithSessionCookieErrorResponse)
        assert not result.authenticated
        assert (
            result.reason == AuthenticateWithSessionCookieFailureReason.REFRESH_DENIED
        )


class TestMapRefreshExceptionToReason:
    @pytest.mark.parametrize(
        "exc, expected",
        [
            (
                MfaChallengeError("mfa challenge"),
                AuthenticateWithSessionCookieFailureReason.MFA_CHALLENGE_REQUIRED,
            ),
            (
                MfaEnrollmentError("mfa enrollment"),
                AuthenticateWithSessionCookieFailureReason.MFA_ENROLLMENT_REQUIRED,
            ),
            (
                SsoRequiredError("sso required"),
                AuthenticateWithSessionCookieFailureReason.SSO_REQUIRED,
            ),
            (
                EmailVerificationRequiredError("email verification required"),
                AuthenticateWithSessionCookieFailureReason.EMAIL_VERIFICATION_REQUIRED,
            ),
            (
                OrganizationSelectionRequiredError("org selection required"),
                AuthenticateWithSessionCookieFailureReason.ORGANIZATION_SELECTION_REQUIRED,
            ),
            (
                OrganizationAuthMethodsRequiredError("org auth methods required"),
                AuthenticateWithSessionCookieFailureReason.ORGANIZATION_AUTH_METHODS_REQUIRED,
            ),
            (
                AuthenticationMethodNotAllowedError("method not allowed"),
                AuthenticateWithSessionCookieFailureReason.AUTHENTICATION_METHOD_NOT_ALLOWED,
            ),
            (
                RadarChallengeError("radar challenge"),
                AuthenticateWithSessionCookieFailureReason.RADAR_CHALLENGE_REQUIRED,
            ),
            (
                AuthenticationError("unauthorized"),
                AuthenticateWithSessionCookieFailureReason.REFRESH_DENIED,
            ),
            (
                WorkOSConnectionError("connection failed"),
                AuthenticateWithSessionCookieFailureReason.REFRESH_NETWORK_ERROR,
            ),
            (
                WorkOSTimeoutError("timeout"),
                AuthenticateWithSessionCookieFailureReason.REFRESH_NETWORK_ERROR,
            ),
        ],
    )
    def test_known_exceptions_map_to_reason(self, exc, expected):
        assert _map_refresh_exception_to_reason(exc) == expected

    def test_unknown_exception_falls_back_to_string(self):
        result = _map_refresh_exception_to_reason(RuntimeError("boom"))
        assert result == "boom"


@pytest.mark.asyncio
class TestAsyncSession:
    def _mock_jwks(self, public_key):
        mock_jwks = MagicMock()
        mock_signing_key = MagicMock()
        mock_signing_key.key = public_key
        mock_jwks.get_signing_key_from_jwt.return_value = mock_signing_key
        return mock_jwks

    async def test_async_session_authenticate_no_data(self, async_workos):
        session = AsyncSession(
            client=async_workos, session_data="", cookie_password=COOKIE_PASSWORD
        )
        result = session.authenticate()
        assert isinstance(result, AuthenticateWithSessionCookieErrorResponse)

    async def test_async_session_authenticate_success(self, async_workos):
        private_key, public_key = _generate_rsa_key_pair()
        token = _make_jwt(private_key)
        sealed = seal_data(
            {"access_token": token, "refresh_token": "rt", "user": {"id": "u1"}},
            COOKIE_PASSWORD,
        )
        session = AsyncSession(
            client=async_workos, session_data=sealed, cookie_password=COOKIE_PASSWORD
        )
        session.jwks = self._mock_jwks(public_key)
        result = session.authenticate()
        assert isinstance(result, AuthenticateWithSessionCookieSuccessResponse)
        assert result.session_id == "session_01"

    async def test_async_session_refresh_success(self, async_workos):
        from unittest.mock import AsyncMock

        private_key, public_key = _generate_rsa_key_pair()
        new_token = _make_jwt(private_key)
        sealed = seal_data(
            {"refresh_token": "rt_old", "user": {"id": "user_01"}}, COOKIE_PASSWORD
        )
        session = AsyncSession(
            client=async_workos, session_data=sealed, cookie_password=COOKIE_PASSWORD
        )
        session.jwks = self._mock_jwks(public_key)

        api_response = {
            "access_token": new_token,
            "refresh_token": "rt_new",
            "user": {"id": "user_01", "email": "test@example.com"},
            "authentication_method": "Password",
        }
        session._client.request_raw = AsyncMock(return_value=api_response)

        result = await session.refresh()
        assert isinstance(result, RefreshWithSessionCookieSuccessResponse)
        assert result.authenticated
        assert result.session_id == "session_01"

        unsealed = unseal_data(result.sealed_session, COOKIE_PASSWORD)
        assert unsealed["access_token"] == new_token
        assert unsealed["refresh_token"] == "rt_new"

    async def test_async_session_refresh_maps_auth_error_to_refresh_denied(
        self, async_workos
    ):
        from unittest.mock import AsyncMock

        sealed = seal_data(
            {"refresh_token": "rt_old", "user": {"id": "user_01"}}, COOKIE_PASSWORD
        )
        session = AsyncSession(
            client=async_workos, session_data=sealed, cookie_password=COOKIE_PASSWORD
        )
        session._client.request_raw = AsyncMock(
            side_effect=AuthenticationError("unauthorized")
        )

        result = await session.refresh()
        assert isinstance(result, RefreshWithSessionCookieErrorResponse)
        assert not result.authenticated
        assert (
            result.reason == AuthenticateWithSessionCookieFailureReason.REFRESH_DENIED
        )

    async def test_async_session_refresh_missing_access_token_returns_refresh_denied(
        self, async_workos
    ):
        from unittest.mock import AsyncMock

        sealed = seal_data(
            {"refresh_token": "rt_old", "user": {"id": "user_01"}}, COOKIE_PASSWORD
        )
        session = AsyncSession(
            client=async_workos, session_data=sealed, cookie_password=COOKIE_PASSWORD
        )
        session._client.request_raw = AsyncMock(return_value={})

        result = await session.refresh()
        assert isinstance(result, RefreshWithSessionCookieErrorResponse)
        assert not result.authenticated
        assert (
            result.reason == AuthenticateWithSessionCookieFailureReason.REFRESH_DENIED
        )
