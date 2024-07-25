from typing import Literal, Optional
from typing_extensions import TypedDict

from workos.resources.workos_model import WorkOSModel


PasswordHashType = Literal["bcrypt", "firebase-scrypt", "ssha"]


class User(WorkOSModel):
    """Representation of a User as returned by WorkOS through User Management features."""

    object: Literal["user"]
    id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email_verified: bool
    profile_picture_url: Optional[str] = None
    created_at: str
    updated_at: str


class Impersonator(WorkOSModel):
    """Representation of a WorkOS Dashboard member impersonating a user"""

    email: str
    reason: str


class AuthenticationResponse(WorkOSModel):
    """Representation of a User and Organization ID response as returned by WorkOS through User Management features."""

    access_token: str
    impersonator: Optional[Impersonator] = None
    organization_id: Optional[str] = None
    refresh_token: str
    user: User


class RefreshTokenAuthenticationResponse(WorkOSModel):
    """Representation of refresh token authentication response as returned by WorkOS through User Management features."""

    access_token: str
    refresh_token: str


class EmailVerification(WorkOSModel):
    """Representation of a EmailVerification object as returned by WorkOS through User Management features."""

    object: Literal["email_verification"]
    id: str
    user_id: str
    email: str
    expires_at: str
    code: str
    created_at: str
    updated_at: str


class Invitation(WorkOSModel):
    """Representation of an Invitation as returned by WorkOS through User Management features."""

    object: Literal["invitation"]
    id: str
    email: str
    state: str
    accepted_at: Optional[str] = None
    revoked_at: Optional[str] = None
    expires_at: str
    token: str
    accept_invitation_url: str
    organization_id: Optional[str] = None
    inviter_user_id: Optional[str] = None
    created_at: str
    updated_at: str


class MagicAuth(WorkOSModel):
    """Representation of a MagicAuth object as returned by WorkOS through User Management features."""

    object: Literal["magic_auth"]
    id: str
    user_id: str
    email: str
    expires_at: str
    code: str
    created_at: str
    updated_at: str


class PasswordReset(WorkOSModel):
    """Representation of a PasswordReset object as returned by WorkOS through User Management features."""

    object: Literal["password_reset"]
    id: str
    user_id: str
    email: str
    password_reset_token: str
    password_reset_url: str
    expires_at: str
    created_at: str


class OrganizationMembershipRole(TypedDict):
    slug: str


OrganizationMembershipStatus = Literal["active", "inactive", "pending"]


class OrganizationMembership(WorkOSModel):
    """Representation of an Organization Membership as returned by WorkOS through User Management features."""

    object: Literal["organization_membership"]
    id: str
    user_id: str
    organization_id: str
    role: OrganizationMembershipRole
    status: OrganizationMembershipStatus
    created_at: str
    updated_at: str
