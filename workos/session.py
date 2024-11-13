import json
from typing import Any, Dict, List, Optional, Union
import jwt
from jwt import PyJWKClient
from cryptography.fernet import Fernet

from workos.types.user_management.session import (
    AuthenticateWithSessionCookieFailureReason,
    AuthenticateWithSessionCookieSuccessResponse,
    AuthenticateWithSessionCookieErrorResponse,
)

class SessionModule:
    def __init__(
        self,
        *,
        user_management: Any,
        client_id: str,
        session_data: str,
        cookie_password: str
    ) -> None:
        # If the cookie password is not provided, throw an error
        if cookie_password is None or cookie_password == "":
            raise ValueError("cookie_password is required")

        self.user_management = user_management
        self.client_id = client_id
        self.session_data = session_data
        self.cookie_password = cookie_password

        self.jwks = self.create_remote_jwk_set(
            self.user_management.get_jwks_url()
        )
        self.jwk_algorithms = [str(key.Algorithm) for key in self.jwks]

        for key in self.jwks:
            print("Key properties:", dir(key))  # This will show all available attributes
            print("Algorithm:", key.Algorithm)
            print("Key type:", key.key_type)

    def authenticate(
        self,
    ) -> Union[
        AuthenticateWithSessionCookieSuccessResponse,
        AuthenticateWithSessionCookieErrorResponse,
    ]:
        if self.session_data is None:
            return AuthenticateWithSessionCookieErrorResponse(
                authenticated=False, reason=AuthenticateWithSessionCookieFailureReason.NO_SESSION_COOKIE_PROVIDED
            )

        try:
            session = self.unseal_data(self.session_data, self.cookie_password)
        except Exception:
            return AuthenticateWithSessionCookieErrorResponse(
                authenticated=False, reason=AuthenticateWithSessionCookieFailureReason.INVALID_SESSION_COOKIE
            )

        if not session["access_token"]:
            return AuthenticateWithSessionCookieErrorResponse(
                authenticated=False, reason=AuthenticateWithSessionCookieFailureReason.INVALID_SESSION_COOKIE
            )

        if not self.is_valid_jwt(session["access_token"]):
            return AuthenticateWithSessionCookieErrorResponse(
                authenticated=False, reason=AuthenticateWithSessionCookieFailureReason.INVALID_JWT
            )

        decoded = jwt.decode(
            session["access_token"], self.jwks, algorithms=self.jwk_algorithms
        )

        return AuthenticateWithSessionCookieSuccessResponse(
            authenticated=True,
            session_id=decoded["sid"],
            organization_id=decoded["org_id"],
            role=decoded["role"],
            permissions=decoded["permissions"],
            entitlements=decoded["entitlements"],
            user=session["user"],
            impersonator=session["impersonator"],
            reason=None,
        )

    def refresh(self, options: Optional[Dict[str, Any]] = None) -> Union[
        AuthenticateWithSessionCookieSuccessResponse,
        AuthenticateWithSessionCookieErrorResponse,
    ]:
        cookie_password = options.get("cookie_password", self.cookie_password)
        organization_id = options.get("organization_id", None)

        try:
            session = self.unseal_data(self.session_data, cookie_password)
        except Exception:
            return AuthenticateWithSessionCookieErrorResponse(
                authenticated=False, reason=AuthenticateWithSessionCookieFailureReason.INVALID_SESSION_COOKIE
            )

        if not session["refresh_token"] or not session["user"]:
            return AuthenticateWithSessionCookieErrorResponse(
                authenticated=False, reason=AuthenticateWithSessionCookieFailureReason.INVALID_SESSION_COOKIE
            )

        try:
            auth_response = self.user_management.authenticate_with_refresh_token(
                refresh_token=session["refresh_token"],
                organization_id=organization_id,
            )

            self.session_data = auth_response.sealed_session
            self.cookie_password = cookie_password

            return AuthenticateWithSessionCookieSuccessResponse(
                authenticated=True,
                sealed_session=auth_response.sealed_session,
                session=auth_response,
                reason=None,
            )
        except Exception as e:
            return AuthenticateWithSessionCookieErrorResponse(
                authenticated=False, reason=str(e)
            )

    def get_logout_url(self) -> str:
        auth_response = self.authenticate()

        if not auth_response["authenticated"]:
            raise ValueError(auth_response["reason"])

        return self.user_management.get_logout_url(
            session_id=auth_response["session_id"]
        )

    def create_remote_jwk_set(self, url: str) -> List[Dict[str, Any]]:
        jwks_client = PyJWKClient(url)
        return jwks_client.get_signing_keys()

    def is_valid_jwt(self, token: str) -> bool:
        try:
            jwt.decode(token, self.jwks, algorithms=self.jwk_algorithms)
            return True
        except jwt.exceptions.InvalidTokenError as error:
            print("invalid token", error)
            return False

    @staticmethod
    def seal_data(data: Dict[str, Any], key: str) -> str:
        fernet = Fernet(key)
        # take the data and encrypt it with the key using fernet
        return fernet.encrypt(json.dumps(data).encode())

    @staticmethod
    def unseal_data(sealed_data: str, key: str) -> Dict[str, Any]:
        fernet = Fernet(key)
        return json.loads(fernet.decrypt(sealed_data).decode())
