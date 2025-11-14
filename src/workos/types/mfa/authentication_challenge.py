from typing import Literal, Optional
from workos.types.workos_model import WorkOSModel


class AuthenticationChallenge(WorkOSModel):
    """Representation of a MFA Challenge Response as returned by WorkOS through the MFA feature."""

    object: Literal["authentication_challenge"]
    id: str
    created_at: str
    updated_at: str
    expires_at: Optional[str] = None
    code: Optional[str] = None
    authentication_factor_id: str
