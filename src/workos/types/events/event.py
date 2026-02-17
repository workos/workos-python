from typing import Literal, Union
from pydantic import Field
from typing_extensions import Annotated
from workos.types.user_management import OrganizationMembership, User
from workos.types.directory_sync.directory_group import DirectoryGroup
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
    DirectoryPayloadWithLegacyFieldsForEventsApi,
)
from workos.types.events.directory_user_with_previous_attributes import (
    DirectoryUserWithPreviousAttributes,
)
from workos.types.authorization.organization_role import OrganizationRoleEvent
from workos.types.authorization.permission import Permission
from workos.types.events.event_model import EventModel
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
from workos.types.organizations.organization_common import OrganizationCommon
from workos.types.organization_domains import OrganizationDomain
from workos.types.roles.role import EventRole
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


class ApiKeyCreatedEvent(EventModel[ApiKey]):
    event: Literal["api_key.created"]


class ApiKeyRevokedEvent(EventModel[ApiKey]):
    event: Literal["api_key.revoked"]


class AuthenticationEmailVerificationFailedEvent(
    EventModel[AuthenticationEmailVerificationFailedPayload,]
):
    event: Literal["authentication.email_verification_failed"]


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


class AuthenticationMfaFailedEvent(EventModel[AuthenticationMfaFailedPayload]):
    event: Literal["authentication.mfa_failed"]


class AuthenticationMfaSucceededEvent(EventModel[AuthenticationMfaSucceededPayload]):
    event: Literal["authentication.mfa_succeeded"]


class AuthenticationOauthFailedEvent(EventModel[AuthenticationOauthFailedPayload]):
    event: Literal["authentication.oauth_failed"]


class AuthenticationOauthSucceededEvent(
    EventModel[AuthenticationOauthSucceededPayload]
):
    event: Literal["authentication.oauth_succeeded"]


class AuthenticationPasskeyFailedEvent(EventModel[AuthenticationPasskeyFailedPayload]):
    event: Literal["authentication.passkey_failed"]


class AuthenticationPasskeySucceededEvent(
    EventModel[AuthenticationPasskeySucceededPayload]
):
    event: Literal["authentication.passkey_succeeded"]


class AuthenticationPasswordFailedEvent(
    EventModel[AuthenticationPasswordFailedPayload]
):
    event: Literal["authentication.password_failed"]


class AuthenticationPasswordSucceededEvent(
    EventModel[AuthenticationPasswordSucceededPayload,]
):
    event: Literal["authentication.password_succeeded"]


class AuthenticationRadarRiskDetectedEvent(
    EventModel[AuthenticationRadarRiskDetectedPayload]
):
    event: Literal["authentication.radar_risk_detected"]


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


class ConnectionSamlCertificateRenewedEvent(
    EventModel[ConnectionSamlCertificateRenewedPayload]
):
    event: Literal["connection.saml_certificate_renewed"]


class ConnectionSamlCertificateRenewalRequiredEvent(
    EventModel[ConnectionSamlCertificateRenewalRequiredPayload]
):
    event: Literal["connection.saml_certificate_renewal_required"]


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


class FlagCreatedEvent(EventModel[FlagPayload]):
    event: Literal["flag.created"]


class FlagDeletedEvent(EventModel[FlagPayload]):
    event: Literal["flag.deleted"]


class FlagRuleUpdatedEvent(EventModel[FlagPayload]):
    event: Literal["flag.rule_updated"]
    context: FlagRuleUpdatedContext


class FlagUpdatedEvent(EventModel[FlagPayload]):
    event: Literal["flag.updated"]


class InvitationAcceptedEvent(EventModel[InvitationCommon]):
    event: Literal["invitation.accepted"]


class InvitationCreatedEvent(EventModel[InvitationCommon]):
    event: Literal["invitation.created"]


class InvitationResentEvent(EventModel[InvitationCommon]):
    event: Literal["invitation.resent"]


class InvitationRevokedEvent(EventModel[InvitationCommon]):
    event: Literal["invitation.revoked"]


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


class OrganizationDomainCreatedEvent(EventModel[OrganizationDomain]):
    event: Literal["organization_domain.created"]


class OrganizationDomainUpdatedEvent(EventModel[OrganizationDomain]):
    event: Literal["organization_domain.updated"]


class OrganizationDomainDeletedEvent(EventModel[OrganizationDomain]):
    event: Literal["organization_domain.deleted"]


class OrganizationMembershipCreatedEvent(EventModel[OrganizationMembership]):
    event: Literal["organization_membership.created"]


