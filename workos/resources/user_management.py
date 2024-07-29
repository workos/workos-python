from typing import Literal, Optional
from typing_extensions import TypedDict

from workos.resources.workos_model import WorkOSModel
from workos.types.user_management.invitation_common import InvitationCommon


PasswordHashType = Literal["bcrypt", "firebase-scrypt", "ssha"]

AuthenticationMethod = Literal[
    "SSO",
    "Password",
    "AppleOAuth",
    "GitHubOAuth",
    "GoogleOAuth",
    "MicrosoftOAuth",
    "MagicAuth",
    "Impersonation",
]


class User(WorkOSModel):
    """Representation of a WorkOS User."""

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
    """Representation of a WorkOS User and Organization ID response."""

    access_token: str
    authentication_method: Optional[AuthenticationMethod] = None
    impersonator: Optional[Impersonator] = None
    organization_id: Optional[str] = None
    refresh_token: str
    user: User


class RefreshTokenAuthenticationResponse(WorkOSModel):
    """Representation of a WorkOS refresh token authentication response."""

    access_token: str
    refresh_token: str


class EmailVerification(WorkOSModel):
    """Representation of a WorkOS EmailVerification object."""

    object: Literal["email_verification"]
    id: str
    user_id: str
    email: str
    expires_at: str
    code: str
    created_at: str
    updated_at: str


class Invitation(InvitationCommon):
    """Representation of a WorkOS Invitation as returned."""

    token: str
    accept_invitation_url: str


class MagicAuth(WorkOSModel):
    """Representation of a WorkOS MagicAuth object."""

    object: Literal["magic_auth"]
    id: str
    user_id: str
    email: str
    expires_at: str
    code: str
    created_at: str
    updated_at: str


class PasswordReset(WorkOSModel):
    """Representation of a WorkOS PasswordReset object."""

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
    """Representation of an WorkOS Organization Membership."""

    object: Literal["organization_membership"]
    id: str
    user_id: str
    organization_id: str
    role: OrganizationMembershipRole
    status: OrganizationMembershipStatus
    created_at: str
    updated_at: str
