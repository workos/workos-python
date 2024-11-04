from typing import Literal, List
from workos.types.workos_model import WorkOSModel

OauthCredentialProviders = Literal[
    "AppleOauth",
    "GitHubOauth",
    "GoogleOauth",
    "MicrosoftOauth",
]


class OauthCredentials(WorkOSModel):
    """Representation of a Oauth credentials"""

    provider: OauthCredentialProviders
    access_token: str
    refresh_token: str
    expires_at: int
    scopes: List[str]
