from typing import Literal, Optional
from workos.types.workos_model import WorkOSModel


class AuthenticationResultCommon(WorkOSModel):
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    email: str


class AuthenticationResultSucceeded(AuthenticationResultCommon):
    status: Literal["succeeded"]


class ErrorWithCode(WorkOSModel):
    code: str
    message: str


class AuthenticationResultFailed(AuthenticationResultCommon):
    status: Literal["failed"]
    error: ErrorWithCode


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
    user_id: str


class AuthenticationOauthSucceededPayload(AuthenticationResultSucceeded):
    type: Literal["oauth"]
    user_id: str


class AuthenticationPasswordFailedPayload(AuthenticationResultFailed):
    type: Literal["password"]


class AuthenticationPasswordSucceededPayload(AuthenticationResultSucceeded):
    type: Literal["password"]
    user_id: str


class AuthenticationSsoSucceededPayload(AuthenticationResultSucceeded):
    type: Literal["sso"]
    user_id: Optional[str] = None
