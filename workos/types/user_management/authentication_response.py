from typing import Literal, Optional, TypeVar, Union
from workos.types.user_management.impersonator import Impersonator
from workos.types.user_management.user import User
from workos.types.workos_model import WorkOSModel


AuthenticationMethod = Literal[
    "SSO",
    "Password",
    "AppleOAuth",
    "GitHubOAuth",
    "GoogleOAuth",
    "MicrosoftOAuth",
    "MagicAuth",
    "Impersonation",
]


class AuthenticationResponseBase(WorkOSModel):
    access_token: str
    refresh_token: str


class AuthenticationResponse(AuthenticationResponseBase):
    """Representation of a WorkOS User and Organization ID response."""

    authentication_method: Optional[AuthenticationMethod] = None
    impersonator: Optional[Impersonator] = None
    organization_id: Optional[str] = None
    user: User


class AuthKitAuthenticationResponse(AuthenticationResponse):
    """Representation of a WorkOS User and Organization ID response."""

    impersonator: Optional[Impersonator] = None


class RefreshTokenAuthenticationResponse(AuthenticationResponseBase):
    """Representation of a WorkOS refresh token authentication response."""

    pass


AuthenticationResponseType = TypeVar(
    "AuthenticationResponseType",
    bound=AuthenticationResponseBase,
)
