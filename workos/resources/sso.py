from typing import Literal, Optional, Sequence
from workos.resources.workos_model import WorkOSModel
from workos.types.sso.connection import Connection, ConnectionType
from workos.typing.literals import LiteralOrUntyped


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
    groups: Optional[Sequence[str]] = None
    raw_attributes: dict


class ProfileAndToken(WorkOSModel):
    """Representation of a User Profile and Access Token as returned by WorkOS through the SSO feature."""

    access_token: str
    profile: Profile


class ConnectionDomain(WorkOSModel):
    object: Literal["connection_domain"]
    id: str
    domain: str


class ConnectionWithDomains(Connection):
    """Representation of a Connection Response as returned by WorkOS through the SSO feature."""

    domains: Sequence[ConnectionDomain]
