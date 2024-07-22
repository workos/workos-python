from enum import Enum


class UserManagementProviderType(Enum):
    AuthKit = "authkit"
    AppleOAuth = "AppleOAuth"
    GitHubOAuth = "GitHubOAuth"
    GoogleOAuth = "GoogleOAuth"
    MicrosoftOAuth = "MicrosoftOAuth"
