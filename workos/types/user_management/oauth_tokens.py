from typing import Literal, Sequence

from workos.types.workos_model import WorkOSModel

OAuthTokensProvidersType = Literal[
    "AppleOauth",
    "GitHubOauth",
    "GoogleOauth",
    "MicrosoftOauth",
]


class OAuthTokens(WorkOSModel):
    """Representation of a WorkOS Dashboard member impersonating a user"""

    provider: OAuthTokensProvidersType
    access_token: str
    refresh_token: str
    expires_at: int
    scopes: Sequence[str]
