from typing import Literal


UserManagementProviderType = Literal[
    "authkit", "AppleOAuth", "GitHubOAuth", "GoogleOAuth", "MicrosoftOAuth"
]
