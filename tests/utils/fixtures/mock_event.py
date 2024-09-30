import datetime

from workos.types.events import DirectoryActivatedEvent
from workos.types.events.directory_payload_with_legacy_fields import (
    DirectoryPayloadWithLegacyFields,
    DirectoryPayloadWithLegacyFieldsForEventsApi,
)


class MockEvent(DirectoryActivatedEvent):
    def __init__(self, id):
        now = datetime.datetime.now().isoformat()
        super().__init__(
            object="event",
            id=id,
            event="dsync.activated",
            data=DirectoryPayloadWithLegacyFieldsForEventsApi(
                object="directory",
                id="dir_1234",
                organization_id="organization_id",
                external_key="ext_123",
                domains=[],
                name="Some fake name",
                state="active",
                type="gsuite directory",
                created_at=now,
                updated_at=now,
            ),
            created_at=now,
        )
