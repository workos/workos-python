"""Tests for new authorization types: Resource, RoleAssignment, AccessEvaluation,
AuthorizationOrganizationMembership."""

from workos.types.authorization import (
    AccessEvaluation,
    AuthorizationOrganizationMembership,
    Resource,
    RoleAssignment,
    RoleAssignmentResource,
    RoleAssignmentRole,
)


class TestAccessEvaluation:
    def test_authorized_true(self):
        result = AccessEvaluation(authorized=True)
        assert result.authorized is True

    def test_authorized_false(self):
        result = AccessEvaluation(authorized=False)
        assert result.authorized is False

    def test_from_dict(self):
        result = AccessEvaluation.model_validate({"authorized": True})
        assert result.authorized is True


class TestResource:
    def test_resource_deserialization(self):
        data = {
            "object": "authorization_resource",
            "id": "res_01ABC",
            "external_id": "ext_123",
            "name": "Test Document",
            "resource_type_slug": "document",
            "organization_id": "org_01EHT88Z8J8795GZNQ4ZP1J81T",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        resource = Resource.model_validate(data)

        assert resource.object == "authorization_resource"
        assert resource.id == "res_01ABC"
        assert resource.external_id == "ext_123"
        assert resource.name == "Test Document"
        assert resource.resource_type_slug == "document"
        assert resource.organization_id == "org_01EHT88Z8J8795GZNQ4ZP1J81T"
        assert resource.description is None
        assert resource.parent_resource_id is None

    def test_resource_with_optional_fields(self):
        data = {
            "object": "authorization_resource",
            "id": "res_01ABC",
            "external_id": "ext_123",
            "name": "Test Document",
            "description": "A test document resource",
            "resource_type_slug": "document",
            "organization_id": "org_01EHT88Z8J8795GZNQ4ZP1J81T",
            "parent_resource_id": "res_01PARENT",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        resource = Resource.model_validate(data)

        assert resource.description == "A test document resource"
        assert resource.parent_resource_id == "res_01PARENT"


class TestRoleAssignment:
    def test_role_assignment_deserialization(self):
        data = {
            "object": "role_assignment",
            "id": "ra_01ABC",
            "role": {"slug": "admin"},
            "resource": {
                "id": "res_01ABC",
                "external_id": "ext_123",
                "resource_type_slug": "document",
            },
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        assignment = RoleAssignment.model_validate(data)

        assert assignment.object == "role_assignment"
        assert assignment.id == "ra_01ABC"
        assert assignment.role.slug == "admin"
        assert assignment.resource.id == "res_01ABC"
        assert assignment.resource.external_id == "ext_123"
        assert assignment.resource.resource_type_slug == "document"

    def test_role_assignment_role(self):
        role = RoleAssignmentRole(slug="editor")
        assert role.slug == "editor"

    def test_role_assignment_resource(self):
        resource = RoleAssignmentResource(
            id="res_01ABC",
            external_id="ext_123",
            resource_type_slug="document",
        )
        assert resource.id == "res_01ABC"
        assert resource.external_id == "ext_123"
        assert resource.resource_type_slug == "document"


class TestAuthorizationOrganizationMembership:
    def test_membership_deserialization(self):
        data = {
            "object": "organization_membership",
            "id": "om_01ABC",
            "user_id": "user_01ABC",
            "organization_id": "org_01ABC",
            "status": "active",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        membership = AuthorizationOrganizationMembership.model_validate(data)

        assert membership.object == "organization_membership"
        assert membership.id == "om_01ABC"
        assert membership.user_id == "user_01ABC"
        assert membership.organization_id == "org_01ABC"
        assert membership.status == "active"
        assert membership.custom_attributes is None

    def test_membership_with_custom_attributes(self):
        data = {
            "object": "organization_membership",
            "id": "om_01ABC",
            "user_id": "user_01ABC",
            "organization_id": "org_01ABC",
            "organization_name": "Test Org",
            "status": "active",
            "custom_attributes": {"department": "Engineering"},
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }
        membership = AuthorizationOrganizationMembership.model_validate(data)

        assert membership.custom_attributes == {"department": "Engineering"}
