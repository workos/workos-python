from typing import Generic, Literal, TypeVar
from workos.types.user_management import OrganizationMembership, User
from workos.types.workos_model import WorkOSModel
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


EventPayload = TypeVar(
    "EventPayload",
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
    Connection,
    ConnectionPayloadWithLegacyFields,
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
    InvitationCommon,
    MagicAuthCommon,
    OrganizationCommon,
    OrganizationDomain,
    OrganizationDomainVerificationFailedPayload,
    OrganizationMembership,
    PasswordResetCommon,
    Role,
    SessionCreatedPayload,
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
