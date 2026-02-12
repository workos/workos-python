from typing import Literal, Union

from pydantic import Field
from typing_extensions import Annotated

from workos.types.directory_sync import DirectoryGroup
from workos.types.directory_sync.directory_user import DirectoryUser
from workos.types.api_keys import ApiKey
from workos.types.events.authentication_payload import (
    AuthenticationEmailVerificationFailedPayload,
    AuthenticationEmailVerificationSucceededPayload,
    AuthenticationMagicAuthFailedPayload,
    AuthenticationMagicAuthSucceededPayload,
    AuthenticationMfaFailedPayload,
    AuthenticationMfaSucceededPayload,
    AuthenticationOauthFailedPayload,
    AuthenticationOauthSucceededPayload,
    AuthenticationPasskeyFailedPayload,
    AuthenticationPasskeySucceededPayload,
    AuthenticationPasswordFailedPayload,
    AuthenticationPasswordSucceededPayload,
    AuthenticationRadarRiskDetectedPayload,
    AuthenticationSsoFailedPayload,
    AuthenticationSsoSucceededPayload,
)
from workos.types.events.connection_payload_with_legacy_fields import (
    ConnectionPayloadWithLegacyFields,
)
from workos.types.events.connection_saml_certificate_payload import (
    ConnectionSamlCertificateRenewedPayload,
    ConnectionSamlCertificateRenewalRequiredPayload,
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
from workos.types.events.flag_payload import FlagPayload, FlagRuleUpdatedContext
from workos.types.events.organization_domain_verification_failed_payload import (
    OrganizationDomainVerificationFailedPayload,
)
from workos.types.events.organization_role_payload import OrganizationRolePayload
from workos.types.events.permission_payload import PermissionPayload
from workos.types.events.session_payload import (
    SessionCreatedPayload,
    SessionRevokedPayload,
)
from workos.types.organization_domains import OrganizationDomain
from workos.types.organizations.organization_common import OrganizationCommon
from workos.types.roles.role import EventRole
from workos.types.sso.connection import Connection
from workos.types.user_management import OrganizationMembership, User
from workos.types.user_management.email_verification import (
    EmailVerificationCommon,
)
from workos.types.user_management.invitation import InvitationCommon
from workos.types.user_management.magic_auth import MagicAuthCommon
from workos.types.user_management.password_reset import PasswordResetCommon
from workos.types.webhooks.webhook_model import WebhookModel

# README
# When adding a new webhook event type, ensure the new webhook class is
# added to the Webhook union type at the bottom of this file.


class ApiKeyCreatedWebhook(WebhookModel[ApiKey]):
    event: Literal["api_key.created"]


class ApiKeyRevokedWebhook(WebhookModel[ApiKey]):
    event: Literal["api_key.revoked"]


class AuthenticationEmailVerificationFailedWebhook(
    WebhookModel[AuthenticationEmailVerificationFailedPayload,]
):
    event: Literal["authentication.email_verification_failed"]


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


class AuthenticationMfaFailedWebhook(WebhookModel[AuthenticationMfaFailedPayload]):
    event: Literal["authentication.mfa_failed"]


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


class AuthenticationPasskeyFailedWebhook(
    WebhookModel[AuthenticationPasskeyFailedPayload]
):
    event: Literal["authentication.passkey_failed"]


class AuthenticationPasskeySucceededWebhook(
    WebhookModel[AuthenticationPasskeySucceededPayload]
):
    event: Literal["authentication.passkey_succeeded"]


class AuthenticationPasswordFailedWebhook(
    WebhookModel[AuthenticationPasswordFailedPayload]
):
    event: Literal["authentication.password_failed"]


class AuthenticationPasswordSucceededWebhook(
    WebhookModel[AuthenticationPasswordSucceededPayload,]
):
    event: Literal["authentication.password_succeeded"]


class AuthenticationRadarRiskDetectedWebhook(
    WebhookModel[AuthenticationRadarRiskDetectedPayload]
):
    event: Literal["authentication.radar_risk_detected"]


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


class ConnectionSamlCertificateRenewedWebhook(
    WebhookModel[ConnectionSamlCertificateRenewedPayload]
):
    event: Literal["connection.saml_certificate_renewed"]


class ConnectionSamlCertificateRenewalRequiredWebhook(
    WebhookModel[ConnectionSamlCertificateRenewalRequiredPayload]
):
    event: Literal["connection.saml_certificate_renewal_required"]


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


class FlagCreatedWebhook(WebhookModel[FlagPayload]):
    event: Literal["flag.created"]


class FlagDeletedWebhook(WebhookModel[FlagPayload]):
    event: Literal["flag.deleted"]


class FlagRuleUpdatedWebhook(WebhookModel[FlagPayload]):
    event: Literal["flag.rule_updated"]
    context: FlagRuleUpdatedContext


class FlagUpdatedWebhook(WebhookModel[FlagPayload]):
    event: Literal["flag.updated"]


class InvitationAcceptedWebhook(WebhookModel[InvitationCommon]):
    event: Literal["invitation.accepted"]


class InvitationCreatedWebhook(WebhookModel[InvitationCommon]):
    event: Literal["invitation.created"]


class InvitationResentWebhook(WebhookModel[InvitationCommon]):
    event: Literal["invitation.resent"]


class InvitationRevokedWebhook(WebhookModel[InvitationCommon]):
    event: Literal["invitation.revoked"]


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


class OrganizationDomainCreatedWebhook(WebhookModel[OrganizationDomain]):
    event: Literal["organization_domain.created"]


class OrganizationDomainUpdatedWebhook(WebhookModel[OrganizationDomain]):
    event: Literal["organization_domain.updated"]


class OrganizationDomainDeletedWebhook(WebhookModel[OrganizationDomain]):
    event: Literal["organization_domain.deleted"]


class OrganizationMembershipCreatedWebhook(WebhookModel[OrganizationMembership]):
    event: Literal["organization_membership.created"]


class OrganizationMembershipDeletedWebhook(WebhookModel[OrganizationMembership]):
    event: Literal["organization_membership.deleted"]


class OrganizationMembershipUpdatedWebhook(WebhookModel[OrganizationMembership]):
    event: Literal["organization_membership.updated"]


class OrganizationRoleCreatedWebhook(WebhookModel[OrganizationRolePayload]):
    event: Literal["organization_role.created"]


class OrganizationRoleDeletedWebhook(WebhookModel[OrganizationRolePayload]):
    event: Literal["organization_role.deleted"]


class OrganizationRoleUpdatedWebhook(WebhookModel[OrganizationRolePayload]):
    event: Literal["organization_role.updated"]


class PasswordResetCreatedWebhook(WebhookModel[PasswordResetCommon]):
    event: Literal["password_reset.created"]


class PasswordResetSucceededWebhook(WebhookModel[PasswordResetCommon]):
    event: Literal["password_reset.succeeded"]


class PermissionCreatedWebhook(WebhookModel[PermissionPayload]):
    event: Literal["permission.created"]


class PermissionDeletedWebhook(WebhookModel[PermissionPayload]):
    event: Literal["permission.deleted"]


class PermissionUpdatedWebhook(WebhookModel[PermissionPayload]):
    event: Literal["permission.updated"]


class RoleCreatedWebhook(WebhookModel[EventRole]):
    event: Literal["role.created"]


class RoleDeletedWebhook(WebhookModel[EventRole]):
    event: Literal["role.deleted"]


class RoleUpdatedWebhook(WebhookModel[EventRole]):
    event: Literal["role.updated"]


class SessionCreatedWebhook(WebhookModel[SessionCreatedPayload]):
    event: Literal["session.created"]


class SessionRevokedWebhook(WebhookModel[SessionRevokedPayload]):
    event: Literal["session.revoked"]


class UserCreatedWebhook(WebhookModel[User]):
    event: Literal["user.created"]


class UserDeletedWebhook(WebhookModel[User]):
    event: Literal["user.deleted"]


class UserUpdatedWebhook(WebhookModel[User]):
    event: Literal["user.updated"]


Webhook = Annotated[
    Union[
        ApiKeyCreatedWebhook,
        ApiKeyRevokedWebhook,
        AuthenticationEmailVerificationFailedWebhook,
        AuthenticationEmailVerificationSucceededWebhook,
        AuthenticationMagicAuthFailedWebhook,
        AuthenticationMagicAuthSucceededWebhook,
        AuthenticationMfaFailedWebhook,
        AuthenticationMfaSucceededWebhook,
        AuthenticationOauthFailedWebhook,
        AuthenticationOauthSucceededWebhook,
        AuthenticationPasskeyFailedWebhook,
        AuthenticationPasskeySucceededWebhook,
        AuthenticationPasswordFailedWebhook,
        AuthenticationPasswordSucceededWebhook,
        AuthenticationRadarRiskDetectedWebhook,
        AuthenticationSsoFailedWebhook,
        AuthenticationSsoSucceededWebhook,
        ConnectionActivatedWebhook,
        ConnectionDeactivatedWebhook,
        ConnectionDeletedWebhook,
        ConnectionSamlCertificateRenewedWebhook,
        ConnectionSamlCertificateRenewalRequiredWebhook,
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
        FlagCreatedWebhook,
        FlagDeletedWebhook,
        FlagRuleUpdatedWebhook,
        FlagUpdatedWebhook,
        InvitationAcceptedWebhook,
        InvitationCreatedWebhook,
        InvitationResentWebhook,
        InvitationRevokedWebhook,
        MagicAuthCreatedWebhook,
        OrganizationCreatedWebhook,
        OrganizationDeletedWebhook,
        OrganizationUpdatedWebhook,
        OrganizationDomainCreatedWebhook,
        OrganizationDomainDeletedWebhook,
        OrganizationDomainUpdatedWebhook,
        OrganizationDomainVerificationFailedWebhook,
        OrganizationDomainVerifiedWebhook,
        OrganizationMembershipCreatedWebhook,
        OrganizationMembershipDeletedWebhook,
        OrganizationMembershipUpdatedWebhook,
        OrganizationRoleCreatedWebhook,
        OrganizationRoleDeletedWebhook,
        OrganizationRoleUpdatedWebhook,
        PasswordResetCreatedWebhook,
        PasswordResetSucceededWebhook,
        PermissionCreatedWebhook,
        PermissionDeletedWebhook,
        PermissionUpdatedWebhook,
        RoleCreatedWebhook,
        RoleDeletedWebhook,
        RoleUpdatedWebhook,
        SessionCreatedWebhook,
        SessionRevokedWebhook,
        UserCreatedWebhook,
        UserDeletedWebhook,
        UserUpdatedWebhook,
    ],
    Field(..., discriminator="event"),
]
