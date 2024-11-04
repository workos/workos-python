from typing import List
from workos.types.workos_model import WorkOSModel


class OauthCredentials(WorkOSModel):
    """Representation of a Oauth credentials"""

    provider: str
    access_token: str
    refresh_token: str
    expires_at: int
    scopes: List[str]
