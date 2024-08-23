from typing import Literal, Optional
from workos.types.workos_model import WorkOSModel


class AuthenticationResultCommon(WorkOSModel):
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuthenticationResultSucceeded(AuthenticationResultCommon):
    status: Literal["succeeded"]
    email: str


class ErrorWithCode(WorkOSModel):
    code: str
    message: str


class AuthenticationResultFailed(AuthenticationResultCommon):
    status: Literal["failed"]
    error: ErrorWithCode
    email: Optional[str] = None
    user_id: Optional[str] = None


class AuthenticationEmailVerificationSucceededPayload(AuthenticationResultSucceeded):
    type: Literal["email_verification"]
    user_id: str


class AuthenticationMagicAuthFailedPayload(AuthenticationResultFailed):
    type: Literal["magic_auth"]


class AuthenticationMagicAuthSucceededPayload(AuthenticationResultSucceeded):
    type: Literal["magic_auth"]
    user_id: str


class AuthenticationMfaSucceededPayload(AuthenticationResultSucceeded):
    type: Literal["mfa"]
    user_id: Optional[str] = None


class AuthenticationOauthFailedPayload(AuthenticationResultFailed):
    type: Literal["oauth"]


class AuthenticationOauthSucceededPayload(AuthenticationResultSucceeded):
    type: Literal["oauth"]
    user_id: Optional[str] = None


class AuthenticationPasswordFailedPayload(AuthenticationResultFailed):
    type: Literal["password"]


class AuthenticationPasswordSucceededPayload(AuthenticationResultSucceeded):
    type: Literal["password"]
    user_id: str


class AuthenticationSsoFailedPayload(AuthenticationResultFailed):
    type: Literal["sso"]


class AuthenticationSsoSucceededPayload(AuthenticationResultSucceeded):
    type: Literal["sso"]
    user_id: Optional[str] = None
