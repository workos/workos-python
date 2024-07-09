from typing import List, Literal, NamedTuple
from enum import Enum
from workos.utils.types import JsonDict


class ConnectionState(Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"


class ConnectionType(Enum):
    ADFS_SAML = "ADFSSAML"
    ADP_OIDC = "AdpOidc"
    AUTH0_SAML = "Auth0SAML"
    AZURE_SAML = "AzureSAML"
    CAS_SAML = "CasSAML"
    CLASS_LINK_SAML = "ClassLinkSAML"
    CLOUDFLARE_SAML = "CloudflareSAML"
    CYBER_ARK_SAML = "CyberArkSAML"
    DUO_SAML = "DuoSAML"
    GENERIC_OIDC = "GenericOIDC"
    GENERIC_SAML = "GenericSAML"
    GOOGLE_OAUTH = "GoogleOAuth"
    GOOGLE_SAML = "GoogleSAML"
    JUMP_CLOUD_SAML = "JumpCloudSAML"
    KEYCLOAK_SAML = "KeycloakSAML"
    LAST_PASS_SAML = "LastPassSAML"
    LOGIN_GOV_OIDC = "LoginGovOidc"
    MAGIC_LINK = "MagicLink"
    MICROSOFT_OAUTH = "MicrosoftOAuth"
    MINI_ORANGE_SAML = "MiniOrangeSAML"
    NET_IQ_SAML = "NetIqSAML"
    OKTA_SAML = "OktaSAML"
    ONE_LOGIN_SAML = "OneLoginSAML"
    ORACLE_SAML = "OracleSAML"
    PING_FEDERATE_SAML = "PingFederateSAML"
    PING_ONE_SAML = "PingOneSAML"
    RIPPLING_SAML = "RipplingSAML"
    SALESFORCE_SAML = "SalesforceSAML"
    SHIBBOLETH_GENERIC_SAML = "ShibbolethGenericSAML"
    SHIBBOLETH_SAML = "ShibbolethSAML"
    SIMPLE_SAML_PHP_SAML = "SimpleSamlPhpSAML"
    VM_WARE_SAML = "VMwareSAML"


class Domain:
    def __init__(self, attributes: JsonDict) -> None:
        self.id: str = attributes["id"]
        self.object: Literal["connection_domain"] = attributes["object"]
        self.domain: str = attributes["domain"]


class ConnectionEvent:
    def __init__(self, attributes: JsonDict) -> None:
        self.object: Literal["connection"] = attributes["object"]
        self.id: str = attributes["id"]
        self.organization_id: str = attributes["organization_id"]
        self.state: str = ConnectionState(attributes["state"])
        self.connection_type: str = ConnectionType(attributes["connection_type"])
        self.name: str = attributes["name"]
        self.created_at: str = attributes["created_at"]
        self.updated_at: str = attributes["updated_at"]
        self.domains = []
        for domain in attributes["domains"]:
            self.domains.push(Domain(attributes=domain))


class ConnectionActivatedEvent:
    event_name = "connection.activated"

    def __init__(self, attributes: JsonDict) -> None:
        self.event: Literal["connection.activated"] = attributes["event"]
        self.id: str = attributes["id"]
        self.created_at = attributes["created_at"]
        self.data: ConnectionEvent = ConnectionEvent(attributes["data"])


class ConnectionDeactivatedEvent:
    event_name = "connection.deactivated"

    def __init__(self, attributes: JsonDict) -> None:
        self.event: Literal["connection.deactivated"] = attributes["event"]
        self.id: str = attributes["id"]
        self.created_at = attributes["created_at"]
        self.data: ConnectionEvent = ConnectionEvent(attributes["data"])


class ConnectionDeactivatedEvent:
    event_name = "connection.deleted"

    def __init__(self, attributes: JsonDict) -> None:
        self.event: Literal["connection.deleted"] = attributes["event"]
        self.id: str = attributes["id"]
        self.created_at = attributes["created_at"]
        self.data: ConnectionEvent = ConnectionEvent(attributes["data"])
