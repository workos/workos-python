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
        self.domains = [
            {
                "domain": "example.io",
                "object": "organization_domain",
                "id": "org_domain_01EHT88Z8WZEFWYPM6EC9BX2R8",
            }
        ]

    OBJECT_FIELDS = [
        "id",
        "object",
        "name",
        "allow_profiles_outside_organization",
        "created_at",
        "updated_at",
        "domains",
        "lookup_key",
    ]
