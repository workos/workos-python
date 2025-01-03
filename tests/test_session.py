import pytest
from unittest.mock import Mock, patch
import jwt
from datetime import datetime, timezone

from tests.conftest import with_jwks_mock
from workos.session import Session
from workos.types.user_management.authentication_response import (
    RefreshTokenAuthenticationResponse,
)
from workos.types.user_management.session import (
    AuthenticateWithSessionCookieFailureReason,
    AuthenticateWithSessionCookieSuccessResponse,
    RefreshWithSessionCookieErrorResponse,
    RefreshWithSessionCookieSuccessResponse,
)
from workos.types.user_management.user import User

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


@pytest.fixture(scope="session")
def TEST_CONSTANTS():
    # Generate RSA key pair for testing
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    public_key = private_key.public_key()

    # Get the private key in PEM format
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    return {
        "COOKIE_PASSWORD": "pfSqwTFXUTGEBBD1RQh2kt/oNJYxBgaoZan4Z8sMrKU=",
        "SESSION_DATA": "session_data",
        "CLIENT_ID": "client_123",
        "USER_ID": "user_123",
        "SESSION_ID": "session_123",
        "ORGANIZATION_ID": "organization_123",
        "CURRENT_TIMESTAMP": str(datetime.now(timezone.utc)),
        "PRIVATE_KEY": private_pem,
        "PUBLIC_KEY": public_key,
        "TEST_TOKEN": jwt.encode(
            {
                "sid": "session_123",
                "org_id": "organization_123",
                "role": "admin",
                "permissions": ["read"],
                "entitlements": ["feature_1"],
                "exp": int(datetime.now(timezone.utc).timestamp()) + 3600,
                "iat": int(datetime.now(timezone.utc).timestamp()),
            },
            private_pem,
            algorithm="RS256",
        ),
    }


@pytest.fixture
def mock_user_management():
    mock = Mock()
    mock.get_jwks_url.return_value = (
        "https://api.workos.com/user_management/sso/jwks/client_123"
    )

    return mock


@with_jwks_mock
def test_initialize_session_module(TEST_CONSTANTS, mock_user_management):
    session = Session(
        user_management=mock_user_management,
        client_id=TEST_CONSTANTS["CLIENT_ID"],
        session_data=TEST_CONSTANTS["SESSION_DATA"],
        cookie_password=TEST_CONSTANTS["COOKIE_PASSWORD"],
    )

    assert session.client_id == TEST_CONSTANTS["CLIENT_ID"]
    assert session.cookie_password is not None


@with_jwks_mock
def test_initialize_without_cookie_password(TEST_CONSTANTS, mock_user_management):
    with pytest.raises(ValueError, match="cookie_password is required"):
        Session(
            user_management=mock_user_management,
            client_id=TEST_CONSTANTS["CLIENT_ID"],
            session_data=TEST_CONSTANTS["SESSION_DATA"],
            cookie_password="",
        )


@with_jwks_mock
def test_authenticate_no_session_cookie_provided(TEST_CONSTANTS, mock_user_management):
    session = Session(
        user_management=mock_user_management,
        client_id=TEST_CONSTANTS["CLIENT_ID"],
        session_data=None,
        cookie_password=TEST_CONSTANTS["COOKIE_PASSWORD"],
    )

    response = session.authenticate()

    assert (
        response.reason
        == AuthenticateWithSessionCookieFailureReason.NO_SESSION_COOKIE_PROVIDED
    )


@with_jwks_mock
def test_authenticate_invalid_session_cookie(TEST_CONSTANTS, mock_user_management):
    session = Session(
        user_management=mock_user_management,
        client_id=TEST_CONSTANTS["CLIENT_ID"],
        session_data="invalid_session_data",
        cookie_password=TEST_CONSTANTS["COOKIE_PASSWORD"],
    )

    response = session.authenticate()

    assert (
        response.reason
        == AuthenticateWithSessionCookieFailureReason.INVALID_SESSION_COOKIE
    )


@with_jwks_mock
def test_authenticate_invalid_jwt(TEST_CONSTANTS, mock_user_management):
    invalid_session_data = Session.seal_data(
        {"access_token": "invalid_session_data"}, TEST_CONSTANTS["COOKIE_PASSWORD"]
    )
    session = Session(
        user_management=mock_user_management,
        client_id=TEST_CONSTANTS["CLIENT_ID"],
        session_data=invalid_session_data,
        cookie_password=TEST_CONSTANTS["COOKIE_PASSWORD"],
    )

    response = session.authenticate()

    assert response.reason == AuthenticateWithSessionCookieFailureReason.INVALID_JWT


