import datetime

from workos.types.user_management import OrganizationMembership


class MockOrganizationMembership(OrganizationMembership):
    def __init__(self, id):
        now = datetime.datetime.now().isoformat()
        super().__init__(
            object="organization_membership",
            id=id,
            user_id="user_12345",
            organization_id="org_67890",
            status="active",
            role={"slug": "member"},
            created_at=now,
            updated_at=now,
        )
