from enum import Enum


class ConnectionType(Enum):
    ADFSSAML = ("ADFSSAML",)
    AdpOidc = "AdpOidc"
    Auth0SAML = "Auth0SAML"
    AzureSAML = "AzureSAML"
    CasSAML = "CasSAML"
    CloudflareSAML = "CloudflareSAML"
    ClassLinkSAML = "ClassLinkSAML"
    CyberArkSAML = "CyberArkSAML"
    DuoSAML = "DuoSAML"
    GenericOIDC = "GenericOIDC"
    GenericSAML = "GenericSAML"
    GoogleOAuth = "GoogleOAuth"
    GoogleSAML = "GoogleSAML"
    JumpCloudSAML = "JumpCloudSAML"
    KeycloakSAML = "KeycloakSAML"
    LastPassSAML = "LastPassSAML"
    MagicLink = "MagicLink"
    MicrosoftOAuth = "MicrosoftOAuth"
    MiniOrangeSAML = "MiniOrangeSAML"
    NetIqSAML = "NetIqSAML"
    OktaSAML = "OktaSAML"
    OneLoginSAML = "OneLoginSAML"
    OracleSAML = "OracleSAML"
    PingFederateSAML = "PingFederateSAML"
    PingOneSAML = "PingOneSAML"
    RipplingSAML = "RipplingSAML"
    SalesforceSAML = "SalesforceSAML"
    ShibbolethGenericSAML = "ShibbolethGenericSAML"
    ShibbolethSAML = "ShibbolethSAML"
    SimpleSamlPhpSAML = "SimpleSamlPhpSAML"
    VMwareSAML = "VMwareSAML"
