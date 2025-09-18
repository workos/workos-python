import concurrent.futures
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from tests.conftest import with_jwks_mock
from workos.session import AsyncSession, Session, _get_jwks_client
from workos.types.user_management.authentication_response import (
    RefreshTokenAuthenticationResponse,
)
from workos.types.user_management.session import (
    AuthenticateWithSessionCookieFailureReason,
    AuthenticateWithSessionCookieSuccessResponse,
    RefreshWithSessionCookieErrorResponse,
    RefreshWithSessionCookieSuccessResponse,
)


class SessionFixtures:
    @pytest.fixture(autouse=True)
    def clear_jwks_cache(self):
        _get_jwks_client.cache_clear()
        yield
        _get_jwks_client.cache_clear()

    @pytest.fixture
    def session_constants(self):
        # Generate RSA key pair for testing
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

        public_key = private_key.public_key()

        # Get the private key in PEM format
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        current_datetime = datetime.now(timezone.utc)
        current_timestamp = str(current_datetime)

        token_claims = {
            "sid": "session_123",
            "org_id": "organization_123",
            "role": "admin",
            "roles": ["admin"],
            "permissions": ["read"],
            "entitlements": ["feature_1"],
            "exp": int(current_datetime.timestamp()) + 3600,
            "iat": int(current_datetime.timestamp()),
        }

        user_id = "user_123"

        return {
            "COOKIE_PASSWORD": "pfSqwTFXUTGEBBD1RQh2kt/oNJYxBgaoZan4Z8sMrKU=",
            "SESSION_DATA": "session_data",
            "CLIENT_ID": "client_123",
            "USER_ID": user_id,
            "SESSION_ID": "session_123",
            "ORGANIZATION_ID": "organization_123",
            "CURRENT_DATETIME": current_datetime,
            "CURRENT_TIMESTAMP": current_timestamp,
            "PRIVATE_KEY": private_pem,
            "PUBLIC_KEY": public_key,
            "TEST_TOKEN": jwt.encode(token_claims, private_pem, algorithm="RS256"),
            "TEST_TOKEN_CLAIMS": token_claims,
            "TEST_USER": {
                "object": "user",
                "id": user_id,
                "email": "user@example.com",
                "first_name": "Test",
                "last_name": "User",
                "email_verified": True,
                "created_at": current_timestamp,
                "updated_at": current_timestamp,
            },
        }

    @pytest.fixture
    def mock_user_management(self):
        mock = Mock()
        mock.get_jwks_url.return_value = (
            "https://api.workos.com/user_management/sso/jwks/client_123"
        )

        return mock


