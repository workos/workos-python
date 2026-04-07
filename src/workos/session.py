# @oagen-ignore-file
# This file is hand-maintained. Session management (sealed cookies, JWT
# validation, JWKS) is client-side logic that cannot be generated from the
# OpenAPI spec.

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Optional,
    Sequence,
    Union,
    cast,
)

import jwt
from cryptography.fernet import Fernet
from jwt import PyJWKClient

if TYPE_CHECKING:
    from ._client import AsyncWorkOSClient, WorkOSClient


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------


class AuthenticateWithSessionCookieFailureReason(Enum):
    INVALID_JWT = "invalid_jwt"
    INVALID_SESSION_COOKIE = "invalid_session_cookie"
    NO_SESSION_COOKIE_PROVIDED = "no_session_cookie_provided"


@dataclass(slots=True)
class AuthenticateWithSessionCookieSuccessResponse:
    """Successful session cookie authentication result."""

    authenticated: bool
    """Always True for successful authentication."""
    session_id: str
    """The authenticated session identifier."""
    organization_id: Optional[str] = None
    """The organization the user is authenticated into, if any."""
    role: Optional[str] = None
    """The user's primary role slug in the organization."""
    roles: Optional[Sequence[str]] = None
    """All role slugs assigned to the user."""
    permissions: Optional[Sequence[str]] = None
    """Permissions granted to the user."""
    user: Optional[Dict[str, Any]] = None
    """The authenticated user object."""
    impersonator: Optional[Dict[str, Any]] = None
    """Present when the session is impersonated; contains the impersonator's details."""
    entitlements: Optional[Sequence[str]] = None
    """Entitlements granted to the user."""
    feature_flags: Optional[Sequence[str]] = None
    """Feature flags enabled for the user."""


@dataclass(slots=True)
class AuthenticateWithSessionCookieErrorResponse:
    """Failed session cookie authentication result."""

    authenticated: bool
    """Always False for failed authentication."""
    reason: Union[AuthenticateWithSessionCookieFailureReason, str]
    """The reason authentication failed."""


@dataclass(slots=True)
class RefreshWithSessionCookieSuccessResponse:
    """Successful session cookie refresh result."""

    authenticated: bool
    """Always True for successful refresh."""
    sealed_session: str
    """The new sealed session token to set as a cookie."""
    session_id: str
    """The refreshed session identifier."""
    organization_id: Optional[str] = None
    """The organization the user is authenticated into, if any."""
    role: Optional[str] = None
    """The user's primary role slug in the organization."""
    roles: Optional[Sequence[str]] = None
    """All role slugs assigned to the user."""
    permissions: Optional[Sequence[str]] = None
    """Permissions granted to the user."""
    user: Optional[Dict[str, Any]] = None
    """The authenticated user object."""
    impersonator: Optional[Dict[str, Any]] = None
    """Present when the session is impersonated; contains the impersonator's details."""
    entitlements: Optional[Sequence[str]] = None
    """Entitlements granted to the user."""
    feature_flags: Optional[Sequence[str]] = None
    """Feature flags enabled for the user."""


