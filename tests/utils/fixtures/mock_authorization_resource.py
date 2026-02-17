"""Mock fixture for AuthorizationResource used in testing new FGA APIs.

This fixture represents the new organization-scoped authorization resource model
used in the Advanced FGA APIs, distinct from the legacy warrant-based resources.
"""

from typing import Optional


class MockAuthorizationResource:
    """Mock authorization resource for testing the new FGA resource-based APIs.

    Attributes:
        id: Internal WorkOS resource ID.
        external_id: Customer-provided external identifier for the resource.
        name: Human-readable name for the resource.
        description: Optional description of the resource.
        resource_type_slug: The type of resource (e.g., "document", "folder").
        organization_id: The organization this resource belongs to.
        parent_resource_id: Optional parent resource ID for hierarchical resources.
    """

    def __init__(
        self,
        id: str = "authz_resource_01HXYZ123ABC456DEF789ABC",
        external_id: str = "doc-456",
        name: str = "Q4 Budget Report",
        description: Optional[str] = "Financial report for Q4 2025",
        resource_type_slug: str = "document",
        organization_id: str = "org_01HXYZ123ABC456DEF789ABC",
        parent_resource_id: Optional[str] = None,
    ):
        self.id = id
        self.external_id = external_id
        self.name = name
        self.description = description
        self.resource_type_slug = resource_type_slug
        self.organization_id = organization_id
        self.parent_resource_id = parent_resource_id

    def dict(self) -> dict:
        """Return the resource as a dictionary matching API response format."""
        return {
            "object": "authorization_resource",
            "id": self.id,
            "external_id": self.external_id,
            "name": self.name,
            "description": self.description,
            "resource_type_slug": self.resource_type_slug,
            "organization_id": self.organization_id,
            "parent_resource_id": self.parent_resource_id,
            "created_at": "2024-01-15T09:30:00.000Z",
            "updated_at": "2024-01-15T09:30:00.000Z",
        }
