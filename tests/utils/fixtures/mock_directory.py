import datetime
from workos.resources.base import WorkOSBaseResource


class MockDirectory(WorkOSBaseResource):
    def __init__(self, id):
        self.object = "directory"
        self.id = id
        self.domain = "crashlanding.com"
        self.name = "Ri Jeong Hyeok"
        self.state = None
        self.type = "gsuite_directory"
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()

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
