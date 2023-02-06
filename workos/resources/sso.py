import workos
from workos.resources.base import WorkOSBaseResource


class WorkOSProfile(WorkOSBaseResource):
    """Representation of a User Profile as returned by WorkOS through the SSO feature.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSProfile is comprised of.
    """

    OBJECT_FIELDS = [
        "id",
        "email",
        "first_name",
        "last_name",
        "organization_id",
        "connection_id",
        "connection_type",
        "idp_id",
        "raw_attributes",
    ]


class WorkOSProfileAndToken(WorkOSBaseResource):
    """Representation of a User Profile and Access Token as returned by WorkOS through the SSO feature.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSProfileAndToken is comprised of.
    """

    OBJECT_FIELDS = [
        "access_token",
    ]

    @classmethod
    def construct_from_response(cls, response):
        profile_and_token = super(WorkOSProfileAndToken, cls).construct_from_response(
            response
        )

        profile_and_token.profile = WorkOSProfile.construct_from_response(
            response["profile"]
        )

        return profile_and_token

    def to_dict(self):
        profile_and_token_dict = super(WorkOSProfileAndToken, self).to_dict()

        profile_dict = self.profile.to_dict()
        profile_and_token_dict["profile"] = profile_dict

        return profile_and_token_dict


class WorkOSConnection(WorkOSBaseResource):
    """Representation of a Connection Response as returned by WorkOS through the SSO feature.
    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSConnection is comprised of.
    """

    OBJECT_FIELDS = [
        "object",
        "id",
        "organization_id",
        "connection_type",
        "name",
        "state",
        "created_at",
        "updated_at",
        "status",
        "domains",
    ]

    @classmethod
    def construct_from_response(cls, response):
        connection_response = super(WorkOSConnection, cls).construct_from_response(
            response
        )

        return connection_response

    def to_dict(self):
        connection_response_dict = super(WorkOSConnection, self).to_dict()

        return connection_response_dict


class WorkOSConnectionList(WorkOSBaseResource):
    """Representation of a List Connections Response as returned by WorkOS through the SSO feature.
    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSConnectionList is comprised of.
    """

    OBJECT_FIELDS = [
        "data",
        "list_metadata",
    ]

    @classmethod
    def construct_from_response(cls, response):
        connection_response = super(WorkOSConnectionList, cls).construct_from_response(
            response
        )

        return connection_response

    def to_dict(self):
        connection_response_dict = super(WorkOSConnectionList, self).to_dict()

        return connection_response_dict

    def auto_paging_iter(self):
        connections = self.to_dict()["data"]
        before = self.to_dict()["list_metadata"]["before"]

        while before is not None:
            response = workos.client.sso.list_connections(limit=100, before=before)
            for i in response["data"]:
                connections.append(i)
            before = response["list_metadata"]["before"]

        return connections
