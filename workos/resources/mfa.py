from typing import Literal, Optional, Union
from workos.resources.workos_model import WorkOSModel


SmsAuthenticationFactorType = Literal["sms"]
TotpAuthenticationFactorType = Literal["totp"]
AuthenticationFactorType = Literal[
    "generic_otp", SmsAuthenticationFactorType, TotpAuthenticationFactorType
]
EnrollAuthenticationFactorType = Literal[
    SmsAuthenticationFactorType, TotpAuthenticationFactorType
]


class TotpFactor(WorkOSModel):
    """Representation of a TOTP factor as returned in events."""

    issuer: str
    user: str


class ExtendedTotpFactor(TotpFactor):
    """Representation of a TOTP factor as returned by the API."""

    issuer: str
    user: str
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
    type: AuthenticationFactorType
    user_id: Optional[str] = None


class AuthenticationFactorTotp(AuthenticationFactorBase):
    """Representation of a MFA Authentication Factor Response as returned by WorkOS through the MFA feature."""

    type: TotpAuthenticationFactorType
    totp: Union[TotpFactor, ExtendedTotpFactor, None]


class AuthenticationFactorSms(AuthenticationFactorBase):
    """Representation of a SMS Authentication Factor Response as returned by WorkOS through the MFA feature."""

    type: SmsAuthenticationFactorType
    sms: Union[SmsFactor, None]


AuthenticationFactor = Union[AuthenticationFactorTotp, AuthenticationFactorSms]


class AuthenticationChallenge(WorkOSModel):
    """Representation of a MFA Challenge Response as returned by WorkOS through the MFA feature."""

    object: Literal["authentication_challenge"]
    id: str
    created_at: str
    updated_at: str
    expires_at: Optional[str] = None
    code: Optional[str] = None
    authentication_factor_id: str


class AuthenticationFactorTotpAndChallengeResponse(WorkOSModel):
    """Representation of an authentication factor and authentication challenge response as returned by WorkOS through User Management features."""

    authentication_factor: AuthenticationFactorTotp
    authentication_challenge: AuthenticationChallenge


class AuthenticationChallengeVerificationResponse(WorkOSModel):
    """Representation of a WorkOS MFA Challenge Verification Response."""

    challenge: AuthenticationChallenge
    valid: bool