class TestSessionBase(SessionFixtures):
    @with_jwks_mock
    def test_initialize_session_module(self, session_constants, mock_user_management):
        session = Session(
            user_management=mock_user_management,
            client_id=session_constants["CLIENT_ID"],
            session_data=session_constants["SESSION_DATA"],
            cookie_password=session_constants["COOKIE_PASSWORD"],
        )

        assert session.client_id == session_constants["CLIENT_ID"]
        assert session.cookie_password is not None

    @with_jwks_mock
    def test_initialize_without_cookie_password(
        self, session_constants, mock_user_management
    ):
        with pytest.raises(ValueError, match="cookie_password is required"):
            Session(
                user_management=mock_user_management,
                client_id=session_constants["CLIENT_ID"],
                session_data=session_constants["SESSION_DATA"],
                cookie_password="",
            )

    @with_jwks_mock
    def test_authenticate_no_session_cookie_provided(
        self, session_constants, mock_user_management
    ):
        session = Session(
            user_management=mock_user_management,
            client_id=session_constants["CLIENT_ID"],
            session_data="",
            cookie_password=session_constants["COOKIE_PASSWORD"],
        )

        response = session.authenticate()

        assert response.authenticated is False
        assert (
            response.reason
            == AuthenticateWithSessionCookieFailureReason.NO_SESSION_COOKIE_PROVIDED
        )

    @with_jwks_mock
    def test_authenticate_invalid_session_cookie(
        self, session_constants, mock_user_management
    ):
        session = Session(
            user_management=mock_user_management,
            client_id=session_constants["CLIENT_ID"],
            session_data="invalid_session_data",
            cookie_password=session_constants["COOKIE_PASSWORD"],
        )

        response = session.authenticate()

        assert response.authenticated is False
        assert (
            response.reason
            == AuthenticateWithSessionCookieFailureReason.INVALID_SESSION_COOKIE
        )

    @with_jwks_mock
    def test_authenticate_invalid_jwt(self, session_constants, mock_user_management):
        invalid_session_data = Session.seal_data(
            {"access_token": "invalid_session_data"},
            session_constants["COOKIE_PASSWORD"],
        )
        session = Session(
            user_management=mock_user_management,
            client_id=session_constants["CLIENT_ID"],
            session_data=invalid_session_data,
            cookie_password=session_constants["COOKIE_PASSWORD"],
        )

        response = session.authenticate()
        assert response.authenticated is False
        assert response.reason == AuthenticateWithSessionCookieFailureReason.INVALID_JWT

    @with_jwks_mock
    def test_authenticate_jwt_with_aud_claim(
        self, session_constants, mock_user_management
    ):
        access_token = jwt.encode(
            {
                **session_constants["TEST_TOKEN_CLAIMS"],
                **{"aud": session_constants["CLIENT_ID"]},
            },
            session_constants["PRIVATE_KEY"],
            algorithm="RS256",
        )

        session_data = Session.seal_data(
            {"access_token": access_token, "user": session_constants["TEST_USER"]},
            session_constants["COOKIE_PASSWORD"],
        )
        session = Session(
            user_management=mock_user_management,
            client_id=session_constants["CLIENT_ID"],
            session_data=session_data,
            cookie_password=session_constants["COOKIE_PASSWORD"],
        )

        response = session.authenticate()

        assert isinstance(response, AuthenticateWithSessionCookieSuccessResponse)

    @with_jwks_mock
    def test_authenticate_success(self, session_constants, mock_user_management):
        session = Session(
            user_management=mock_user_management,
            client_id=session_constants["CLIENT_ID"],
            session_data=session_constants["SESSION_DATA"],
            cookie_password=session_constants["COOKIE_PASSWORD"],
        )

        # Mock the session data that would be unsealed
        mock_session = {
            "access_token": jwt.encode(
                {
                    "sid": session_constants["SESSION_ID"],
                    "org_id": session_constants["ORGANIZATION_ID"],
                    "role": "admin",
                    "roles": ["admin"],
                    "permissions": ["read"],
                    "entitlements": ["feature_1"],
                    "exp": int(datetime.now(timezone.utc).timestamp()) + 3600,
                    "iat": int(datetime.now(timezone.utc).timestamp()),
                },
                session_constants["PRIVATE_KEY"],
                algorithm="RS256",
            ),
            "user": {
                "object": "user",
                "id": session_constants["USER_ID"],
                "email": "user@example.com",
                "email_verified": True,
                "created_at": session_constants["CURRENT_TIMESTAMP"],
                "updated_at": session_constants["CURRENT_TIMESTAMP"],
            },
            "impersonator": None,
        }

        # Mock the JWT payload that would be decoded
        mock_jwt_payload = {
            "sid": session_constants["SESSION_ID"],
            "org_id": session_constants["ORGANIZATION_ID"],
            "role": "admin",
            "roles": ["admin"],
            "permissions": ["read"],
            "entitlements": ["feature_1"],
        }

        with patch.object(Session, "unseal_data", return_value=mock_session), patch(
            "jwt.decode", return_value=mock_jwt_payload
        ), patch.object(
            session.jwks,
            "get_signing_key_from_jwt",
            return_value=Mock(key=session_constants["PUBLIC_KEY"]),
        ):
            response = session.authenticate()

            assert isinstance(response, AuthenticateWithSessionCookieSuccessResponse)
            assert response.authenticated is True
            assert response.session_id == session_constants["SESSION_ID"]
            assert response.organization_id == session_constants["ORGANIZATION_ID"]
            assert response.role == "admin"
            assert response.roles == ["admin"]
            assert response.permissions == ["read"]
            assert response.entitlements == ["feature_1"]
            assert response.user.id == session_constants["USER_ID"]
            assert response.impersonator is None

    @with_jwks_mock
    def test_authenticate_success_with_roles(
        self, session_constants, mock_user_management
    ):
        session = Session(
            user_management=mock_user_management,
            client_id=session_constants["CLIENT_ID"],
            session_data=session_constants["SESSION_DATA"],
            cookie_password=session_constants["COOKIE_PASSWORD"],
        )

        # Mock the session data that would be unsealed
        mock_session = {
            "access_token": jwt.encode(
                {
                    "sid": session_constants["SESSION_ID"],
                    "org_id": session_constants["ORGANIZATION_ID"],
                    "role": "admin",
                    "roles": ["admin", "member"],
                    "permissions": ["read", "write"],
                    "entitlements": ["feature_1"],
                    "exp": int(datetime.now(timezone.utc).timestamp()) + 3600,
                    "iat": int(datetime.now(timezone.utc).timestamp()),
                },
                session_constants["PRIVATE_KEY"],
                algorithm="RS256",
            ),
            "user": {
                "object": "user",
                "id": session_constants["USER_ID"],
                "email": "user@example.com",
                "email_verified": True,
                "created_at": session_constants["CURRENT_TIMESTAMP"],
                "updated_at": session_constants["CURRENT_TIMESTAMP"],
            },
            "impersonator": None,
        }

        # Mock the JWT payload that would be decoded
        mock_jwt_payload = {
            "sid": session_constants["SESSION_ID"],
            "org_id": session_constants["ORGANIZATION_ID"],
            "role": "admin",
            "roles": ["admin", "member"],
            "permissions": ["read", "write"],
            "entitlements": ["feature_1"],
        }

        with patch.object(Session, "unseal_data", return_value=mock_session), patch(
            "jwt.decode", return_value=mock_jwt_payload
        ), patch.object(
            session.jwks,
            "get_signing_key_from_jwt",
            return_value=Mock(key=session_constants["PUBLIC_KEY"]),
        ):
            response = session.authenticate()

            assert isinstance(response, AuthenticateWithSessionCookieSuccessResponse)
            assert response.authenticated is True
            assert response.session_id == session_constants["SESSION_ID"]
            assert response.organization_id == session_constants["ORGANIZATION_ID"]
            assert response.role == "admin"
            assert response.roles == ["admin", "member"]
            assert response.permissions == ["read", "write"]
            assert response.entitlements == ["feature_1"]
            assert response.user.id == session_constants["USER_ID"]
            assert response.impersonator is None

    @with_jwks_mock
    def test_refresh_invalid_session_cookie(
        self, session_constants, mock_user_management
    ):
        session = Session(
            user_management=mock_user_management,
            client_id=session_constants["CLIENT_ID"],
            session_data="invalid_session_data",
            cookie_password=session_constants["COOKIE_PASSWORD"],
        )

        response = session.refresh()

        assert isinstance(response, RefreshWithSessionCookieErrorResponse)
        assert (
            response.reason
            == AuthenticateWithSessionCookieFailureReason.INVALID_SESSION_COOKIE
        )

    def test_seal_data(self, session_constants):
        test_data = {"test": "data"}
        sealed = Session.seal_data(test_data, session_constants["COOKIE_PASSWORD"])
        assert isinstance(sealed, str)

        # Test unsealing
        unsealed = Session.unseal_data(sealed, session_constants["COOKIE_PASSWORD"])

        assert unsealed == test_data

    def test_unseal_invalid_data(self, session_constants):
        with pytest.raises(
            Exception
        ):  # Adjust exception type based on your implementation
            Session.unseal_data(
                "invalid_sealed_data", session_constants["COOKIE_PASSWORD"]
            )


