import datetime
from workos.resources.base import WorkOSBaseResource


class MockDirectory(WorkOSBaseResource):
    def __init__(self, id):
        now = datetime.datetime.now().isoformat()
        self.object = "directory"
        self.id = id
        self.organization_id = "organization_id"
        self.domain = "crashlanding.com"
        self.name = "Ri Jeong Hyeok"
        self.state = "linked"
        self.type = "gsuite directory"
        self.created_at = now
        self.updated_at = now

    OBJECT_FIELDS = [
        "object",
        "id",
        "domain",
        "name",
        "organization_id",
        "state",
        "type",
        "created_at",
        "updated_at",
    ]
