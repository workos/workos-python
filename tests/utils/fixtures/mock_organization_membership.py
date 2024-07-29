import datetime
from workos.resources.base import WorkOSBaseResource


class MockOrganizationMembership(WorkOSBaseResource):
    def __init__(self, id):
        now = datetime.datetime.now().isoformat()
        self.object = "organization_membership"
        self.id = id
        self.user_id = "user_12345"
        self.organization_id = "org_67890"
        self.status = "active"
        self.role = {"slug": "member"}
        self.created_at = now
        self.updated_at = now

    OBJECT_FIELDS = [
        "object",
        "id",
        "user_id",
        "organization_id",
        "status",
        "role",
        "created_at",
        "updated_at",
    ]
