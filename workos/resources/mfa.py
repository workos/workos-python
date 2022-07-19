from workos.resources.base import WorkOSBaseResource


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
