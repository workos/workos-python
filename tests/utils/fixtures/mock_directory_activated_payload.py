import datetime
from workos.resources.base import WorkOSBaseResource


class MockDirectoryActivatedPayload(WorkOSBaseResource):
    def __init__(self, id):
        now = datetime.datetime.now().isoformat()
        self.object = "directory"
        self.id = id
        self.organization_id = "organization_id"
        self.external_key = "ext_123"
        self.domains = []
        self.name = "Some fake name"
        self.state = "active"
        self.type = "gsuite directory"
        self.created_at = now
        self.updated_at = now

    OBJECT_FIELDS = [
        "object",
        "id",
        "name",
        "external_key",
        "domains",
        "organization_id",
        "state",
        "type",
        "created_at",
        "updated_at",
    ]
