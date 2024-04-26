import datetime
from workos.resources.base import WorkOSBaseResource


class MockEvent(WorkOSBaseResource):
    def __init__(self, id):
        self.object = "event"
        self.id = id
        self.event = "dsync.user.created"
        self.data = {
            "id": "event_01234ABCD",
            "organization_id": "org_1234"
        }
        self.created_at = datetime.datetime.now()

    OBJECT_FIELDS = [
        "object",
        "id",
        "event",
        "data",
        "created_at",
    ]
