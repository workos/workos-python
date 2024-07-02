import datetime
from workos.resources.base import WorkOSBaseResource


class MockEvent(WorkOSBaseResource):
    def __init__(self, id):
        self.object = "event"
        self.id = id
        self.event = "user.created"
        self.data = {
            "id": "user_01E4ZCR3C5A4QZ2Z2JQXGKZJ9E",
            "email": "todd@example.com",
        }
        self.created_at = datetime.datetime.now()

    OBJECT_FIELDS = [
        "object",
        "id",
        "event",
        "data",
        "created_at",
    ]
