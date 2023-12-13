from enum import Enum


class SsoProviderType(Enum):
    GitHubOAuth = "GitHubOAuth"
    GoogleOAuth = "GoogleOAuth"
    MicrosoftOAuth = "MicrosoftOAuth"
