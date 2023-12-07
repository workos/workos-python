from enum import Enum


class UserManagementProviderType(Enum):
    AuthKit = "authkit"
    GoogleOAuth = "GoogleOAuth"
    MicrosoftOAuth = "MicrosoftOAuth"
