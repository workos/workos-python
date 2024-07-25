import datetime
from workos.resources.base import WorkOSBaseResource


class MockConnection(WorkOSBaseResource):
    def __init__(self, id):
        self.object = "connection"
        self.id = id
        self.organization_id = "org_id_" + id
        self.connection_type = "OktaSAML"
        self.name = "Foo Corporation"
        self.state = "active"
        self.created_at = datetime.datetime.now().isoformat()
        self.updated_at = datetime.datetime.now().isoformat()
        self.domains = [
            {
                "id": "connection_domain_abc123",
                "object": "connection_domain",
                "domain": "domain1.com",
            }
        ]

    OBJECT_FIELDS = [
        "object",
        "id",
        "organization_id",
        "connection_type",
        "name",
        "state",
        "created_at",
        "updated_at",
        "domains",
    ]
