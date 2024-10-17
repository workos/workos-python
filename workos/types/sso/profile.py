from typing import Any, Literal, Mapping, Optional, Sequence
from workos.types.sso.connection import ConnectionType
from workos.types.workos_model import WorkOSModel
from workos.typing.literals import LiteralOrUntyped
from typing_extensions import TypedDict


class ProfileRole(TypedDict):
    slug: str


class Profile(WorkOSModel):
    """Representation of a User Profile as returned by WorkOS through the SSO feature."""

    object: Literal["profile"]
    id: str
    connection_id: str
    connection_type: LiteralOrUntyped[ConnectionType]
    organization_id: Optional[str] = None
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    idp_id: str
    role: Optional[ProfileRole] = None
    groups: Optional[Sequence[str]] = None
    raw_attributes: Mapping[str, Any]


class ProfileAndToken(WorkOSModel):
    """Representation of a User Profile and Access Token as returned by WorkOS through the SSO feature."""

    access_token: str
    profile: Profile
