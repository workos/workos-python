import datetime
from workos.resources.base import WorkOSBaseResource
from workos.event_objects.directory_user import DirectoryUserEvent


class MockDirectorySyncEvent(WorkOSBaseResource):
    def __init__(self, id):
        self.object = "event"
        self.id = id
        self.event = "dsync.user.created"
        self.data = {
            "id": "directory_user_01E1X1B89NH8Z3SDFJR4H7RGX7",
            "directory_id": "directory_01ECAZ4NV9QMV47GW873HDCX74",
            "organization_id": "org_01EZTR6WYX1A0DSE2CYMGXQ24Y",
            "idp_id": "8931",
            "emails": [
                {"primary": True, "type": "work", "value": "lela.block@example.com"}
            ],
            "first_name": "Lela",
            "last_name": "Block",
            "job_title": "Software Engineer",
            "username": "lela.block@example.com",
            "state": "active",
            "created_at": "2021-06-25T19:07:33.155Z",
            "updated_at": "2021-06-25T19:07:33.155Z",
            "custom_attributes": {"department": "Engineering"},
            "raw_attributes": {},
            "object": "directory_user",
        }

        self.created_at = datetime.datetime.now()

    OBJECT_FIELDS = [
        "object",
        "id",
        "event",
        "data",
        "created_at",
    ]
