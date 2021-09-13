from enum import Enum


class ConnectionType(Enum):
    ADFSSAML = "ADFSSAML"
    AzureSAML = "AzureSAML"
    GenericOIDC = "GenericOIDC"
    GenericSAML = "GenericSAML"
    GoogleOAuth = "GoogleOAuth"
    GoogleSAML = "GoogleSAML"
    MagicLink = "MagicLink"
    MicrosoftOAuth = "MicrosoftOAuth"
    OktaSAML = "OktaSAML"
    OneLoginSAML = "OneLoginSAML"
    PingFederateSAML = "PingFederateSAML"
    PingOneSAML = "PingOneSAML"
    VMwareSAML = "VMwareSAML"
