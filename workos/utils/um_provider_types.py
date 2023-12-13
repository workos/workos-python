from enum import Enum


class UserManagementProviderType(Enum):
    AuthKit = "authkit"
    GitHubOAuth = "GitHubOAuth"
    GoogleOAuth = "GoogleOAuth"
    MicrosoftOAuth = "MicrosoftOAuth"
