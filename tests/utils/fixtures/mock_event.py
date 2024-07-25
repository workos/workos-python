import datetime
from tests.utils.fixtures.mock_directory import MockDirectory
from tests.utils.fixtures.mock_directory_activated_payload import (
    MockDirectoryActivatedPayload,
)
from workos.resources.base import WorkOSBaseResource


class MockEvent(WorkOSBaseResource):
    def __init__(self, id):
        self.object = "event"
        self.id = id
        self.event = "dsync.activated"
        self.data = MockDirectoryActivatedPayload("dir_1234").to_dict()
        self.created_at = datetime.datetime.now().isoformat()

    OBJECT_FIELDS = [
        "object",
        "id",
        "event",
        "data",
        "created_at",
    ]
