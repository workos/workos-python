from typing import Literal, Optional, Union

from workos.types.workos_model import WorkOSModel
from workos.types.mfa.enroll_authentication_factor_type import (
    SmsAuthenticationFactorType,
    TotpAuthenticationFactorType,
)
from workos.typing.literals import LiteralOrUntyped


AuthenticationFactorType = Literal[
    "generic_otp", SmsAuthenticationFactorType, TotpAuthenticationFactorType
]


class TotpFactor(WorkOSModel):
    """Representation of a TOTP factor when returned in list resources and sessions."""

    issuer: str
    user: str


class ExtendedTotpFactor(TotpFactor):
    """Representation of a TOTP factor when returned when enrolling an authentication factor."""

    qr_code: str
    secret: str
    uri: str


class SmsFactor(WorkOSModel):
    phone_number: str


class AuthenticationFactorBase(WorkOSModel):
    """Representation of a MFA Authentication Factor Response as returned by WorkOS through the MFA feature."""

    object: Literal["authentication_factor"]
    id: str
    created_at: str
    updated_at: str
    type: LiteralOrUntyped[AuthenticationFactorType]
    user_id: Optional[str] = None


class AuthenticationFactorTotp(AuthenticationFactorBase):
    """Representation of a MFA Authentication Factor Response as returned by WorkOS through the MFA feature."""

    type: TotpAuthenticationFactorType
    totp: TotpFactor


class AuthenticationFactorTotpExtended(AuthenticationFactorBase):
    """Representation of a MFA Authentication Factor Response when enrolling an authentication factor."""

    type: TotpAuthenticationFactorType
    totp: ExtendedTotpFactor


class AuthenticationFactorSms(AuthenticationFactorBase):
    """Representation of a SMS Authentication Factor Response as returned by WorkOS through the MFA feature."""

    type: SmsAuthenticationFactorType
    sms: SmsFactor


AuthenticationFactor = Union[AuthenticationFactorTotp, AuthenticationFactorSms]
AuthenticationFactorExtended = Union[
    AuthenticationFactorTotpExtended, AuthenticationFactorSms
]
