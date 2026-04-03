import time
from unittest.mock import MagicMock

import jwt as pyjwt
import pytest
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.asymmetric import rsa

from workos import AsyncWorkOS, WorkOS
from workos.session import (
    AsyncSession,
    AuthenticateWithSessionCookieErrorResponse,
    AuthenticateWithSessionCookieFailureReason,
    AuthenticateWithSessionCookieSuccessResponse,
    RefreshWithSessionCookieErrorResponse,
    Session,
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

    def test_seal_without_optional_fields(self):
        sealed = seal_session_from_auth_response(
            access_token="at_123",
            refresh_token="rt_456",
            cookie_password=COOKIE_PASSWORD,
        )
        data = unseal_data(sealed, COOKIE_PASSWORD)
        assert "user" not in data

    def test_seal_with_impersonator(self):
        sealed = seal_session_from_auth_response(
            access_token="at_123",
            refresh_token="rt_456",
            impersonator={"email": "admin@example.com"},
            cookie_password=COOKIE_PASSWORD,
        )
        data = unseal_data(sealed, COOKIE_PASSWORD)
        assert data["impersonator"]["email"] == "admin@example.com"


class TestSession:
    def setup_method(self):
        self.private_key, self.public_key = _generate_rsa_key_pair()
        self.workos = WorkOS(
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