@dataclass(slots=True)
class RefreshWithSessionCookieErrorResponse:
    """Failed session cookie refresh result."""

    authenticated: bool
    """Always False for failed refresh."""
    reason: Union[AuthenticateWithSessionCookieFailureReason, str]
    """The reason the refresh failed."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@lru_cache(maxsize=None)
def _get_jwks_client(jwks_url: str) -> PyJWKClient:
    return PyJWKClient(jwks_url)


def seal_data(data: Dict[str, Any], key: str) -> str:
    """Encrypt a dictionary with Fernet symmetric encryption."""
    fernet = Fernet(key)
    encrypted_bytes = fernet.encrypt(json.dumps(data).encode())
    return encrypted_bytes.decode("utf-8")


def unseal_data(sealed_data: str, key: str) -> Dict[str, Any]:
    """Decrypt a Fernet-encrypted string back to a dictionary."""
    fernet = Fernet(key)
    encrypted_bytes = sealed_data.encode("utf-8")
    decrypted_str = fernet.decrypt(encrypted_bytes).decode()
    return cast(Dict[str, Any], json.loads(decrypted_str))


def seal_session_from_auth_response(
    *,
    access_token: str,
    refresh_token: str,
    user: Optional[Dict[str, Any]] = None,
    impersonator: Optional[Dict[str, Any]] = None,
    cookie_password: str,
) -> str:
    """Seal session data from an authentication response into a cookie-safe string.

    Args:
        access_token: The access token from the auth response.
        refresh_token: The refresh token from the auth response.
        user: The user dict from the auth response.
        impersonator: The impersonator dict, if present.
        cookie_password: The Fernet key used to seal the session.

    Returns:
        A sealed session string suitable for storing in a cookie.
    """
    session_data: Dict[str, Any] = {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }
    if user is not None:
        session_data["user"] = user
    if impersonator is not None:
        session_data["impersonator"] = impersonator
    return seal_data(session_data, cookie_password)


# ---------------------------------------------------------------------------
# Session (sync)
# ---------------------------------------------------------------------------


class Session:
    """Server-side session management using sealed cookies and JWT validation."""

    _JWK_ALGORITHMS: List[str] = ["RS256"]

    def __init__(
        self,
        *,
        client: "WorkOSClient",
        session_data: str,
        cookie_password: str,
    ) -> None:
        if not cookie_password:
            raise ValueError("cookie_password is required")

        self._client = client
        self.session_data = session_data
        self.cookie_password = cookie_password

        jwks_url = f"{client.base_url}sso/jwks/{client.client_id}"
        self.jwks = _get_jwks_client(jwks_url)

    def authenticate(
        self,
    ) -> Union[
        AuthenticateWithSessionCookieSuccessResponse,
        AuthenticateWithSessionCookieErrorResponse,
    ]:
        """Validate the sealed session cookie and return the session claims."""
        if not self.session_data:
            return AuthenticateWithSessionCookieErrorResponse(
                authenticated=False,
                reason=AuthenticateWithSessionCookieFailureReason.NO_SESSION_COOKIE_PROVIDED,
            )

        try:
            session = unseal_data(self.session_data, self.cookie_password)
        except Exception:
            return AuthenticateWithSessionCookieErrorResponse(
                authenticated=False,
                reason=AuthenticateWithSessionCookieFailureReason.INVALID_SESSION_COOKIE,
            )

        if not session.get("access_token"):
            return AuthenticateWithSessionCookieErrorResponse(
                authenticated=False,
                reason=AuthenticateWithSessionCookieFailureReason.INVALID_SESSION_COOKIE,
            )

        try:
            signing_key = self.jwks.get_signing_key_from_jwt(session["access_token"])
            decoded = jwt.decode(
                session["access_token"],
                signing_key.key,
                algorithms=self._JWK_ALGORITHMS,
                options={"verify_aud": False},
                leeway=self._client._jwt_leeway,
            )
        except jwt.exceptions.InvalidTokenError:
            return AuthenticateWithSessionCookieErrorResponse(
                authenticated=False,
                reason=AuthenticateWithSessionCookieFailureReason.INVALID_JWT,
            )

        return AuthenticateWithSessionCookieSuccessResponse(
            authenticated=True,
            session_id=decoded["sid"],
            organization_id=decoded.get("org_id"),
            role=decoded.get("role"),
            roles=decoded.get("roles"),
            permissions=decoded.get("permissions"),
            entitlements=decoded.get("entitlements"),
            user=session.get("user"),
            impersonator=session.get("impersonator"),
            feature_flags=decoded.get("feature_flags"),
        )

    def refresh(
        self,
        *,
        organization_id: Optional[str] = None,
        cookie_password: Optional[str] = None,
    ) -> Union[
        RefreshWithSessionCookieSuccessResponse,
        RefreshWithSessionCookieErrorResponse,
    ]:
        """Refresh the session using the stored refresh token."""
        effective_cookie_password = cookie_password or self.cookie_password

        try:
            session = unseal_data(self.session_data, effective_cookie_password)
        except Exception:
            return RefreshWithSessionCookieErrorResponse(
                authenticated=False,
                reason=AuthenticateWithSessionCookieFailureReason.INVALID_SESSION_COOKIE,
            )

        if not session.get("refresh_token") or not session.get("user"):
            return RefreshWithSessionCookieErrorResponse(
                authenticated=False,
                reason=AuthenticateWithSessionCookieFailureReason.INVALID_SESSION_COOKIE,
            )

        try:
            # Use raw dict request because the generated AuthenticateResponse
            # doesn't include sealed_session, and the request body needs the
            # session parameter which isn't in the generated request models.
            body: Dict[str, Any] = {
                "grant_type": "refresh_token",
                "client_id": self._client.client_id,
                "client_secret": self._client._api_key,
                "refresh_token": session["refresh_token"],
                "session": {
                    "seal_session": True,
                    "cookie_password": effective_cookie_password,
                },
            }
            if organization_id is not None:
                body["organization_id"] = organization_id

            auth_response = self._client.request_raw(
                method="post",
                path="user_management/authenticate",
                body=body,
            )

            self.session_data = str(auth_response["sealed_session"])
            self.cookie_password = effective_cookie_password

            signing_key = self.jwks.get_signing_key_from_jwt(
                auth_response["access_token"]
            )
            decoded = jwt.decode(
                auth_response["access_token"],
                signing_key.key,
                algorithms=self._JWK_ALGORITHMS,
                options={"verify_aud": False},
                leeway=self._client._jwt_leeway,
            )

            return RefreshWithSessionCookieSuccessResponse(
                authenticated=True,
                sealed_session=str(auth_response["sealed_session"]),
                session_id=decoded["sid"],
                organization_id=decoded.get("org_id"),
                role=decoded.get("role"),
                roles=decoded.get("roles"),
                permissions=decoded.get("permissions"),
                entitlements=decoded.get("entitlements"),
                user=auth_response.get("user"),
                impersonator=auth_response.get("impersonator"),
                feature_flags=decoded.get("feature_flags"),
            )
        except Exception as e:
            return RefreshWithSessionCookieErrorResponse(
                authenticated=False, reason=str(e)
            )

    def get_logout_url(self, return_to: Optional[str] = None) -> str:
        """Get the logout URL for the current session."""
        auth_response = self.authenticate()

        if isinstance(auth_response, AuthenticateWithSessionCookieErrorResponse):
            raise ValueError(
                f"Failed to extract session ID for logout URL: {auth_response.reason}"
            )

        return self._client.user_management.get_logout_url(
            session_id=auth_response.session_id,
            return_to=return_to,
        )


# ---------------------------------------------------------------------------
# AsyncSession
# ---------------------------------------------------------------------------


class AsyncSession:
    """Async server-side session management using sealed cookies and JWT validation."""

    _JWK_ALGORITHMS: List[str] = ["RS256"]

    def __init__(
        self,
        *,
        client: "AsyncWorkOSClient",
        session_data: str,
        cookie_password: str,
    ) -> None:
        if not cookie_password:
            raise ValueError("cookie_password is required")

        self._client = client
        self.session_data = session_data
        self.cookie_password = cookie_password

        jwks_url = f"{client.base_url}sso/jwks/{client.client_id}"
        self.jwks = _get_jwks_client(jwks_url)

    def authenticate(
        self,
    ) -> Union[
        AuthenticateWithSessionCookieSuccessResponse,
        AuthenticateWithSessionCookieErrorResponse,
    ]:
        """Validate the sealed session cookie and return the session claims.

        Note: This method is synchronous because it only performs local
        operations (Fernet decryption and JWT validation using cached JWKS).
        """
        if not self.session_data:
            return AuthenticateWithSessionCookieErrorResponse(
                authenticated=False,
                reason=AuthenticateWithSessionCookieFailureReason.NO_SESSION_COOKIE_PROVIDED,
            )

        try:
            session = unseal_data(self.session_data, self.cookie_password)
        except Exception:
            return AuthenticateWithSessionCookieErrorResponse(
                authenticated=False,
                reason=AuthenticateWithSessionCookieFailureReason.INVALID_SESSION_COOKIE,
            )

        if not session.get("access_token"):
            return AuthenticateWithSessionCookieErrorResponse(
                authenticated=False,
                reason=AuthenticateWithSessionCookieFailureReason.INVALID_SESSION_COOKIE,
            )

        try:
            signing_key = self.jwks.get_signing_key_from_jwt(session["access_token"])
            decoded = jwt.decode(
                session["access_token"],
                signing_key.key,
                algorithms=self._JWK_ALGORITHMS,
                options={"verify_aud": False},
                leeway=self._client._jwt_leeway,
            )
        except jwt.exceptions.InvalidTokenError:
            return AuthenticateWithSessionCookieErrorResponse(
                authenticated=False,
                reason=AuthenticateWithSessionCookieFailureReason.INVALID_JWT,
            )

        return AuthenticateWithSessionCookieSuccessResponse(
            authenticated=True,
            session_id=decoded["sid"],
            organization_id=decoded.get("org_id"),
            role=decoded.get("role"),
            roles=decoded.get("roles"),
            permissions=decoded.get("permissions"),
            entitlements=decoded.get("entitlements"),
            user=session.get("user"),
            impersonator=session.get("impersonator"),
            feature_flags=decoded.get("feature_flags"),
        )

    async def refresh(
        self,
        *,
        organization_id: Optional[str] = None,
        cookie_password: Optional[str] = None,
    ) -> Union[
        RefreshWithSessionCookieSuccessResponse,
        RefreshWithSessionCookieErrorResponse,
    ]:
        """Refresh the session using the stored refresh token."""
        effective_cookie_password = cookie_password or self.cookie_password

        try:
            session = unseal_data(self.session_data, effective_cookie_password)
        except Exception:
            return RefreshWithSessionCookieErrorResponse(
                authenticated=False,
                reason=AuthenticateWithSessionCookieFailureReason.INVALID_SESSION_COOKIE,
            )

        if not session.get("refresh_token") or not session.get("user"):
            return RefreshWithSessionCookieErrorResponse(
                authenticated=False,
                reason=AuthenticateWithSessionCookieFailureReason.INVALID_SESSION_COOKIE,
            )

        try:
            body: Dict[str, Any] = {
                "grant_type": "refresh_token",
                "client_id": self._client.client_id,
                "client_secret": self._client._api_key,
                "refresh_token": session["refresh_token"],
                "session": {
                    "seal_session": True,
                    "cookie_password": effective_cookie_password,
                },
            }
            if organization_id is not None:
                body["organization_id"] = organization_id

            auth_response = await self._client.request_raw(
                method="post",
                path="user_management/authenticate",
                body=body,
            )

            self.session_data = str(auth_response["sealed_session"])
            self.cookie_password = effective_cookie_password

            signing_key = self.jwks.get_signing_key_from_jwt(
                auth_response["access_token"]
            )
            decoded = jwt.decode(
                auth_response["access_token"],
                signing_key.key,
                algorithms=self._JWK_ALGORITHMS,
                options={"verify_aud": False},
                leeway=self._client._jwt_leeway,
            )

            return RefreshWithSessionCookieSuccessResponse(
                authenticated=True,
                sealed_session=str(auth_response["sealed_session"]),
                session_id=decoded["sid"],
                organization_id=decoded.get("org_id"),
                role=decoded.get("role"),
                roles=decoded.get("roles"),
                permissions=decoded.get("permissions"),
                entitlements=decoded.get("entitlements"),
                user=auth_response.get("user"),
                impersonator=auth_response.get("impersonator"),
                feature_flags=decoded.get("feature_flags"),
            )
        except Exception as e:
            return RefreshWithSessionCookieErrorResponse(
                authenticated=False, reason=str(e)
            )

    async def get_logout_url(self, return_to: Optional[str] = None) -> str:
        """Get the logout URL for the current session."""
        auth_response = self.authenticate()

        if isinstance(auth_response, AuthenticateWithSessionCookieErrorResponse):
            raise ValueError(
                f"Failed to extract session ID for logout URL: {auth_response.reason}"
            )

        return self._client.user_management.get_logout_url(
            session_id=auth_response.session_id,
            return_to=return_to,
        )
