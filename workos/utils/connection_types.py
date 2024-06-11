from enum import Enum


class ConnectionType(Enum):
    ADFSSAML = "ADFSSAML"
    AdpOidc = "AdpOidc"
    AppleOAuth = "AppleOAuth"
    Auth0SAML = "Auth0SAML"
    AzureSAML = "AzureSAML"
    CasSAML = "CasSAML"
    CloudflareSAML = "CloudflareSAML"
    ClassLinkSAML = "ClassLinkSAML"
    CyberArkSAML = "CyberArkSAML"
    DuoSAML = "DuoSAML"
    GenericOIDC = "GenericOIDC"
    GenericSAML = "GenericSAML"
    GitHubOAuth = "GitHubOAuth"
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

    @classmethod
    def providers(cls):
        """Returns a generator of all connection types/providers.
        This is only needed as a workaround for providers passed
        as a string connection type.

        Returns:
            generator(list): A lazy list of all connection types
        """
        return (connection_type.value for connection_type in ConnectionType)
