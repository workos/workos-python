from enum import Enum


class ConnectionType(Enum):
    ADFSSAML = "ADFSSAML"
    AzureSAML = "AzureSAML"
    GoogleOAuth = "GoogleOAuth"
    OktaSAML = "OktaSAML"
