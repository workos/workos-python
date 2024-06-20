from enum import Enum


class SsoProviderType(Enum):
    AppleOAuth = "AppleOAuth"
    GitHubOAuth = "GitHubOAuth"
    GoogleOAuth = "GoogleOAuth"
    MicrosoftOAuth = "MicrosoftOAuth"