class OrganizationMembershipDeletedEvent(EventModel[OrganizationMembership]):
    event: Literal["organization_membership.deleted"]


class OrganizationMembershipUpdatedEvent(EventModel[OrganizationMembership]):
    event: Literal["organization_membership.updated"]


class OrganizationRoleCreatedEvent(EventModel[OrganizationRoleEvent]):
    event: Literal["organization_role.created"]


class OrganizationRoleUpdatedEvent(EventModel[OrganizationRoleEvent]):
    event: Literal["organization_role.updated"]


class OrganizationRoleDeletedEvent(EventModel[OrganizationRoleEvent]):
    event: Literal["organization_role.deleted"]


class PasswordResetCreatedEvent(EventModel[PasswordResetCommon]):
    event: Literal["password_reset.created"]


class PasswordResetSucceededEvent(EventModel[PasswordResetCommon]):
    event: Literal["password_reset.succeeded"]


class PermissionCreatedEvent(EventModel[Permission]):
    event: Literal["permission.created"]


class PermissionUpdatedEvent(EventModel[Permission]):
    event: Literal["permission.updated"]


class PermissionDeletedEvent(EventModel[Permission]):
    event: Literal["permission.deleted"]


class RoleCreatedEvent(EventModel[EventRole]):
    event: Literal["role.created"]


class RoleDeletedEvent(EventModel[EventRole]):
    event: Literal["role.deleted"]


class RoleUpdatedEvent(EventModel[EventRole]):
    event: Literal["role.updated"]


class SessionCreatedEvent(EventModel[SessionCreatedPayload]):
    event: Literal["session.created"]


class SessionRevokedEvent(EventModel[SessionRevokedPayload]):
    event: Literal["session.revoked"]


class UserCreatedEvent(EventModel[User]):
    event: Literal["user.created"]


class UserDeletedEvent(EventModel[User]):
    event: Literal["user.deleted"]


class UserUpdatedEvent(EventModel[User]):
    event: Literal["user.updated"]


Event = Annotated[
    Union[
        ApiKeyCreatedEvent,
        ApiKeyRevokedEvent,
        AuthenticationEmailVerificationFailedEvent,
        AuthenticationEmailVerificationSucceededEvent,
        AuthenticationMagicAuthFailedEvent,
        AuthenticationMagicAuthSucceededEvent,
        AuthenticationMfaFailedEvent,
        AuthenticationMfaSucceededEvent,
        AuthenticationOauthFailedEvent,
        AuthenticationOauthSucceededEvent,
        AuthenticationPasskeyFailedEvent,
        AuthenticationPasskeySucceededEvent,
        AuthenticationPasswordFailedEvent,
        AuthenticationPasswordSucceededEvent,
        AuthenticationRadarRiskDetectedEvent,
        AuthenticationSsoFailedEvent,
        AuthenticationSsoSucceededEvent,
        ConnectionActivatedEvent,
        ConnectionDeactivatedEvent,
        ConnectionDeletedEvent,
        ConnectionSamlCertificateRenewedEvent,
        ConnectionSamlCertificateRenewalRequiredEvent,
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
        FlagCreatedEvent,
        FlagDeletedEvent,
        FlagRuleUpdatedEvent,
        FlagUpdatedEvent,
        InvitationAcceptedEvent,
        InvitationCreatedEvent,
        InvitationResentEvent,
        InvitationRevokedEvent,
        MagicAuthCreatedEvent,
        OrganizationCreatedEvent,
        OrganizationDeletedEvent,
        OrganizationUpdatedEvent,
        OrganizationDomainCreatedEvent,
        OrganizationDomainDeletedEvent,
        OrganizationDomainUpdatedEvent,
        OrganizationDomainVerificationFailedEvent,
        OrganizationDomainVerifiedEvent,
        OrganizationMembershipCreatedEvent,
        OrganizationMembershipDeletedEvent,
        OrganizationMembershipUpdatedEvent,
        OrganizationRoleCreatedEvent,
        OrganizationRoleUpdatedEvent,
        OrganizationRoleDeletedEvent,
        PasswordResetCreatedEvent,
        PasswordResetSucceededEvent,
        PermissionCreatedEvent,
        PermissionUpdatedEvent,
        PermissionDeletedEvent,
        RoleCreatedEvent,
        RoleDeletedEvent,
        RoleUpdatedEvent,
        SessionCreatedEvent,
        SessionRevokedEvent,
        UserCreatedEvent,
        UserDeletedEvent,
        UserUpdatedEvent,
    ],
    Field(..., discriminator="event"),
]
