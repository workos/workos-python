from typing import Optional

from workos.types.authorization.authorization_resource import AuthorizationResource


class MockAuthorizationResource(AuthorizationResource):
    def __init__(
        self,
        id: str = "authz_resource_01HXYZ123ABC456DEF789ABC",
        external_id: str = "doc-456",
        name: str = "Q4 Budget Report",
        description: Optional[str] = "Financial report for Q4 2025",
        resource_type_slug: str = "folder",
        organization_id: str = "org_01HXYZ123ABC456DEF789ABC",
        parent_resource_id: Optional[str] = None,
    ):
        super().__init__(
            object="authorization_resource",
            id=id,
            external_id=external_id,
            name=name,
            description=description,
            resource_type_slug=resource_type_slug,
            organization_id=organization_id,
            parent_resource_id=parent_resource_id,
            created_at="2024-01-15T09:30:00.000Z",
            updated_at="2024-01-15T09:30:00.000Z",
        )
