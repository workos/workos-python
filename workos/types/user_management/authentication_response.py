from typing import Literal, Optional
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


class AuthenticationResponse(WorkOSModel):
    """Representation of a WorkOS User and Organization ID response."""

    access_token: str
    authentication_method: Optional[AuthenticationMethod] = None
    impersonator: Optional[Impersonator] = None
    organization_id: Optional[str] = None
    refresh_token: str
    user: User


class RefreshTokenAuthenticationResponse(WorkOSModel):
    """Representation of a WorkOS refresh token authentication response."""

    access_token: str
    refresh_token: str
