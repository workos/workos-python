from workos.resources.base import WorkOSBaseResource
from workos.resources.users import WorkOSUser


class WorkOSPasswordChallengeResponse(WorkOSBaseResource):
    """Representation of a User and token response as returned by WorkOS through User Management features.
    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSPasswordChallengeResponse is comprised of.
    """

    OBJECT_FIELDS = [
        "token",
    ]

    @classmethod
    def construct_from_response(cls, response):
        challenge_response = super(
            WorkOSPasswordChallengeResponse, cls
        ).construct_from_response(response)

        user = WorkOSUser.construct_from_response(response["user"])
        challenge_response.user = user

        return challenge_response

    def to_dict(self):
        challenge_response = super(WorkOSPasswordChallengeResponse, self).to_dict()

        user_dict = self.user.to_dict()
        challenge_response["user"] = user_dict

        return challenge_response
