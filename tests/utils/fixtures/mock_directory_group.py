import datetime
from workos.resources.base import WorkOSBaseResource


class MockDirectoryGroup(WorkOSBaseResource):
    def __init__(self, id):
        self.id = id
        self.idp_id = "idp_id_" + id
        self.directory_id = "directory_id"
        self.name = "group_" + id
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
        self.raw_attributes = None
        self.object = "directory_group"

    OBJECT_FIELDS = [
        "id",
        "idp_id",
        "directory_id",
        "name",
        "created_at",
        "updated_at",
        "raw_attributes",
        "object",
    ]
