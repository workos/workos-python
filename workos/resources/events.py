from typing import Generic, Literal, TypeVar, Union
from typing_extensions import Annotated
from pydantic import Field
from workos.resources.workos_model import WorkOSModel
from workos.types.directory_sync.directory_group import DirectoryGroup
from workos.types.directory_sync.directory_user import DirectoryUser
from workos.types.events.directory_group_with_previous_attributes import (
    DirectoryGroupWithPreviousAttributes,
)
from workos.types.events.directory_payload import DirectoryPayload
from workos.types.events.directory_payload_with_legacy_fields import (
    DirectoryPayloadWithLegacyFields,
)
from workos.types.events.directory_user_with_previous_attributes import (
    DirectoryUserWithPreviousAttributes,
)
from workos.typing.literals import LiteralOrUntyped

EventType = Literal[
    "dsync.activated",
    "dsync.deleted",
    "dsync.group.created",
    "dsync.group.deleted",
    "dsync.group.updated",
    "dsync.user.created",
    "dsync.user.deleted",
    "dsync.user.updated",
]
EventTypeDiscriminator = TypeVar("EventTypeDiscriminator", bound=EventType)
EventPayload = TypeVar(
    "EventPayload",
    DirectoryPayload,
    DirectoryPayloadWithLegacyFields,
    DirectoryGroup,
    DirectoryGroupWithPreviousAttributes,
    DirectoryUser,
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


class DirectoryGroupCreatedEvent(
    EventModel[Literal["dsync.group.created"], DirectoryGroup]
):
    event: Literal["dsync.group.created"]


class DirectoryGroupDeletedEvent(
    EventModel[Literal["dsync.group.deleted"], DirectoryGroup]
):
    event: Literal["dsync.group.deleted"]


class DirectoryGroupUpdatedEvent(
    EventModel[Literal["dsync.group.updated"], DirectoryGroupWithPreviousAttributes]
):
    event: Literal["dsync.group.updated"]


class DirectoryUserCreatedEvent(
    EventModel[Literal["dsync.user.created"], DirectoryUser]
):
    event: Literal["dsync.user.created"]


class DirectoryUserDeletedEvent(
    EventModel[Literal["dsync.user.deleted"], DirectoryUser]
):
    event: Literal["dsync.user.deleted"]


class DirectoryUserUpdatedEvent(
    EventModel[Literal["dsync.user.updated"], DirectoryUserWithPreviousAttributes]
):
    event: Literal["dsync.user.updated"]


Event = Annotated[
    Union[
        DirectoryActivatedEvent,
        DirectoryDeletedEvent,
        DirectoryGroupCreatedEvent,
        DirectoryGroupDeletedEvent,
        DirectoryGroupUpdatedEvent,
    ],
    Field(..., discriminator="event"),
]
