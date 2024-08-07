from typing import Literal, Sequence
from workos.types.sso.connection_domain import ConnectionDomain
from workos.types.workos_model import WorkOSModel
from workos.typing.literals import LiteralOrUntyped

ConnectionState = Literal[
    "active", "deleting", "inactive", "requires_type", "validating"
]

ConnectionType = Literal[
    "ADFSSAML",
    "AdpOidc",
    "AppleOAuth",
    "Auth0SAML",
    "AzureSAML",
    "CasSAML",
    "CloudflareSAML",
    "ClassLinkSAML",
    "CyberArkSAML",
    "DuoSAML",
    "GenericOIDC",
    "GenericSAML",
    "GitHubOAuth",
    "GoogleOAuth",
    "GoogleSAML",
    "JumpCloudSAML",
    "KeycloakSAML",
    "LastPassSAML",
    "LoginGovOidc",
    "MagicLink",
    "MicrosoftOAuth",
    "MiniOrangeSAML",
    "NetIqSAML",
    "OktaSAML",
    "OneLoginSAML",
    "OracleSAML",
    "PingFederateSAML",
    "PingOneSAML",
    "RipplingSAML",
    "SalesforceSAML",
    "ShibbolethGenericSAML",
    "ShibbolethSAML",
    "SimpleSamlPhpSAML",
    "VMwareSAML",
]


class Connection(WorkOSModel):
    object: Literal["connection"]
    id: str
    organization_id: str
    connection_type: LiteralOrUntyped[ConnectionType]
    name: str
    state: LiteralOrUntyped[ConnectionState]
    created_at: str
    updated_at: str


class ConnectionWithDomains(Connection):
    """Representation of a Connection Response as returned by WorkOS through the SSO feature."""

    domains: Sequence[ConnectionDomain]
