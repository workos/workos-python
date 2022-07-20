from workos.resources.base import WorkOSBaseResource


class WorkOSOrganization(WorkOSBaseResource):
    """Representation of a User Profile and Access Token as returned by WorkOS through the SSO feature.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSProfileAndToken is comprised of.
    """

    OBJECT_FIELDS = [
        "id",
        "object",
        "name",
        "allow_profiles_outside_organization",
        "created_at",
        "updated_at",
        "domains",
    ]

    @classmethod
    def construct_from_response(cls, response):
        return super(WorkOSOrganization, cls).construct_from_response(response)

    def to_dict(self):
        organization = super(WorkOSOrganization, self).to_dict()

        return organization
