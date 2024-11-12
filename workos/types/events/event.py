from typing import Literal, Union
from pydantic import Field
from typing_extensions import Annotated
from workos.types.user_management import OrganizationMembership, User
from workos.types.directory_sync.directory_group import DirectoryGroup
from workos.types.directory_sync.directory_user import DirectoryUser
from workos.types.events.authentication_payload import (
    AuthenticationEmailVerificationSucceededPayload,
    AuthenticationMagicAuthFailedPayload,
    AuthenticationMagicAuthSucceededPayload,
    AuthenticationMfaSucceededPayload,
    AuthenticationOauthFailedPayload,
    AuthenticationOauthSucceededPayload,
    AuthenticationPasswordFailedPayload,
    AuthenticationPasswordSucceededPayload,
    AuthenticationSsoFailedPayload,
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
    DirectoryPayloadWithLegacyFieldsForEventsApi,
)
from workos.types.events.directory_user_with_previous_attributes import (
    DirectoryUserWithPreviousAttributes,
)
from workos.types.events.event_model import EventModel
from workos.types.events.organization_domain_verification_failed_payload import (
    OrganizationDomainVerificationFailedPayload,
)
from workos.types.events.session_created_payload import SessionCreatedPayload
from workos.types.organizations.organization_common import OrganizationCommon
from workos.types.organizations.organization_domain import OrganizationDomain
from workos.types.roles.role import Role
from workos.types.sso.connection import Connection
from workos.types.user_management.email_verification import (
    EmailVerificationCommon,
)
from workos.types.user_management.invitation import InvitationCommon
from workos.types.user_management.magic_auth import MagicAuthCommon
from workos.types.user_management.password_reset import PasswordResetCommon


# README
# When adding a new event type, ensure the new event class is
# added to the Event union type at the bottom of this file, and
# the event name is added to the EventType union type in event_type.py.


class AuthenticationEmailVerificationSucceededEvent(
    EventModel[AuthenticationEmailVerificationSucceededPayload,]
):
    event: Literal["authentication.email_verification_succeeded"]


class AuthenticationMagicAuthFailedEvent(
    EventModel[AuthenticationMagicAuthFailedPayload,]
):
    event: Literal["authentication.magic_auth_failed"]


class AuthenticationMagicAuthSucceededEvent(
    EventModel[AuthenticationMagicAuthSucceededPayload,]
):
    event: Literal["authentication.magic_auth_succeeded"]


class AuthenticationMfaSucceededEvent(EventModel[AuthenticationMfaSucceededPayload]):
    event: Literal["authentication.mfa_succeeded"]


class AuthenticationOauthFailedEvent(EventModel[AuthenticationOauthFailedPayload]):
    event: Literal["authentication.oauth_failed"]


class AuthenticationOauthSucceededEvent(
    EventModel[AuthenticationOauthSucceededPayload]
):
    event: Literal["authentication.oauth_succeeded"]


class AuthenticationPasswordFailedEvent(
    EventModel[AuthenticationPasswordFailedPayload]
):
    event: Literal["authentication.password_failed"]


class AuthenticationPasswordSucceededEvent(
    EventModel[AuthenticationPasswordSucceededPayload,]
):
    event: Literal["authentication.password_succeeded"]


class AuthenticationSsoFailedEvent(EventModel[AuthenticationSsoFailedPayload]):
    event: Literal["authentication.sso_failed"]


class AuthenticationSsoSucceededEvent(EventModel[AuthenticationSsoSucceededPayload]):
    event: Literal["authentication.sso_succeeded"]


class ConnectionActivatedEvent(EventModel[ConnectionPayloadWithLegacyFields]):
    event: Literal["connection.activated"]


class ConnectionDeactivatedEvent(EventModel[ConnectionPayloadWithLegacyFields]):
    event: Literal["connection.deactivated"]


class ConnectionDeletedEvent(EventModel[Connection]):
    event: Literal["connection.deleted"]


class DirectoryActivatedEvent(EventModel[DirectoryPayloadWithLegacyFieldsForEventsApi]):
    event: Literal["dsync.activated"]


class DirectoryDeletedEvent(EventModel[DirectoryPayload]):
    event: Literal["dsync.deleted"]


class DirectoryGroupCreatedEvent(EventModel[DirectoryGroup]):
    event: Literal["dsync.group.created"]