class TestSession(SessionFixtures):
    @with_jwks_mock
    def test_refresh_success(self, session_constants, mock_user_management):
        session_data = Session.seal_data(
            {
                "refresh_token": "refresh_token_12345",
                "user": session_constants["TEST_USER"],
            },
            session_constants["COOKIE_PASSWORD"],
        )

        mock_response = {
            "access_token": session_constants["TEST_TOKEN"],
            "refresh_token": "refresh_token_123",
            "sealed_session": session_data,
            "user": session_constants["TEST_USER"],
        }

        mock_user_management.authenticate_with_refresh_token.return_value = (
            RefreshTokenAuthenticationResponse(**mock_response)
        )

        session = Session(
            user_management=mock_user_management,
            client_id=session_constants["CLIENT_ID"],
            session_data=session_data,
            cookie_password=session_constants["COOKIE_PASSWORD"],
        )

        with patch(
            "jwt.decode",
            return_value={
                "sid": session_constants["SESSION_ID"],
                "org_id": session_constants["ORGANIZATION_ID"],
                "role": "admin",
                "roles": ["admin"],
                "permissions": ["read"],
                "entitlements": ["feature_1"],
            },
        ):
            response = session.refresh()

            assert isinstance(response, RefreshWithSessionCookieSuccessResponse)
            assert response.authenticated is True
            assert response.user.id == session_constants["TEST_USER"]["id"]

        # Verify the refresh token was used correctly
        mock_user_management.authenticate_with_refresh_token.assert_called_once_with(
            refresh_token="refresh_token_12345",
            organization_id=None,
            session={
                "seal_session": True,
                "cookie_password": session_constants["COOKIE_PASSWORD"],
            },
        )

    @with_jwks_mock
    def test_refresh_success_with_aud_claim(
        self, session_constants, mock_user_management
    ):
        session_data = Session.seal_data(
            {
                "refresh_token": "refresh_token_12345",
                "user": session_constants["TEST_USER"],
            },
            session_constants["COOKIE_PASSWORD"],
        )

        access_token = jwt.encode(
            {
                **session_constants["TEST_TOKEN_CLAIMS"],
                **{"aud": session_constants["CLIENT_ID"]},
            },
            session_constants["PRIVATE_KEY"],
            algorithm="RS256",
        )

        mock_response = {
            "access_token": access_token,
            "refresh_token": "refresh_token_123",
            "sealed_session": session_data,
            "user": session_constants["TEST_USER"],
        }

        mock_user_management.authenticate_with_refresh_token.return_value = (
            RefreshTokenAuthenticationResponse(**mock_response)
        )

        session = Session(
            user_management=mock_user_management,
            client_id=session_constants["CLIENT_ID"],
            session_data=session_data,
            cookie_password=session_constants["COOKIE_PASSWORD"],
        )

        response = session.refresh()

        assert isinstance(response, RefreshWithSessionCookieSuccessResponse)


