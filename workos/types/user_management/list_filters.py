from typing import Optional
from workos.resources.list import ListArgs


class UsersListFilters(ListArgs, total=False):
    email: Optional[str]
    organization_id: Optional[str]


class InvitationsListFilters(ListArgs, total=False):
    email: Optional[str]
    organization_id: Optional[str]


class OrganizationMembershipsListFilters(ListArgs, total=False):
    user_id: Optional[str]
    organization_id: Optional[str]
    # A set of statuses that's concatenated into a comma-separated string
    statuses: Optional[str]


class AuthenticationFactorsListFilters(ListArgs, total=False):
    user_id: str
