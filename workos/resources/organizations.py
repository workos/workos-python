import workos
from workos.resources.base import WorkOSBaseResource


class WorkOSOrganization(WorkOSBaseResource):
    """Representation of WorkOS Organization as returned by WorkOS through the Organizations feature.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSOrganization is comprised of.
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


class WorkOSOrganizationList(WorkOSBaseResource):
    """Representation of a list of WorkOS Organizations as returned by WorkOS through the Organizations feature.

    Attributes:
        OBJECT_FIELDS (list): List of fields a WorkOSOrganizationList is comprised of.
    """

    OBJECT_FIELDS = [
        "data",
        "list_metadata",
    ]

    @classmethod
    def construct_from_response(cls, response):
        return super(WorkOSOrganizationList, cls).construct_from_response(response)

    def to_dict(self):
        organizations = super(WorkOSOrganizationList, self).to_dict()

        return organizations

    def auto_paging_iter(self):
        organizations = self.to_dict()["data"]
        before = self.to_dict()["list_metadata"]["before"]

        while before is not None:
            response = workos.client.organizations.list_organizations(
                limit=100, before=before
            )
            for i in response["data"]:
                organizations.append(i)
            before = response["list_metadata"]["before"]

        return organizations
