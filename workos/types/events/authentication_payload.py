from typing import Literal, Union
from workos.resources.workos_model import WorkOSModel


class AuthenticationResultCommon(WorkOSModel):
    ip_address: Union[str, None]
    user_agent: Union[str, None]
    email: str
    created_at: str


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
    type: Literal["oath"]
    user_id: str


class AuthenticationPasswordFailedPayload(AuthenticationResultFailed):
    type: Literal["password"]


class AuthenticationPasswordSucceededPayload(AuthenticationResultSucceeded):
    type: Literal["password"]
    user_id: str


class AuthenticationSsoSucceededPayload(AuthenticationResultSucceeded):
    type: Literal["sso"]
    user_id: Union[str, None]
