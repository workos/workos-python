from typing import Optional, Sequence
from workos.types.list_resource import ListArgs
from workos.types.user_management.organization_membership import (
    OrganizationMembershipStatus,
)


class UsersListFilters(ListArgs, total=False):
    email: Optional[str]
    organization_id: Optional[str]


class InvitationsListFilters(ListArgs, total=False):
    email: Optional[str]
    organization_id: Optional[str]


class OrganizationMembershipsListFilters(ListArgs, total=False):
    user_id: Optional[str]
    organization_id: Optional[str]
    statuses: Optional[Sequence[OrganizationMembershipStatus]]


class AuthenticationFactorsListFilters(ListArgs, total=False):
    user_id: str
