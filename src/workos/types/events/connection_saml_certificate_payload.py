from typing import Literal
from workos.types.workos_model import WorkOSModel

SamlCertificateType = Literal["ResponseSigning", "RequestSigning", "ResponseEncryption"]


class SamlCertificateConnection(WorkOSModel):
    id: str
    organization_id: str


class SamlCertificate(WorkOSModel):
    certificate_type: SamlCertificateType
    expiry_date: str


class SamlCertificateWithExpiry(SamlCertificate):
    is_expired: bool


class ConnectionSamlCertificateRenewedPayload(WorkOSModel):
    connection: SamlCertificateConnection
    certificate: SamlCertificate
    renewed_at: str


class ConnectionSamlCertificateRenewalRequiredPayload(WorkOSModel):
    connection: SamlCertificateConnection
    certificate: SamlCertificateWithExpiry
    days_until_expiry: int
