from typing import Awaitable, Optional, Protocol, Sequence, Type, Union, cast
from urllib.parse import urlencode
from workos._client_configuration import ClientConfiguration
from workos.session import AsyncSession, Session
from workos.types.list_resource import (
    ListArgs,
    ListMetadata,
    ListPage,
    WorkOSListResource,
)
from workos.types.metadata import Metadata
from workos.types.mfa import (
    AuthenticationFactor,
    AuthenticationFactorTotpAndChallengeResponse,
    AuthenticationFactorType,
)
from workos.types.user_management import (
    AuthenticationResponse,
    EmailVerification,
    Invitation,
    MagicAuth,
    OrganizationMembership,
    OrganizationMembershipStatus,
    PasswordReset,
    RefreshTokenAuthenticationResponse,
    User,
)
from workos.types.user_management.authenticate_with_common import (
    AuthenticateWithCodeParameters,
    AuthenticateWithEmailVerificationParameters,
    AuthenticateWithMagicAuthParameters,
    AuthenticateWithOrganizationSelectionParameters,
    AuthenticateWithParameters,
    AuthenticateWithPasswordParameters,
    AuthenticateWithRefreshTokenParameters,
    AuthenticateWithTotpParameters,
)
from workos.types.user_management.authentication_response import (
    AuthKitAuthenticationResponse,
    AuthenticationResponseType,
)
from workos.types.user_management.list_filters import (
    AuthenticationFactorsListFilters,
    InvitationsListFilters,
    OrganizationMembershipsListFilters,
    UsersListFilters,
)
from workos.types.user_management.password_hash_type import PasswordHashType
from workos.types.user_management.screen_hint import ScreenHintType
from workos.types.user_management.session import SessionConfig

class UpdateUserOptions:
    def __init__(self, email, email_verified, first_name, last_name):
        self.email = email
        self.email_verified = email_verified
        self.first_name = first_name
        self.last_name = last_name

    def serialize(self):
        return {
            "email": self.email,
            "email_verified": self.email_verified,
            "first_name": self.first_name,
            "last_name": self.last_name,
        }