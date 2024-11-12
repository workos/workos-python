from typing import Literal, Union
from pydantic import Field
from typing_extensions import Annotated
from workos.types.directory_sync import DirectoryGroup
from workos.types.user_management import OrganizationMembership, User
from workos.types.webhooks.webhook_model import WebhookModel
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
)
from workos.types.events.directory_user_with_previous_attributes import (
    DirectoryUserWithPreviousAttributes,
)
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
# When adding a new webhook event type, ensure the new webhook class is
# added to the Webhook union type at the bottom of this file.


class AuthenticationEmailVerificationSucceededWebhook(
    WebhookModel[AuthenticationEmailVerificationSucceededPayload,]
):
    event: Literal["authentication.email_verification_succeeded"]


class AuthenticationMagicAuthFailedWebhook(
    WebhookModel[AuthenticationMagicAuthFailedPayload,]
):
    event: Literal["authentication.magic_auth_failed"]


class AuthenticationMagicAuthSucceededWebhook(
    WebhookModel[AuthenticationMagicAuthSucceededPayload,]
):
    event: Literal["authentication.magic_auth_succeeded"]


class AuthenticationMfaSucceededWebhook(
    WebhookModel[AuthenticationMfaSucceededPayload]
):
    event: Literal["authentication.mfa_succeeded"]


class AuthenticationOauthFailedWebhook(WebhookModel[AuthenticationOauthFailedPayload]):
    event: Literal["authentication.oauth_failed"]


class AuthenticationOauthSucceededWebhook(
    WebhookModel[AuthenticationOauthSucceededPayload]
):
    event: Literal["authentication.oauth_succeeded"]


class AuthenticationPasswordFailedWebhook(
    WebhookModel[AuthenticationPasswordFailedPayload]
):
    event: Literal["authentication.password_failed"]


class AuthenticationPasswordSucceededWebhook(
    WebhookModel[AuthenticationPasswordSucceededPayload,]
):
    event: Literal["authentication.password_succeeded"]


class AuthenticationSsoFailedWebhook(WebhookModel[AuthenticationSsoFailedPayload]):
    event: Literal["authentication.sso_failed"]


class AuthenticationSsoSucceededWebhook(
    WebhookModel[AuthenticationSsoSucceededPayload]
):
    event: Literal["authentication.sso_succeeded"]


class ConnectionActivatedWebhook(WebhookModel[ConnectionPayloadWithLegacyFields]):
    event: Literal["connection.activated"]


class ConnectionDeactivatedWebhook(WebhookModel[ConnectionPayloadWithLegacyFields]):
    event: Literal["connection.deactivated"]


class ConnectionDeletedWebhook(WebhookModel[Connection]):
    event: Literal["connection.deleted"]


class DirectoryActivatedWebhook(WebhookModel[DirectoryPayloadWithLegacyFields]):
    event: Literal["dsync.activated"]


class DirectoryDeletedWebhook(WebhookModel[DirectoryPayload]):
    event: Literal["dsync.deleted"]


class DirectoryGroupCreatedWebhook(WebhookModel[DirectoryGroup]):
    event: Literal["dsync.group.created"]


class DirectoryGroupDeletedWebhook(WebhookModel[DirectoryGroup]):
    event: Literal["dsync.group.deleted"]


class DirectoryGroupUpdatedWebhook(WebhookModel[DirectoryGroupWithPreviousAttributes]):
    event: Literal["dsync.group.updated"]


class DirectoryUserCreatedWebhook(WebhookModel[DirectoryUser]):
    event: Literal["dsync.user.created"]


class DirectoryUserDeletedWebhook(WebhookModel[DirectoryUser]):
    event: Literal["dsync.user.deleted"]


class DirectoryUserUpdatedWebhook(WebhookModel[DirectoryUserWithPreviousAttributes]):
    event: Literal["dsync.user.updated"]


class DirectoryUserAddedToGroupWebhook(WebhookModel[DirectoryGroupMembershipPayload]):
    event: Literal["dsync.group.user_added"]


class DirectoryUserRemovedFromGroupWebhook(
    WebhookModel[DirectoryGroupMembershipPayload]
):
    event: Literal["dsync.group.user_removed"]


class EmailVerificationCreatedWebhook(WebhookModel[EmailVerificationCommon]):
    event: Literal["email_verification.created"]


