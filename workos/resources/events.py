from typing import Generic, Literal, TypeVar, Union
from typing_extensions import Annotated
from pydantic import Field
from workos.resources.workos_model import WorkOSModel
from workos.types.events.directory_payload import DirectoryPayload
from workos.types.events.directory_payload_with_legacy_fields import (
    DirectoryPayloadWithLegacyFields,
)
from workos.typing.literals import LiteralOrUntyped

EventType = Literal["dsync.activated", "dsync.deleted"]
EventTypeDiscriminator = TypeVar("EventTypeDiscriminator", bound=EventType)
EventPayload = TypeVar(
    "EventPayload", DirectoryPayload, DirectoryPayloadWithLegacyFields
)


class EventModel(WorkOSModel, Generic[EventTypeDiscriminator, EventPayload]):
    # TODO: fix these docs
    """Representation of an Event returned from the Events API or via Webhook.
    Attributes:
        OBJECT_FIELDS (list): List of fields an Event is comprised of.
    """

    id: str
    object: Literal["event"]
    event: LiteralOrUntyped[EventTypeDiscriminator]
    data: EventPayload
    created_at: str


class DirectoryActivatedEvent(
    EventModel[Literal["dsync.activated"], DirectoryPayloadWithLegacyFields]
):
    event: Literal["dsync.activated"]


class DirectoryDeletedEvent(EventModel[Literal["dsync.deleted"], DirectoryPayload]):
    event: Literal["dsync.deleted"]


Event = Annotated[
    Union[DirectoryActivatedEvent, DirectoryDeletedEvent],
    Field(..., discriminator="event"),
]
