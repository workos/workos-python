from typing import Literal, TypeVar


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
    "magic_auth.created",
    "organization.created",
    "organization.deleted",
    "organization.updated",
    "organization_domain.verification_failed",
    "organization_domain.verified",
    "organization_membership.created",
    "organization_membership.deleted",
    "organization_membership.updated",
    "password_reset.created",
    "role.created",
    "role.deleted",
    "role.updated",
    "session.created",
    "user.created",
    "user.deleted",
    "user.updated",
]

EventTypeDiscriminator = TypeVar("EventTypeDiscriminator", bound=EventType)
