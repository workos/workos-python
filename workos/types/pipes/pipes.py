from datetime import datetime
from typing import Literal, Optional, Sequence, Union

from workos.types.workos_model import WorkOSModel


class AccessToken(WorkOSModel):
    """Represents an OAuth access token for a third-party provider."""

    object: Literal["access_token"]
    access_token: str
    expires_at: Optional[datetime] = None
    scopes: Sequence[str]
    missing_scopes: Sequence[str]


class GetAccessTokenSuccessResponse(WorkOSModel):
    """Successful response containing the access token."""

    active: Literal[True]
    access_token: AccessToken


class GetAccessTokenFailureResponse(WorkOSModel):
    """Failed response indicating why the token couldn't be retrieved."""

    active: Literal[False]
    error: Literal["not_installed", "needs_reauthorization"]


GetAccessTokenResponse = Union[
    GetAccessTokenSuccessResponse,
    GetAccessTokenFailureResponse,
]
