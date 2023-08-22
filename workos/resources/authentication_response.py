from workos.resources.base import WorkOSBaseResource
from workos.resources.session import WorkOSSession
from workos.resources.users import WorkOSUser


class WorkOSAuthenticationResponse(WorkOSBaseResource):
    """Representation of a User and Session response as returned by WorkOS through User Management features."""

    @classmethod
    def construct_from_response(cls, response):
        authentication_response = super(
            WorkOSAuthenticationResponse, cls
        ).construct_from_response(response)

        user = WorkOSUser.construct_from_response(response["user"])
        authentication_response.user = user

        session = WorkOSSession.construct_from_response(response["session"])
        authentication_response.session = session

        return authentication_response

    def to_dict(self):
        authentication_response_dict = super(
            WorkOSAuthenticationResponse, self
        ).to_dict()

        user_dict = self.user.to_dict()
        authentication_response_dict["user"] = user_dict

        session_dict = self.session.to_dict()
        authentication_response_dict["session"] = session_dict

        return authentication_response_dict
