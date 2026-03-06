from typing import Literal, Optional, Sequence

from workos.types.workos_model import WorkOSModel
from workos.typing.literals import LiteralOrUntyped


ApplicationType = Literal["oauth", "m2m"]


class RedirectUri(WorkOSModel):
    uri: str
    default: Optional[bool] = None


class ConnectApplication(WorkOSModel):
    object: Literal["connect_application"]
    id: str
    client_id: str
    name: str
    description: Optional[str] = None
    application_type: LiteralOrUntyped[ApplicationType]
    organization_id: Optional[str] = None
    scopes: Sequence[str] = []
    created_at: str
    updated_at: str
    redirect_uris: Optional[Sequence[RedirectUri]] = None
    uses_pkce: Optional[bool] = None
    is_first_party: Optional[bool] = None
    was_dynamically_registered: Optional[bool] = None
