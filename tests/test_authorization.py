from typing import Union

import pytest
from tests.utils.fixtures.mock_environment_role import MockEnvironmentRole
from tests.utils.fixtures.mock_organization_role import MockOrganizationRole
from tests.utils.fixtures.mock_permission import MockPermission
from tests.utils.list_resource import list_response_of
from tests.utils.syncify import syncify
from workos.authorization import AsyncAuthorization, Authorization


@pytest.mark.sync_and_async(Authorization, AsyncAuthorization)
class TestAuthorization:
    @pytest.fixture(autouse=True)
    def setup(self, module_instance: Union[Authorization, AsyncAuthorization]):
        self.http_client = module_instance._http_client
        self.authorization = module_instance

    @pytest.fixture
    def mock_permission(self):
        return MockPermission(id="perm_01ABC").dict()

    @pytest.fixture
    def mock_permissions(self):
        permission_list = [
            MockPermission(id=f"perm_{i}", slug=f"perm-{i}").dict() for i in range(5)
        ]
        return {
            "data": permission_list,
            "list_metadata": {"before": None, "after": None},
            "object": "list",
        }

    @pytest.fixture
    def mock_permissions_multiple_data_pages(self):
        permission_list = [
            MockPermission(id=f"perm_{i}", slug=f"perm-{i}").dict() for i in range(40)
        ]
        return list_response_of(data=permission_list)

    def test_create_permission(
        self, mock_permission, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_permission, 201
        )

        permission = syncify(
            self.authorization.create_permission(
                slug="documents:read", name="Read Documents"
            )
        )

        assert permission.id == "perm_01ABC"
        assert permission.slug == "documents:read"
        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith("/authorization/permissions")
        assert request_kwargs["json"] == {
            "slug": "documents:read",
            "name": "Read Documents",
        }

    def test_create_permission_with_description(
        self, mock_permission, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_permission, 201
        )

        syncify(
            self.authorization.create_permission(
                slug="documents:read",
                name="Read Documents",
                description="Allows reading documents",
            )
        )

        assert request_kwargs["json"] == {
            "slug": "documents:read",
            "name": "Read Documents",
            "description": "Allows reading documents",
        }

    def test_list_permissions(
        self, mock_permissions, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_permissions, 200
        )

        permissions_response = syncify(self.authorization.list_permissions())

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith("/authorization/permissions")
        assert len(permissions_response.data) == 5

    def test_list_permissions_auto_pagination(
        self,
        mock_permissions_multiple_data_pages,
        test_auto_pagination,
    ):
        test_auto_pagination(
            http_client=self.http_client,
            list_function=self.authorization.list_permissions,
            expected_all_page_data=mock_permissions_multiple_data_pages["data"],
        )

    def test_get_permission(
        self, mock_permission, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_permission, 200
        )

        permission = syncify(self.authorization.get_permission("documents:read"))

        assert permission.id == "perm_01ABC"
        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith(
            "/authorization/permissions/documents:read"
        )

    def test_update_permission(
        self, mock_permission, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_permission, 200
        )

        permission = syncify(
            self.authorization.update_permission("documents:read", name="Updated Name")
        )

        assert permission.id == "perm_01ABC"
        assert request_kwargs["method"] == "patch"
        assert request_kwargs["url"].endswith(
            "/authorization/permissions/documents:read"
        )
        assert request_kwargs["json"] == {"name": "Updated Name"}

    def test_update_permission_with_description(
        self, mock_permission, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_permission, 200
        )

        syncify(
            self.authorization.update_permission(
                "documents:read",
                name="Updated Name",
                description="Updated description",
            )
        )

        assert request_kwargs["json"] == {
            "name": "Updated Name",
            "description": "Updated description",
        }

    def test_delete_permission(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client,
            202,
            headers={"content-type": "text/plain; charset=utf-8"},
        )

        response = syncify(self.authorization.delete_permission("documents:read"))

        assert response is None
        assert request_kwargs["method"] == "delete"
        assert request_kwargs["url"].endswith(
            "/authorization/permissions/documents:read"
        )

    # --- Organization Role fixtures ---

    @pytest.fixture
    def mock_organization_role(self):
        return MockOrganizationRole(id="role_01ABC").dict()

    @pytest.fixture
    def mock_organization_roles(self):
        return {
            "data": [MockOrganizationRole(id=f"role_{i}").dict() for i in range(5)],
            "object": "list",
        }

    # --- Organization Role tests ---

    def test_create_organization_role(
        self, mock_organization_role, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_organization_role, 201
        )

        role = syncify(
            self.authorization.create_organization_role(
                "org_01EHT88Z8J8795GZNQ4ZP1J81T",
                slug="admin",
                name="Admin",
            )
        )

        assert role.id == "role_01ABC"
        assert role.type == "OrganizationRole"
        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith(
            "/authorization/organizations/org_01EHT88Z8J8795GZNQ4ZP1J81T/roles"
        )
        assert request_kwargs["json"] == {"slug": "admin", "name": "Admin"}

    def test_list_organization_roles(
        self, mock_organization_roles, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_organization_roles, 200
        )

        roles_response = syncify(
            self.authorization.list_organization_roles("org_01EHT88Z8J8795GZNQ4ZP1J81T")
        )

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith(
            "/authorization/organizations/org_01EHT88Z8J8795GZNQ4ZP1J81T/roles"
        )
        assert len(roles_response.data) == 5

    def test_get_organization_role(
        self, mock_organization_role, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_organization_role, 200
        )

        role = syncify(
            self.authorization.get_organization_role(
                "org_01EHT88Z8J8795GZNQ4ZP1J81T", "admin"
            )
        )

        assert role.id == "role_01ABC"
        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith(
            "/authorization/organizations/org_01EHT88Z8J8795GZNQ4ZP1J81T/roles/admin"
        )

    def test_update_organization_role(
        self, mock_organization_role, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_organization_role, 200
        )

        role = syncify(
            self.authorization.update_organization_role(
                "org_01EHT88Z8J8795GZNQ4ZP1J81T",
                "admin",
                name="Super Admin",
            )
        )

        assert role.id == "role_01ABC"
        assert request_kwargs["method"] == "patch"
        assert request_kwargs["url"].endswith(
            "/authorization/organizations/org_01EHT88Z8J8795GZNQ4ZP1J81T/roles/admin"
        )
        assert request_kwargs["json"] == {"name": "Super Admin"}

    def test_set_organization_role_permissions(
        self, mock_organization_role, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_organization_role, 200
        )

        role = syncify(
            self.authorization.set_organization_role_permissions(
                "org_01EHT88Z8J8795GZNQ4ZP1J81T",
                "admin",
                permissions=["documents:read", "documents:write"],
            )
        )

        assert role.id == "role_01ABC"
        assert request_kwargs["method"] == "put"
        assert request_kwargs["url"].endswith(
            "/authorization/organizations/org_01EHT88Z8J8795GZNQ4ZP1J81T/roles/admin/permissions"
        )
        assert request_kwargs["json"] == {
            "permissions": ["documents:read", "documents:write"]
        }

    def test_add_organization_role_permission(
        self, mock_organization_role, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_organization_role, 200
        )

        role = syncify(
            self.authorization.add_organization_role_permission(
                "org_01EHT88Z8J8795GZNQ4ZP1J81T",
                "admin",
                permission_slug="documents:read",
            )
        )

        assert role.id == "role_01ABC"
        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith(
            "/authorization/organizations/org_01EHT88Z8J8795GZNQ4ZP1J81T/roles/admin/permissions"
        )
        assert request_kwargs["json"] == {"slug": "documents:read"}

    def test_remove_organization_role_permission(
        self, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client,
            202,
            headers={"content-type": "text/plain; charset=utf-8"},
        )

        response = syncify(
            self.authorization.remove_organization_role_permission(
                "org_01EHT88Z8J8795GZNQ4ZP1J81T",
                "admin",
                permission_slug="documents:read",
            )
        )

        assert response is None
        assert request_kwargs["method"] == "delete"
        assert request_kwargs["url"].endswith(
            "/authorization/organizations/org_01EHT88Z8J8795GZNQ4ZP1J81T/roles/admin/permissions/documents:read"
        )

    # --- Environment Role fixtures ---

    @pytest.fixture
    def mock_environment_role(self):
        return MockEnvironmentRole(id="role_01DEF").dict()

    @pytest.fixture
    def mock_environment_roles(self):
        return {
            "data": [MockEnvironmentRole(id=f"role_{i}").dict() for i in range(5)],
            "object": "list",
        }

    # --- Environment Role tests ---

    def test_create_environment_role(
        self, mock_environment_role, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_environment_role, 201
        )

        role = syncify(
            self.authorization.create_environment_role(slug="member", name="Member")
        )

        assert role.id == "role_01DEF"
        assert role.type == "EnvironmentRole"
        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith("/authorization/roles")
        assert request_kwargs["json"] == {"slug": "member", "name": "Member"}

    def test_list_environment_roles(
        self, mock_environment_roles, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_environment_roles, 200
        )

        roles_response = syncify(self.authorization.list_environment_roles())

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith("/authorization/roles")
        assert len(roles_response.data) == 5

    def test_get_environment_role(
        self, mock_environment_role, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_environment_role, 200
        )

        role = syncify(self.authorization.get_environment_role("member"))

        assert role.id == "role_01DEF"
        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith("/authorization/roles/member")

    def test_update_environment_role(
        self, mock_environment_role, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_environment_role, 200
        )

        role = syncify(
            self.authorization.update_environment_role("member", name="Updated Member")
        )

        assert role.id == "role_01DEF"
        assert request_kwargs["method"] == "patch"
        assert request_kwargs["url"].endswith("/authorization/roles/member")
        assert request_kwargs["json"] == {"name": "Updated Member"}

    def test_set_environment_role_permissions(
        self, mock_environment_role, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_environment_role, 200
        )

        role = syncify(
            self.authorization.set_environment_role_permissions(
                "member", permissions=["documents:read"]
            )
        )

        assert role.id == "role_01DEF"
        assert request_kwargs["method"] == "put"
        assert request_kwargs["url"].endswith("/authorization/roles/member/permissions")
        assert request_kwargs["json"] == {"permissions": ["documents:read"]}

    def test_add_environment_role_permission(
        self, mock_environment_role, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_environment_role, 200
        )

        role = syncify(
            self.authorization.add_environment_role_permission(
                "member", permission_slug="documents:read"
            )
        )

        assert role.id == "role_01DEF"
        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith("/authorization/roles/member/permissions")
        assert request_kwargs["json"] == {"slug": "documents:read"}
