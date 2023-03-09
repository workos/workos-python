import datetime
from workos.resources.base import WorkOSBaseResource


class MockConnection(WorkOSBaseResource):
    def __init__(self, id):
        self.object = "organization"
        self.id = id
        self.organization_id = "org_id_" + id
        self.connection_type = "Okta"
        self.name = "Foo Corporation"
        self.state = None
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
        self.status = None
        self.domains = ["domain1.com"]

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
