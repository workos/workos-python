from workos.resources.base import WorkOSBaseResource


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
        "code",
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
