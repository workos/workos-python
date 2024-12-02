from __future__ import annotations
from typing import TYPE_CHECKING

import json
from typing import Any, Dict, Optional, Union, cast
import jwt
from jwt import PyJWKClient
from cryptography.fernet import Fernet

from workos.types.user_management.authentication_response import (
    RefreshTokenAuthenticationResponse,
)
from workos.types.user_management.session import (
    AuthenticateWithSessionCookieFailureReason,
    AuthenticateWithSessionCookieSuccessResponse,
    AuthenticateWithSessionCookieErrorResponse,
    RefreshWithSessionCookieErrorResponse,
    RefreshWithSessionCookieSuccessResponse,
)

if TYPE_CHECKING:
    from workos.user_management import UserManagementModule


class Session:
    def __init__(
        self,
        *,
        user_management: "UserManagementModule",
        client_id: str,
        session_data: str,
        cookie_password: str,
    ) -> None:
        # If the cookie password is not provided, throw an error
        if cookie_password is None or cookie_password == "":
            raise ValueError("cookie_password is required")

        self.user_management = user_management
        self.client_id = client_id
        self.session_data = session_data
        self.cookie_password = cookie_password

        self.jwks = PyJWKClient(self.user_management.get_jwks_url())

        # Algorithms are hardcoded for security reasons. See https://pyjwt.readthedocs.io/en/stable/algorithms.html#specifying-an-algorithm
        self.jwk_algorithms = ["RS256"]

    def authenticate(
        self,
    ) -> Union[
        AuthenticateWithSessionCookieSuccessResponse,
        AuthenticateWithSessionCookieErrorResponse,
    ]:
        if self.session_data is None or self.session_data == "":
            return AuthenticateWithSessionCookieErrorResponse(
                authenticated=False,
                reason=AuthenticateWithSessionCookieFailureReason.NO_SESSION_COOKIE_PROVIDED,
            )

        try:
            session = self.unseal_data(self.session_data, self.cookie_password)
        except Exception:
            return AuthenticateWithSessionCookieErrorResponse(
                authenticated=False,
                reason=AuthenticateWithSessionCookieFailureReason.INVALID_SESSION_COOKIE,
            )

        if not session.get("access_token", None):
            return AuthenticateWithSessionCookieErrorResponse(
                authenticated=False,
                reason=AuthenticateWithSessionCookieFailureReason.INVALID_SESSION_COOKIE,
            )

        if not self._is_valid_jwt(session["access_token"]):
            return AuthenticateWithSessionCookieErrorResponse(
                authenticated=False,
                reason=AuthenticateWithSessionCookieFailureReason.INVALID_JWT,
            )

        signing_key = self.jwks.get_signing_key_from_jwt(session["access_token"])
        decoded = jwt.decode(
            session["access_token"], signing_key.key, algorithms=self.jwk_algorithms
        )

        return AuthenticateWithSessionCookieSuccessResponse(
            authenticated=True,
            session_id=decoded["sid"],
            organization_id=decoded.get("org_id", None),
            role=decoded.get("role", None),
            permissions=decoded.get("permissions", None),
            entitlements=decoded.get("entitlements", None),
            user=session["user"],
            impersonator=session.get("impersonator", None),
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
        cookie_password = (
            self.cookie_password if cookie_password is None else cookie_password
        )

        try:
            session = self.unseal_data(self.session_data, cookie_password)
        except Exception:
            return RefreshWithSessionCookieErrorResponse(
                authenticated=False,
                reason=AuthenticateWithSessionCookieFailureReason.INVALID_SESSION_COOKIE,
            )

        if not session.get("refresh_token", None) or not session.get("user", None):
            return RefreshWithSessionCookieErrorResponse(
                authenticated=False,
                reason=AuthenticateWithSessionCookieFailureReason.INVALID_SESSION_COOKIE,
            )

        try:
            auth_response = cast(
                RefreshTokenAuthenticationResponse,
                self.user_management.authenticate_with_refresh_token(
                    refresh_token=session["refresh_token"],
                    organization_id=organization_id,
                    session={"seal_session": True, "cookie_password": cookie_password},
                ),
            )

            self.session_data = str(auth_response.sealed_session)
            self.cookie_password = (
                cookie_password if cookie_password is not None else self.cookie_password
            )

            signing_key = self.jwks.get_signing_key_from_jwt(auth_response.access_token)

            decoded = jwt.decode(
                auth_response.access_token,
                signing_key.key,
                algorithms=self.jwk_algorithms,
            )

            return RefreshWithSessionCookieSuccessResponse(
                authenticated=True,
                sealed_session=str(auth_response.sealed_session),
                session_id=decoded["sid"],
                organization_id=decoded.get("org_id", None),
                role=decoded.get("role", None),
                permissions=decoded.get("permissions", None),
                entitlements=decoded.get("entitlements", None),
                user=auth_response.user,
                impersonator=auth_response.impersonator,
            )
        except Exception as e:
            return RefreshWithSessionCookieErrorResponse(
                authenticated=False, reason=str(e)
            )

    def get_logout_url(self) -> str:
        auth_response = self.authenticate()

        if isinstance(auth_response, AuthenticateWithSessionCookieErrorResponse):
            raise ValueError(
                f"Failed to extract session ID for logout URL: {auth_response.reason}"
            )

        result = self.user_management.get_logout_url(
            session_id=auth_response.session_id
        )
        return str(result)

    def _is_valid_jwt(self, token: str) -> bool:
        try:
            signing_key = self.jwks.get_signing_key_from_jwt(token)
            jwt.decode(token, signing_key.key, algorithms=self.jwk_algorithms)
            return True
        except jwt.exceptions.InvalidTokenError:
            return False

    @staticmethod
    def seal_data(data: Dict[str, Any], key: str) -> str:
        fernet = Fernet(key)
        # Encrypt and convert bytes to string
        encrypted_bytes = fernet.encrypt(json.dumps(data).encode())
        return encrypted_bytes.decode("utf-8")

    @staticmethod
    def unseal_data(sealed_data: str, key: str) -> Dict[str, Any]:
        fernet = Fernet(key)
        # Convert string back to bytes before decryption
        encrypted_bytes = sealed_data.encode("utf-8")
        decrypted_str = fernet.decrypt(encrypted_bytes).decode()
        return cast(Dict[str, Any], json.loads(decrypted_str))