class DirectoryGroupDeletedEvent(EventModel[DirectoryGroup]):
    event: Literal["dsync.group.deleted"]


class DirectoryGroupUpdatedEvent(EventModel[DirectoryGroupWithPreviousAttributes]):
    event: Literal["dsync.group.updated"]


class DirectoryUserCreatedEvent(EventModel[DirectoryUser]):
    event: Literal["dsync.user.created"]


class DirectoryUserDeletedEvent(EventModel[DirectoryUser]):
    event: Literal["dsync.user.deleted"]


class DirectoryUserUpdatedEvent(EventModel[DirectoryUserWithPreviousAttributes]):
    event: Literal["dsync.user.updated"]


class DirectoryUserAddedToGroupEvent(EventModel[DirectoryGroupMembershipPayload]):
    event: Literal["dsync.group.user_added"]


class DirectoryUserRemovedFromGroupEvent(EventModel[DirectoryGroupMembershipPayload]):
    event: Literal["dsync.group.user_removed"]


class EmailVerificationCreatedEvent(EventModel[EmailVerificationCommon]):
    event: Literal["email_verification.created"]


class InvitationCreatedEvent(EventModel[InvitationCommon]):
    event: Literal["invitation.created"]


class MagicAuthCreatedEvent(EventModel[MagicAuthCommon]):
    event: Literal["magic_auth.created"]


class OrganizationCreatedEvent(EventModel[OrganizationCommon]):
    event: Literal["organization.created"]


class OrganizationDeletedEvent(EventModel[OrganizationCommon]):
    event: Literal["organization.deleted"]


class OrganizationUpdatedEvent(EventModel[OrganizationCommon]):
    event: Literal["organization.updated"]


class OrganizationDomainVerificationFailedEvent(
    EventModel[OrganizationDomainVerificationFailedPayload,]
):
    event: Literal["organization_domain.verification_failed"]


class OrganizationDomainVerifiedEvent(EventModel[OrganizationDomain]):
    event: Literal["organization_domain.verified"]


class OrganizationMembershipCreatedEvent(EventModel[OrganizationMembership]):
    event: Literal["organization_membership.created"]


class OrganizationMembershipDeletedEvent(EventModel[OrganizationMembership]):
    event: Literal["organization_membership.deleted"]


class OrganizationMembershipUpdatedEvent(EventModel[OrganizationMembership]):
    event: Literal["organization_membership.updated"]


class PasswordResetCreatedEvent(EventModel[PasswordResetCommon]):
    event: Literal["password_reset.created"]


class RoleCreatedEvent(EventModel[Role]):
    event: Literal["role.created"]


class RoleDeletedEvent(EventModel[Role]):
    event: Literal["role.deleted"]


class RoleUpdatedEvent(EventModel[Role]):
    event: Literal["role.updated"]


class SessionCreatedEvent(EventModel[SessionCreatedPayload]):
    event: Literal["session.created"]


class UserCreatedEvent(EventModel[User]):
    event: Literal["user.created"]


class UserDeletedEvent(EventModel[User]):
    event: Literal["user.deleted"]


class UserUpdatedEvent(EventModel[User]):
    event: Literal["user.updated"]


Event = Annotated[
    Union[
        AuthenticationEmailVerificationSucceededEvent,
        AuthenticationMagicAuthFailedEvent,
        AuthenticationMagicAuthSucceededEvent,
        AuthenticationMfaSucceededEvent,
        AuthenticationOauthFailedEvent,
        AuthenticationOauthSucceededEvent,
        AuthenticationPasswordFailedEvent,
        AuthenticationPasswordSucceededEvent,
        AuthenticationSsoFailedEvent,
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
        EmailVerificationCreatedEvent,
        InvitationCreatedEvent,
        MagicAuthCreatedEvent,
        OrganizationCreatedEvent,
        OrganizationDeletedEvent,
        OrganizationUpdatedEvent,
        OrganizationDomainVerificationFailedEvent,
        OrganizationDomainVerifiedEvent,
        OrganizationMembershipCreatedEvent,
        OrganizationMembershipDeletedEvent,
        OrganizationMembershipUpdatedEvent,
        PasswordResetCreatedEvent,
        RoleCreatedEvent,
        RoleDeletedEvent,
        RoleUpdatedEvent,
        SessionCreatedEvent,
        UserCreatedEvent,
        UserDeletedEvent,
        UserUpdatedEvent,
    ],
    Field(..., discriminator="event"),
]
