from typing import List, Literal, Union

from workos.resources.workos_model import WorkOSModel
from workos.types.sso.connection import Connection
from workos.typing.literals import LiteralOrUntyped
from workos.utils.connection_types import ConnectionType


class Profile(WorkOSModel):
    """Representation of a User Profile as returned by WorkOS through the SSO feature."""

    object: Literal["profile"]
    id: str
    connection_id: str
    connection_type: LiteralOrUntyped[ConnectionType]
    organization_id: Union[str, None]
    email: str
    first_name: Union[str, None]
    last_name: Union[str, None]
    idp_id: str
    groups: Union[List[str], None]
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

    domains: List[ConnectionDomain]


SsoProviderType = Literal[
    "AppleOAuth",
    "GitHubOAuth",
    "GoogleOAuth",
    "MicrosoftOAuth",
]
