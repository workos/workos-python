from workos.types.authorization.authorization_resource import AuthorizationResource


class MockResource(AuthorizationResource):
    def __init__(
        self,
        id: str = "res_01ABC",
        external_id: str = "ext_123",
        name: str = "Test Resource",
        description: str = "A test resource for unit tests",
        resource_type_slug: str = "document",
        organization_id: str = "org_01EHT88Z8J8795GZNQ4ZP1J81T",
        parent_resource_id: str = "res_01XYZ",
        created_at: str = "2024-01-15T12:00:00.000Z",
        updated_at: str = "2024-01-15T12:00:00.000Z",
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
            created_at=created_at,
            updated_at=updated_at,
        )