class InvitationCreatedWebhook(WebhookModel[InvitationCommon]):
    event: Literal["invitation.created"]


class MagicAuthCreatedWebhook(WebhookModel[MagicAuthCommon]):
    event: Literal["magic_auth.created"]


class OrganizationCreatedWebhook(WebhookModel[OrganizationCommon]):
    event: Literal["organization.created"]


class OrganizationDeletedWebhook(WebhookModel[OrganizationCommon]):
    event: Literal["organization.deleted"]


class OrganizationUpdatedWebhook(WebhookModel[OrganizationCommon]):
    event: Literal["organization.updated"]


class OrganizationDomainVerificationFailedWebhook(
    WebhookModel[OrganizationDomainVerificationFailedPayload,]
):
    event: Literal["organization_domain.verification_failed"]


class OrganizationDomainVerifiedWebhook(WebhookModel[OrganizationDomain]):
    event: Literal["organization_domain.verified"]


class OrganizationMembershipCreatedWebhook(WebhookModel[OrganizationMembership]):
    event: Literal["organization_membership.created"]


class OrganizationMembershipDeletedWebhook(WebhookModel[OrganizationMembership]):
    event: Literal["organization_membership.deleted"]


class OrganizationMembershipUpdatedWebhook(WebhookModel[OrganizationMembership]):
    event: Literal["organization_membership.updated"]


class PasswordResetCreatedWebhook(WebhookModel[PasswordResetCommon]):
    event: Literal["password_reset.created"]


class RoleCreatedWebhook(WebhookModel[Role]):
    event: Literal["role.created"]


class RoleDeletedWebhook(WebhookModel[Role]):
    event: Literal["role.deleted"]


class RoleUpdatedWebhook(WebhookModel[Role]):
    event: Literal["role.updated"]


class SessionCreatedWebhook(WebhookModel[SessionCreatedPayload]):
    event: Literal["session.created"]


class UserCreatedWebhook(WebhookModel[User]):
    event: Literal["user.created"]


class UserDeletedWebhook(WebhookModel[User]):
    event: Literal["user.deleted"]


class UserUpdatedWebhook(WebhookModel[User]):
    event: Literal["user.updated"]


Webhook = Annotated[
    Union[
        AuthenticationEmailVerificationSucceededWebhook,
        AuthenticationMagicAuthFailedWebhook,
        AuthenticationMagicAuthSucceededWebhook,
        AuthenticationMfaSucceededWebhook,
        AuthenticationOauthFailedWebhook,
        AuthenticationOauthSucceededWebhook,
        AuthenticationPasswordFailedWebhook,
        AuthenticationPasswordSucceededWebhook,
        AuthenticationSsoFailedWebhook,
        AuthenticationSsoSucceededWebhook,
        ConnectionActivatedWebhook,
        ConnectionDeactivatedWebhook,
        ConnectionDeletedWebhook,
        DirectoryActivatedWebhook,
        DirectoryDeletedWebhook,
        DirectoryGroupCreatedWebhook,
        DirectoryGroupDeletedWebhook,
        DirectoryGroupUpdatedWebhook,
        DirectoryUserCreatedWebhook,
        DirectoryUserDeletedWebhook,
        DirectoryUserUpdatedWebhook,
        DirectoryUserAddedToGroupWebhook,
        DirectoryUserRemovedFromGroupWebhook,
        EmailVerificationCreatedWebhook,
        InvitationCreatedWebhook,
        MagicAuthCreatedWebhook,
        OrganizationCreatedWebhook,
        OrganizationDeletedWebhook,
        OrganizationUpdatedWebhook,
        OrganizationDomainVerificationFailedWebhook,
        OrganizationDomainVerifiedWebhook,
        OrganizationMembershipCreatedWebhook,
        OrganizationMembershipDeletedWebhook,
        OrganizationMembershipUpdatedWebhook,
        PasswordResetCreatedWebhook,
        RoleCreatedWebhook,
        RoleDeletedWebhook,
        RoleUpdatedWebhook,
        SessionCreatedWebhook,
        UserCreatedWebhook,
        UserDeletedWebhook,
        UserUpdatedWebhook,
    ],
    Field(..., discriminator="event"),
]
