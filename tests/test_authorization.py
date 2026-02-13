from typing import Union

import pytest
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
