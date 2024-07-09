from typing import List, Literal, NamedTuple
from enum import Enum
from workos.utils.types import JsonDict


class AuthenticationType(Enum):
    EMAIL_VERIFICATION = "email_verification"
    MAGIC_AUTH = "magic_auth"
    MFA = "mfa"
    OAUTH = "oauth"
    PASSWORD = "password"
    SSO = "sso"


class Error(NamedTuple):
  code: str
  message: str


class AuthenticationFailedFields:
    def __init__(self, attributes: JsonDict) -> None:
        self.type: AuthenticationType = AuthenticationType(attributes["type"])
        self.status: str = attributes["status"]
        self.user_id: str = attributes["user_id"]
        self.email: str = attributes["email"]
        self.ip_address: str = attributes["ip_address"]
        self.user_agent: str = attributes["user_agent"]
        self.error: Error = Error(code=attributes["error"]["code"], message=attributes["error"]["message"])

class AuthenticationSucceededFields:
    def __init__(self, attributes: JsonDict) -> None:
        self.type: AuthenticationType = AuthenticationType(attributes["type"])
        self.status: str = attributes["status"]
        self.user_id: str = attributes["user_id"]
        self.email: str = attributes["email"]
        self.ip_address: str = attributes["ip_address"]
        self.user_agent: str = attributes["user_agent"]

class AuthenticationEmailVerificationFailedEvent:
    event_name: str = "authentication.email_verification_failed"

    def __init__(self, attributes: JsonDict) -> None:
        self.event: Literal["authentication.email_verification_failed"] = attributes['event']
        self.id: str = attributes["id"]
        self.created_at = attributes["created_at"]
        self.data: AuthenticationFailedFields = AuthenticationFailedFields(
            attributes["data"]
        )

class AuthenticationEmailVerificationSucceededEvent:
    event_name: str = "authentication.email_verification_succeeded"

    def __init__(self, attributes: JsonDict) -> None:
        self.event: Literal["authentication.email_verification_succeeded"] = attributes['event']
        self.id: str = attributes["id"]
        self.created_at = attributes["created_at"]
        self.data: AuthenticationSucceededFields = AuthenticationSucceededFields(
            attributes["data"]
        )

class AuthenticationMagicAuthFailedEvent:
    event_name: str = "authentication.magic_auth_failed"

    def __init__(self, attributes: JsonDict) -> None:
        self.event: Literal["authentication.magic_auth_failed"] = attributes['event']
        self.id: str = attributes["id"]
        self.created_at = attributes["created_at"]
        self.data: AuthenticationFailedFields = AuthenticationFailedFields(
            attributes["data"]
        )

class AuthenticationMagicAuthSucceededEvent:
    event_name: str = "authentication.magic_auth_succeeded"

    def __init__(self, attributes: JsonDict) -> None:
        self.event: Literal["authentication.magic_auth_succeeded"] = attributes['event']
        self.id: str = attributes["id"]
        self.created_at = attributes["created_at"]
        self.data: AuthenticationSucceededFields = AuthenticationSucceededFields(
            attributes["data"]
        )

class AuthenticationMFAFailedEvent:
    event_name: str = "authentication.mfa_failed"

    def __init__(self, attributes: JsonDict) -> None:
        self.event: Literal["authentication.mfa_failed"] = attributes['event']
        self.id: str = attributes["id"]
        self.created_at = attributes["created_at"]
        self.data: AuthenticationFailedFields = AuthenticationFailedFields(
            attributes["data"]
        )

class AuthenticationMFASucceededEvent:
    event_name: str = "authentication.mfa_succeeded"

    def __init__(self, attributes: JsonDict) -> None:
        self.event: Literal["authentication.mfa_succeeded"] = attributes['event']
        self.id: str = attributes["id"]
        self.created_at = attributes["created_at"]
        self.data: AuthenticationSucceededFields = AuthenticationSucceededFields(
            attributes["data"]
        )

class AuthenticationOAuthFailedEvent:
    event_name: str = "authentication.oauth_failed"

    def __init__(self, attributes: JsonDict) -> None:
        self.event: Literal["authentication.oauth_failed"] = attributes['event']
        self.id: str = attributes["id"]
        self.created_at = attributes["created_at"]
        self.data: AuthenticationFailedFields = AuthenticationFailedFields(
            attributes["data"]
        )

class AuthenticationOAuthSucceededEvent:
    event_name: str = "authentication.oauth_succeeded"

    def __init__(self, attributes: JsonDict) -> None:
        self.event: Literal["authentication.oauth_succeeded"] = attributes['event']
        self.id: str = attributes["id"]
        self.created_at = attributes["created_at"]
        self.data: AuthenticationSucceededFields = AuthenticationSucceededFields(
            attributes["data"]
        )

class AuthenticationPasswordFailedEvent:
    event_name: str = "authentication.password_failed"

    def __init__(self, attributes: JsonDict) -> None:
        self.event: Literal["authentication.password_failed"] = attributes['event']
        self.id: str = attributes["id"]
        self.created_at = attributes["created_at"]
        self.data: AuthenticationFailedFields = AuthenticationFailedFields(
            attributes["data"]
        )

class AuthenticationPasswordSucceededEvent:
    event_name: str = "authentication.password_succeeded"

    def __init__(self, attributes: JsonDict) -> None:
        self.event: Literal["authentication.password_succeeded"] = attributes['event']
        self.id: str = attributes["id"]
        self.created_at = attributes["created_at"]
        self.data: AuthenticationSucceededFields = AuthenticationSucceededFields(
            attributes["data"]
        )


class AuthenticationSSOFailedEvent:
    event_name: str = "authentication.sso_failed"

    def __init__(self, attributes: JsonDict) -> None:
        self.event: Literal["authentication.sso_failed"] = attributes['event']
        self.id: str = attributes["id"]
        self.created_at = attributes["created_at"]
        self.data: AuthenticationFailedFields = AuthenticationFailedFields(
            attributes["data"]
        )

class AuthenticationSSOSucceededEvent:
    event_name: str = "authentication.sso_succeeded"

    def __init__(self, attributes: JsonDict) -> None:
        self.event: Literal["authentication.sso_succeeded"] = attributes['event']
        self.id: str = attributes["id"]
        self.created_at = attributes["created_at"]
        self.data: AuthenticationSucceededFields = AuthenticationSucceededFields(
            attributes["data"]
        )

