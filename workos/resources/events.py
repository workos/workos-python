from typing import Generic, Literal, TypeVar, Union
from typing_extensions import Annotated
from pydantic import Field
from workos.resources.directory_sync import DirectoryGroup
from workos.resources.workos_model import WorkOSModel
from workos.types.directory_sync.directory_user import DirectoryUser
from workos.types.events.authentication_payload import (
    AuthenticationEmailVerificationSucceededPayload,
    AuthenticationMagicAuthFailedPayload,
    AuthenticationMagicAuthSucceededPayload,
    AuthenticationMfaSucceededPayload,
    AuthenticationOauthSucceededPayload,
    AuthenticationPasswordFailedPayload,
    AuthenticationPasswordSucceededPayload,
    AuthenticationSsoSucceededPayload,
)
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
from workos.types.events.email_verification_payload import EmailVerificationPayload
from workos.types.organizations.organization_common import OrganizationCommon
from workos.types.sso.connection import Connection
from workos.types.user_management.invitation_common import InvitationCommon
from workos.typing.literals import LiteralOrUntyped

EventType = Literal[
    "authentication.email_verification_succeeded",
    "authentication.magic_auth_failed",
    "authentication.magic_auth_succeeded",
    "authentication.mfa_succeeded",
    "authentication.oauth_succeeded",
    "authentication.password_failed",
    "authentication.password_succeeded",
    "authentication.sso_succeeded",
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
    "email_verification.created",
    "invitation.created",
    "organization.created",
    "organization.deleted",
    "organization.updated",
]
EventTypeDiscriminator = TypeVar("EventTypeDiscriminator", bound=EventType)
EventPayload = TypeVar(
    "EventPayload",
    AuthenticationEmailVerificationSucceededPayload,
    AuthenticationMagicAuthFailedPayload,
    AuthenticationMagicAuthSucceededPayload,
    AuthenticationMfaSucceededPayload,
    AuthenticationOauthSucceededPayload,
    AuthenticationPasswordFailedPayload,
    AuthenticationPasswordSucceededPayload,
    AuthenticationSsoSucceededPayload,
    Connection,
    ConnectionPayloadWithLegacyFields,
    DirectoryPayload,
    DirectoryPayloadWithLegacyFields,
    DirectoryGroup,
    DirectoryGroupWithPreviousAttributes,
    DirectoryUser,
    DirectoryUserWithPreviousAttributes,
    DirectoryGroupMembershipPayload,
    EmailVerificationPayload,
    InvitationCommon,
    OrganizationCommon,
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


class AuthenticationEmailVerificationSucceededEvent(
    EventModel[
        Literal["authentication.email_verification_succeeded"],
        AuthenticationEmailVerificationSucceededPayload,
    ]
):
    event: Literal["authentication.email_verification_succeeded"]


class AuthenticationMagicAuthFailedEvent(
    EventModel[
        Literal["authentication.magic_auth_failed"],
        AuthenticationMagicAuthFailedPayload,
    ]
):
    event: Literal["authentication.magic_auth_failed"]


class AuthenticationMagicAuthSucceededEvent(
    EventModel[
        Literal["authentication.magic_auth_succeeded"],
        AuthenticationMagicAuthSucceededPayload,
    ]
):
    event: Literal["authentication.magic_auth_succeeded"]


class AuthenticationMfaSucceededEvent(
    EventModel[
        Literal["authentication.mfa_succeeded"], AuthenticationMfaSucceededPayload
    ]
):
    event: Literal["authentication.mfa_succeeded"]


class AuthenticationOauthSucceededEvent(
    EventModel[
        Literal["authentication.oauth_succeeded"], AuthenticationOauthSucceededPayload
    ]
):
    event: Literal["authentication.oauth_succeeded"]


class AuthenticationPasswordFailedEvent(
    EventModel[
        Literal["authentication.password_failed"], AuthenticationPasswordFailedPayload
    ]
):
    event: Literal["authentication.password_failed"]


class AuthenticationPasswordSucceededEvent(
    EventModel[
        Literal["authentication.password_succeeded"],
        AuthenticationPasswordSucceededPayload,
    ]
):
    event: Literal["authentication.password_succeeded"]


class AuthenticationSsoSucceededEvent(
    EventModel[
        Literal["authentication.sso_succeeded"], AuthenticationSsoSucceededPayload
    ]
):
    event: Literal["authentication.sso_succeeded"]


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


class EmailVerificationCreated(
    EventModel[Literal["email_verification.created"], EmailVerificationPayload]
):
    event: Literal["email_verification.created"]


class InvitationCreated(EventModel[Literal["invitation.created"], InvitationCommon]):
    event: Literal["invitation.created"]


class OrganizationCreated(
    EventModel[Literal["organization.created"], OrganizationCommon]
):
    event: Literal["organization.created"]


class OrganizationDeleted(
    EventModel[Literal["organization.deleted"], OrganizationCommon]
):
    event: Literal["organization.deleted"]


class OrganizationUpdated(
    EventModel[Literal["organization.updated"], OrganizationCommon]
):
    event: Literal["organization.updated"]


Event = Annotated[
    Union[
        AuthenticationEmailVerificationSucceededEvent,
        AuthenticationMagicAuthFailedEvent,
        AuthenticationMagicAuthSucceededEvent,
        AuthenticationMfaSucceededEvent,
        AuthenticationOauthSucceededEvent,
        AuthenticationPasswordFailedEvent,
        AuthenticationPasswordSucceededEvent,
        AuthenticationSsoSucceededEvent,
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
        EmailVerificationCreated,
        InvitationCreated,
        OrganizationCreated,
        OrganizationDeleted,
        OrganizationUpdated,
    ],
    Field(..., discriminator="event"),
]
