import datetime
from workos.resources.base import WorkOSBaseResource


class MockOrganizationMembership(WorkOSBaseResource):
    def __init__(self, id):
        self.id = id
        self.user_id = "user_12345"
        self.organization_id = "org_67890"
        self.status = "active"
        self.role = {"slug": "member"}
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()

    OBJECT_FIELDS = [
        "id",
        "user_id",
        "organization_id",
        "status",
        "role",
        "created_at",
        "updated_at",
    ]
