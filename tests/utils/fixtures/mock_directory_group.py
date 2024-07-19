import datetime
from workos.resources.base import WorkOSBaseResource


class MockDirectoryGroup(WorkOSBaseResource):
    def __init__(self, id):
        now = datetime.datetime.now().isoformat()
        self.id = id
        self.idp_id = "idp_id_" + id
        self.directory_id = "directory_id"
        self.organization_id = "organization_id"
        self.name = "group_" + id
        self.created_at = now
        self.updated_at = now
        self.raw_attributes = {}
        self.object = "directory_group"

    OBJECT_FIELDS = [
        "id",
        "idp_id",
        "directory_id",
        "organization_id",
        "name",
        "created_at",
        "updated_at",
        "raw_attributes",
        "object",
    ]
