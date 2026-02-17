from typing import Generic, Literal, TypeVar
from workos.types.user_management import OrganizationMembership, User
from workos.types.workos_model import WorkOSModel
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
    DirectoryPayloadWithLegacyFields,
    DirectoryPayloadWithLegacyFieldsForEventsApi,
)
from workos.types.events.directory_user_with_previous_attributes import (
    DirectoryUserWithPreviousAttributes,
)
from workos.types.events.flag_payload import FlagPayload
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
from workos.types.authorization.organization_role import (
    OrganizationRole,
    OrganizationRoleEvent,
)
from workos.types.authorization.permission import Permission
from workos.types.roles.role import EventRole
from workos.types.sso.connection import Connection
from workos.types.user_management.email_verification import (
    EmailVerificationCommon,
)
from workos.types.user_management.invitation import InvitationCommon
from workos.types.user_management.magic_auth import MagicAuthCommon
from workos.types.user_management.password_reset import PasswordResetCommon


EventPayload = TypeVar(
    "EventPayload",
    ApiKey,
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
    Connection,
    ConnectionPayloadWithLegacyFields,
    ConnectionSamlCertificateRenewedPayload,
    ConnectionSamlCertificateRenewalRequiredPayload,
    DirectoryPayload,
    DirectoryPayloadWithLegacyFields,
    # TODO: Remove once merged with DirectoryPayloadWithLegacyFields in next major release.
    DirectoryPayloadWithLegacyFieldsForEventsApi,
    DirectoryGroup,
    DirectoryGroupWithPreviousAttributes,
    DirectoryUser,
    DirectoryUserWithPreviousAttributes,
    DirectoryGroupMembershipPayload,
    EmailVerificationCommon,
    EventRole,
    FlagPayload,
    InvitationCommon,
    MagicAuthCommon,
    OrganizationCommon,
    OrganizationDomain,
    OrganizationDomainVerificationFailedPayload,
    OrganizationMembership,
    OrganizationRoleEvent,
    PasswordResetCommon,
    Permission,
    SessionCreatedPayload,
    SessionRevokedPayload,
    User,
)


class EventModel(WorkOSModel, Generic[EventPayload]):
    # TODO: fix these docs
    """Representation of an Event returned from the Events API or via Webhook.
    Attributes:
        OBJECT_FIELDS (list): List of fields an Event is comprised of.
    """

    id: str
    object: Literal["event"]
    data: EventPayload
    created_at: str