@with_jwks_mock
def test_authenticate_success(TEST_CONSTANTS, mock_user_management):
    session = Session(
        user_management=mock_user_management,
        client_id=TEST_CONSTANTS["CLIENT_ID"],
        session_data=TEST_CONSTANTS["SESSION_DATA"],
        cookie_password=TEST_CONSTANTS["COOKIE_PASSWORD"],
    )

    # Mock the session data that would be unsealed
    mock_session = {
        "access_token": jwt.encode(
            {
                "sid": TEST_CONSTANTS["SESSION_ID"],
                "org_id": TEST_CONSTANTS["ORGANIZATION_ID"],
                "role": "admin",
                "permissions": ["read"],
                "entitlements": ["feature_1"],
                "exp": int(datetime.now(timezone.utc).timestamp()) + 3600,
                "iat": int(datetime.now(timezone.utc).timestamp()),
            },
            TEST_CONSTANTS["PRIVATE_KEY"],
            algorithm="RS256",
        ),
        "user": {
            "object": "user",
            "id": TEST_CONSTANTS["USER_ID"],
            "email": "user@example.com",
            "email_verified": True,
            "created_at": TEST_CONSTANTS["CURRENT_TIMESTAMP"],
            "updated_at": TEST_CONSTANTS["CURRENT_TIMESTAMP"],
        },
        "impersonator": None,
    }

    # Mock the JWT payload that would be decoded
    mock_jwt_payload = {
        "sid": TEST_CONSTANTS["SESSION_ID"],
        "org_id": TEST_CONSTANTS["ORGANIZATION_ID"],
        "role": "admin",
        "permissions": ["read"],
        "entitlements": ["feature_1"],
    }

    with patch.object(Session, "unseal_data", return_value=mock_session), patch.object(
        session, "_is_valid_jwt", return_value=True
    ), patch("jwt.decode", return_value=mock_jwt_payload), patch.object(
        session.jwks,
        "get_signing_key_from_jwt",
        return_value=Mock(key=TEST_CONSTANTS["PUBLIC_KEY"]),
    ):
        response = session.authenticate()

        assert isinstance(response, AuthenticateWithSessionCookieSuccessResponse)
        assert response.authenticated is True
        assert response.session_id == TEST_CONSTANTS["SESSION_ID"]
        assert response.organization_id == TEST_CONSTANTS["ORGANIZATION_ID"]
        assert response.role == "admin"
        assert response.permissions == ["read"]
        assert response.entitlements == ["feature_1"]
        assert response.user.id == TEST_CONSTANTS["USER_ID"]
        assert response.impersonator is None


@with_jwks_mock
def test_refresh_invalid_session_cookie(TEST_CONSTANTS, mock_user_management):
    session = Session(
        user_management=mock_user_management,
        client_id=TEST_CONSTANTS["CLIENT_ID"],
        session_data="invalid_session_data",
        cookie_password=TEST_CONSTANTS["COOKIE_PASSWORD"],
    )

    response = session.refresh()

    assert isinstance(response, RefreshWithSessionCookieErrorResponse)
    assert (
        response.reason
        == AuthenticateWithSessionCookieFailureReason.INVALID_SESSION_COOKIE
    )


@with_jwks_mock
def test_refresh_success(TEST_CONSTANTS, mock_user_management):
    test_user = {
        "object": "user",
        "id": TEST_CONSTANTS["USER_ID"],
        "email": "user@example.com",
        "first_name": "Test",
        "last_name": "User",
        "email_verified": True,
        "created_at": TEST_CONSTANTS["CURRENT_TIMESTAMP"],
        "updated_at": TEST_CONSTANTS["CURRENT_TIMESTAMP"],
    }

    session_data = Session.seal_data(
        {"refresh_token": "refresh_token_12345", "user": test_user},
        TEST_CONSTANTS["COOKIE_PASSWORD"],
    )

    mock_response = {
        "access_token": TEST_CONSTANTS["TEST_TOKEN"],
        "refresh_token": "refresh_token_123",
        "sealed_session": session_data,
        "user": test_user,
    }

    mock_user_management.authenticate_with_refresh_token.return_value = (
        RefreshTokenAuthenticationResponse(**mock_response)
    )

    session = Session(
        user_management=mock_user_management,
        client_id=TEST_CONSTANTS["CLIENT_ID"],
        session_data=session_data,
        cookie_password=TEST_CONSTANTS["COOKIE_PASSWORD"],
    )

    with patch.object(session, "_is_valid_jwt", return_value=True) as _:
        with patch(
            "jwt.decode",
            return_value={
                "sid": TEST_CONSTANTS["SESSION_ID"],
                "org_id": TEST_CONSTANTS["ORGANIZATION_ID"],
                "role": "admin",
                "permissions": ["read"],
                "entitlements": ["feature_1"],
            },
        ):
            response = session.refresh()

            assert isinstance(response, RefreshWithSessionCookieSuccessResponse)
            assert response.authenticated is True
            assert response.user.id == test_user["id"]

    # Verify the refresh token was used correctly
    mock_user_management.authenticate_with_refresh_token.assert_called_once_with(
        refresh_token="refresh_token_12345",
        organization_id=None,
        session={
            "seal_session": True,
            "cookie_password": TEST_CONSTANTS["COOKIE_PASSWORD"],
        },
    )


def test_seal_data(TEST_CONSTANTS):
    test_data = {"test": "data"}
    sealed = Session.seal_data(test_data, TEST_CONSTANTS["COOKIE_PASSWORD"])
    assert isinstance(sealed, str)

    # Test unsealing
    unsealed = Session.unseal_data(sealed, TEST_CONSTANTS["COOKIE_PASSWORD"])

    assert unsealed == test_data


def test_unseal_invalid_data(TEST_CONSTANTS):
    with pytest.raises(Exception):  # Adjust exception type based on your implementation
        Session.unseal_data("invalid_sealed_data", TEST_CONSTANTS["COOKIE_PASSWORD"])
