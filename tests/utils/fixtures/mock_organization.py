import datetime
from workos.resources.base import WorkOSBaseResource


class MockOrganization(WorkOSBaseResource):
    def __init__(self, id):
        self.id = id
        self.object = "organization"
        self.name = "Foo Corporation"
        self.allow_profiles_outside_organization = False
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
        self.domains = ["domain1.com"]

    OBJECT_FIELDS = [
        "id",
        "object",
        "name",
        "allow_profiles_outside_organization",
        "created_at",
        "updated_at",
        "domains",
    ]
