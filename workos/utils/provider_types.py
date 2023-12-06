from enum import Enum


class ProviderType(Enum):
    AuthKit = "authkit"
    GoogleOAuth = "GoogleOAuth"
    MicrosoftOAuth = "MicrosoftOAuth"
