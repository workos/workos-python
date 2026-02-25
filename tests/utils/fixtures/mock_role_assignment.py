class MockRoleAssignment:
    def __init__(
        self,
        id: str = "role_assignment_01HXYZ123ABC456DEF789ABC",
        role_slug: str = "editor",
        resource_id: str = "resource_01HXYZ123ABC456DEF789XYZ",
        resource_external_id: str = "doc-123",
        resource_type_slug: str = "document",
    ):
        self.id = id
        self.role_slug = role_slug
        self.resource_id = resource_id
        self.resource_external_id = resource_external_id
        self.resource_type_slug = resource_type_slug

    def dict(self) -> dict:
        return {
            "object": "role_assignment",
            "id": self.id,
            "role": {"slug": self.role_slug},
            "resource": {
                "id": self.resource_id,
                "external_id": self.resource_external_id,
                "resource_type_slug": self.resource_type_slug,
            },
            "created_at": "2024-01-15T09:30:00.000Z",
            "updated_at": "2024-01-15T09:30:00.000Z",
        }