class TestAsyncSession(SessionFixtures):
    @pytest.mark.asyncio
    @with_jwks_mock
    async def test_refresh_success(self, session_constants, mock_user_management):
        session_data = AsyncSession.seal_data(
            {
                "refresh_token": "refresh_token_12345",
                "user": session_constants["TEST_USER"],
            },
            session_constants["COOKIE_PASSWORD"],
        )

        mock_response = {
            "access_token": session_constants["TEST_TOKEN"],
            "refresh_token": "refresh_token_123",
            "sealed_session": session_data,
            "user": session_constants["TEST_USER"],
        }

        mock_user_management.authenticate_with_refresh_token = AsyncMock(
            return_value=(RefreshTokenAuthenticationResponse(**mock_response))
        )

        session = AsyncSession(
            user_management=mock_user_management,
            client_id=session_constants["CLIENT_ID"],
            session_data=session_data,
            cookie_password=session_constants["COOKIE_PASSWORD"],
        )

        with patch(
            "jwt.decode",
            return_value={
                "sid": session_constants["SESSION_ID"],
                "org_id": session_constants["ORGANIZATION_ID"],
                "role": "admin",
                "roles": ["admin"],
                "permissions": ["read"],
                "entitlements": ["feature_1"],
            },
        ):
            response = await session.refresh()

            assert isinstance(response, RefreshWithSessionCookieSuccessResponse)
            assert response.authenticated is True
            assert response.user.id == session_constants["TEST_USER"]["id"]

        # Verify the refresh token was used correctly
        mock_user_management.authenticate_with_refresh_token.assert_called_once_with(
            refresh_token="refresh_token_12345",
            organization_id=None,
            session={
                "seal_session": True,
                "cookie_password": session_constants["COOKIE_PASSWORD"],
            },
        )

    @pytest.mark.asyncio
    @with_jwks_mock
    async def test_refresh_success_with_aud_claim(
        self, session_constants, mock_user_management
    ):
        session_data = AsyncSession.seal_data(
            {
                "refresh_token": "refresh_token_12345",
                "user": session_constants["TEST_USER"],
            },
            session_constants["COOKIE_PASSWORD"],
        )

        access_token = jwt.encode(
            {
                **session_constants["TEST_TOKEN_CLAIMS"],
                **{"aud": session_constants["CLIENT_ID"]},
            },
            session_constants["PRIVATE_KEY"],
            algorithm="RS256",
        )

        mock_response = {
            "access_token": access_token,
            "refresh_token": "refresh_token_123",
            "sealed_session": session_data,
            "user": session_constants["TEST_USER"],
        }

        mock_user_management.authenticate_with_refresh_token = AsyncMock(
            return_value=(RefreshTokenAuthenticationResponse(**mock_response))
        )

        session = AsyncSession(
            user_management=mock_user_management,
            client_id=session_constants["CLIENT_ID"],
            session_data=session_data,
            cookie_password=session_constants["COOKIE_PASSWORD"],
        )

        response = await session.refresh()

        assert isinstance(response, RefreshWithSessionCookieSuccessResponse)


class TestJWKSCaching:
    def test_jwks_client_caching_same_url(self):
        url = "https://api.workos.com/sso/jwks/test"

        client1 = _get_jwks_client(url)
        client2 = _get_jwks_client(url)

        # Should be the exact same instance
        assert client1 is client2
        assert id(client1) == id(client2)

    def test_jwks_client_caching_different_urls(self):
        url1 = "https://api.workos.com/sso/jwks/client1"
        url2 = "https://api.workos.com/sso/jwks/client2"

        client1 = _get_jwks_client(url1)
        client2 = _get_jwks_client(url2)

        # Should be different instances
        assert client1 is not client2
        assert id(client1) != id(client2)

    def test_jwks_cache_thread_safety(self):
        url = "https://api.workos.com/sso/jwks/thread_test"
        clients = []

        def get_client():
            return _get_jwks_client(url)

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(get_client) for _ in range(10)]
            clients = [future.result() for future in futures]

        first_client = clients[0]
        for client in clients[1:]:
            assert (
                client is first_client
            ), "All concurrent calls should return the same instance"
