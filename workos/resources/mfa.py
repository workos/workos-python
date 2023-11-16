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

class WorkOSAuthenticationChallengeAndFactor(WorkOSBaseResource):
    """Representation of an Authentication Challenge and Factor as returned by WorkOS through the User Management feature.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSAuthenticationChallengeAndFactor is comprised of.
    """

    OBJECT_FIELDS = [
        "authentication_challenge",
        "authentication_factor",
    ]

    @classmethod
    def construct_from_response(cls, response):
        authentication_challenge_and_factor = super(WorkOSAuthenticationChallengeAndFactor, cls).construct_from_response(
            response
        )

        authentication_challenge_and_factor.authentication_challenge = WorkOSChallenge.construct_from_response(
            response["authentication_challenge"]
        )

        authentication_challenge_and_factor.authentication_factor = WorkOSAuthenticationFactorTotp.construct_from_response(
            response["authentication_factor"]
        )

        return authentication_challenge_and_factor

    def to_dict(self):
        authentication_challenge_and_factor_dict = super(WorkOSAuthenticationChallengeAndFactor, self).to_dict()

        challenge_dict = self.authentication_challenge.to_dict()
        authentication_challenge_and_factor_dict["authentication_challenge"] = challenge_dict

        factor_dict = self.authentication_factor.to_dict()
        authentication_challenge_and_factor_dict["authentication_factor"] = factor_dict

        return authentication_challenge_and_factor_dict
