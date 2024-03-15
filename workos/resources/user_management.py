from workos.resources.base import WorkOSBaseResource


class WorkOSAuthenticationResponse(WorkOSBaseResource):
    """Representation of a User and Organization ID response as returned by WorkOS through User Management features."""

    """Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSAuthenticationResponse comprises.
    """

    OBJECT_FIELDS = [
        "organization_id",
    ]

    @classmethod
    def construct_from_response(cls, response):
        authentication_response = super(
            WorkOSAuthenticationResponse, cls
        ).construct_from_response(response)

        user = WorkOSUser.construct_from_response(response["user"])
        authentication_response.user = user

        return authentication_response

    def to_dict(self):
        authentication_response_dict = super(
            WorkOSAuthenticationResponse, self
        ).to_dict()

        user_dict = self.user.to_dict()
        authentication_response_dict["user"] = user_dict

        return authentication_response_dict


class WorkOSInvitation(WorkOSBaseResource):
    """Representation of an Invitation as returned by WorkOS through User Management features.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSInvitation comprises.
    """

    OBJECT_FIELDS = [
        "id",
        "email",
        "state",
        "accepted_at",
        "revoked_at",
        "expires_at",
        "token",
        "organization_id",
        "created_at",
        "updated_at",
    ]


class WorkOSOrganizationMembership(WorkOSBaseResource):
    """Representation of an Organization Membership as returned by WorkOS through User Management features.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSOrganizationMembership comprises.
    """

    OBJECT_FIELDS = [
        "id",
        "user_id",
        "organization_id",
        "status",
        "created_at",
        "updated_at",
        "role",
    ]


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


class WorkOSUser(WorkOSBaseResource):
    """Representation of a User as returned by WorkOS through User Management features.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSUser comprises.
    """

    OBJECT_FIELDS = [
        "id",
        "email",
        "first_name",
        "last_name",
        "email_verified",
        "profile_picture_url",
        "created_at",
        "updated_at",
    ]
