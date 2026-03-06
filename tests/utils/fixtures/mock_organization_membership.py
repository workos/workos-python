import datetime
from typing import Optional, Sequence

from workos.types.authorization.organization_membership import (
    AuthorizationOrganizationMembership,
)
from workos.types.list_resource import ListMetadata, ListPage
from workos.types.user_management import OrganizationMembership


class MockAuthorizationOrganizationMembershipList(
    ListPage[AuthorizationOrganizationMembership]
):
    def __init__(
        self,
        data: Optional[Sequence[AuthorizationOrganizationMembership]] = None,
        before: Optional[str] = None,
        after: Optional[str] = "om_01DEF",
    ):
        if data is None:
            data = [
                AuthorizationOrganizationMembership(
                    object="organization_membership",
                    id="om_01ABC",
                    user_id="user_123",
                    organization_id="org_456",
                    status="active",
                    directory_managed=False,
                    created_at="2024-01-01T00:00:00Z",
                    updated_at="2024-01-01T00:00:00Z",
                ),
                AuthorizationOrganizationMembership(
                    object="organization_membership",
                    id="om_01DEF",
                    user_id="user_789",
                    organization_id="org_456",
                    status="active",
                    directory_managed=False,
                    created_at="2024-01-02T00:00:00Z",
                    updated_at="2024-01-02T00:00:00Z",
                ),
            ]
        super().__init__(
            object="list",
            data=data,
            list_metadata=ListMetadata(before=before, after=after),
        )


class MockOrganizationMembership(OrganizationMembership):
    def __init__(self, id):
        now = datetime.datetime.now().isoformat()
        super().__init__(
            object="organization_membership",
            id=id,
            user_id="user_12345",
            organization_id="org_67890",
            status="active",
            directory_managed=False,
            role={"slug": "member"},
            custom_attributes={},
            created_at=now,
            updated_at=now,
        )
