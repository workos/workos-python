from typing import Literal, Optional, Union
from workos.resources.base import WorkOSBaseResource
from workos.resources.workos_model import WorkOSModel


SmsAuthenticationFactorType = Literal["sms"]
TotpAuthenticationFactorType = Literal["totp"]
AuthenticationFactorType = Literal[
    "generic_otp", SmsAuthenticationFactorType, TotpAuthenticationFactorType
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


class WorkOSAuthenticationFactorTotp(WorkOSBaseResource):
    """Representation of a MFA Authentication Factor Response as returned by WorkOS through the MFA feature.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSAuthenticationFactor is comprised of.
    """

    OBJECT_FIELDS = [
        "object",
        "id",
        "created_at",
        "updated_at",
        "type",
        "totp",
    ]

    @classmethod
    def construct_from_response(cls, response):
        enroll_factor_response = super(
            WorkOSAuthenticationFactorTotp, cls
        ).construct_from_response(response)

        return enroll_factor_response

    def to_dict(self):
        challenge_response_dict = super(WorkOSAuthenticationFactorTotp, self).to_dict()

        return challenge_response_dict


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


class WorkOSAuthenticationFactorSms(WorkOSBaseResource):
    """Representation of a MFA Authentication Factor Response as returned by WorkOS through the MFA feature.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSAuthenticationFactor is comprised of.
    """

    OBJECT_FIELDS = [
        "object",
        "id",
        "created_at",
        "updated_at",
        "type",
        "sms",
    ]

    @classmethod
    def construct_from_response(cls, response):
        enroll_factor_response = super(
            WorkOSAuthenticationFactorSms, cls
        ).construct_from_response(response)

        return enroll_factor_response

    def to_dict(self):
        challenge_response_dict = super(WorkOSAuthenticationFactorSms, self).to_dict()

        return challenge_response_dict


class WorkOSChallenge(WorkOSBaseResource):
    """Representation of a MFA Challenge Response as returned by WorkOS through the MFA feature.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSChallenge is comprised of.
    """

    OBJECT_FIELDS = [
        "object",
        "id",
        "created_at",
        "updated_at",
        "expires_at",
        "authentication_factor_id",
    ]

    @classmethod
    def construct_from_response(cls, response):
        challenge_response = super(WorkOSChallenge, cls).construct_from_response(
            response
        )

        return challenge_response

    def to_dict(self):
        challenge_response_dict = super(WorkOSChallenge, self).to_dict()

        return challenge_response_dict


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


class WorkOSChallengeVerification(WorkOSBaseResource):
    """Representation of a MFA Challenge Verification Response as returned by WorkOS through the MFA feature.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSChallengeVerification is comprised of.
    """

    OBJECT_FIELDS = [
        "challenge",
        "valid",
    ]

    @classmethod
    def construct_from_response(cls, response):
        verification_response = super(
            WorkOSChallengeVerification, cls
        ).construct_from_response(response)

        return verification_response

    def to_dict(self):
        verification_response_dict = super(WorkOSChallengeVerification, self).to_dict()

        return verification_response_dict
