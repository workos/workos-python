from workos.resources.base import WorkOSBaseResource


class WorkOSPasswordlessSession(WorkOSBaseResource):
    """Representation of a MFA Authentication Factor Response as returned by WorkOS through the MFA feature.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSAuthenticationFactor is comprised of.
    """

    OBJECT_FIELDS = [
        "object",
        "id",
        "email",
        "expires_at",
        "link",
    ]

    @classmethod
    def construct_from_response(cls, response):
        enroll_factor_response = super(
            WorkOSPasswordlessSession, cls
        ).construct_from_response(response)

        return enroll_factor_response

    def to_dict(self):
        challenge_response_dict = super(WorkOSPasswordlessSession, self).to_dict()

        return challenge_response_dict
