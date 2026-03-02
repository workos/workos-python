"""Tests for new authorization types: AuthorizationResource, RoleAssignment, AccessEvaluation,
AuthorizationOrganizationMembership."""

from workos.types.authorization import (
    AccessCheckResponse,
    AuthorizationOrganizationMembership,
    AuthorizationResource,
    RoleAssignment,
    RoleAssignmentResource,
    RoleAssignmentRole,
)


class TestAccessEvaluation:
    def test_authorized_true(self):
        response = AccessCheckResponse(authorized=True)
        assert response.authorized is True

    def test_authorized_false(self):
        response = AccessCheckResponse(authorized=False)
        assert response.authorized is False

    def test_from_dict(self):
        response = AccessCheckResponse.model_validate({"authorized": True})
        assert response.authorized is True


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
        response = AuthorizationResource.model_validate(data)

        assert response.object == "authorization_resource"
        assert response.id == "res_01ABC"
        assert response.external_id == "ext_123"
        assert response.name == "Test Document"
        assert response.resource_type_slug == "document"
        assert response.organization_id == "org_01EHT88Z8J8795GZNQ4ZP1J81T"
        assert response.description is None
        assert response.parent_resource_id is None

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
        response = AuthorizationResource.model_validate(data)

        assert response.description == "A test document resource"
        assert response.parent_resource_id == "res_01PARENT"


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
        response = RoleAssignment.model_validate(data)

        assert response.object == "role_assignment"
        assert response.id == "ra_01ABC"
        assert response.role.slug == "admin"
        assert response.resource.id == "res_01ABC"
        assert response.resource.external_id == "ext_123"
        assert response.resource.resource_type_slug == "document"

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
        response = AuthorizationOrganizationMembership.model_validate(data)

        assert response.object == "organization_membership"
        assert response.id == "om_01ABC"
        assert response.user_id == "user_01ABC"
        assert response.organization_id == "org_01ABC"
        assert response.status == "active"
