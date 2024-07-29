from typing import Generic, Literal, TypeVar, Union
from typing_extensions import Annotated
from pydantic import Field
from workos.resources.directory_sync import DirectoryGroup
from workos.resources.workos_model import WorkOSModel
from workos.types.directory_sync.directory_user import DirectoryUser
from workos.types.events.connection_payload_with_legacy_fields import (
    ConnectionPayloadWithLegacyFields,
)
from workos.types.events.directory_group_membership_payload import (
    DirectoryGroupMembershipPayload,
)
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
from workos.types.sso.connection import Connection
from workos.typing.literals import LiteralOrUntyped

EventType = Literal[
    "connection.activated",
    "connection.deactivated",
    "connection.deleted",
    "dsync.activated",
    "dsync.deleted",
    "dsync.group.created",
    "dsync.group.deleted",
    "dsync.group.updated",
    "dsync.user.created",
    "dsync.user.deleted",
    "dsync.user.updated",
    "dsync.group.user_added",
    "dsync.group.user_removed",
]
EventTypeDiscriminator = TypeVar("EventTypeDiscriminator", bound=EventType)
EventPayload = TypeVar(
    "EventPayload",
    Connection,
    ConnectionPayloadWithLegacyFields,
    DirectoryPayload,
    DirectoryPayloadWithLegacyFields,
    DirectoryGroup,
    DirectoryGroupWithPreviousAttributes,
    DirectoryUser,
    DirectoryUserWithPreviousAttributes,
    DirectoryGroupMembershipPayload,
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


class ConnectionActivatedEvent(
    EventModel[Literal["connection.activated"], ConnectionPayloadWithLegacyFields]
):
    event: Literal["connection.activated"]


class ConnectionDeactivatedEvent(
    EventModel[Literal["connection.deactivated"], ConnectionPayloadWithLegacyFields]
):
    event: Literal["connection.deactivated"]


class ConnectionDeletedEvent(EventModel[Literal["connection.deleted"], Connection]):
    event: Literal["connection.deleted"]


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


class DirectoryUserAddedToGroupEvent(
    EventModel[Literal["dsync.group.user_added"], DirectoryGroupMembershipPayload]
):
    event: Literal["dsync.group.user_added"]


class DirectoryUserRemovedFromGroupEvent(
    EventModel[Literal["dsync.group.user_removed"], DirectoryGroupMembershipPayload]
):
    event: Literal["dsync.group.user_removed"]


Event = Annotated[
    Union[
        ConnectionActivatedEvent,
        ConnectionDeactivatedEvent,
        ConnectionDeletedEvent,
        DirectoryActivatedEvent,
        DirectoryDeletedEvent,
        DirectoryGroupCreatedEvent,
        DirectoryGroupDeletedEvent,
        DirectoryGroupUpdatedEvent,
        DirectoryUserCreatedEvent,
        DirectoryUserDeletedEvent,
        DirectoryUserUpdatedEvent,
        DirectoryUserAddedToGroupEvent,
        DirectoryUserRemovedFromGroupEvent,
    ],
    Field(..., discriminator="event"),
]
