import datetime

from workos.types.authorization.organization_role import OrganizationRole


class MockOrganizationRole(OrganizationRole):
    def __init__(
        self,
        id: str,
        organization_id: str = "org_01EHT88Z8J8795GZNQ4ZP1J81T",
    ):
        now = datetime.datetime.now().isoformat()
        super().__init__(
            object="role",
            id=id,
            organization_id=organization_id,
            name="Admin",
            slug="admin",
            description="Organization admin role",
            resource_type_slug="organization",
            permissions=["documents:read", "documents:write"],
            type="OrganizationRole",
            created_at=now,
            updated_at=now,
        )
