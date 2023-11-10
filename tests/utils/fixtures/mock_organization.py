import datetime
from workos.resources.base import WorkOSBaseResource


class MockOrganization(WorkOSBaseResource):
    def __init__(self, id):
        self.id = id
        self.object = "organization"
        self.name = "Foo Corporation"
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()

    OBJECT_FIELDS = [
        "id",
        "object",
        "name",
        "created_at",
        "updated_at",
    ]
