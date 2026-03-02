from typing import Union

import pytest
from tests.utils.fixtures.mock_resource import MockResource
from tests.utils.syncify import syncify
from workos.authorization import AsyncAuthorization, Authorization


@pytest.mark.sync_and_async(Authorization, AsyncAuthorization)
class TestAuthorizationResourceCRUD:
    @pytest.fixture(autouse=True)
    def setup(self, module_instance: Union[Authorization, AsyncAuthorization]):
        self.http_client = module_instance._http_client
        self.authorization = module_instance

    @pytest.fixture
    def mock_resource(self):
        return MockResource(id="res_01ABC").dict()

    # --- get_resource ---

    def test_get_resource(self, mock_resource, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 200
        )

        resource = syncify(self.authorization.get_resource("res_01ABC"))

        assert resource.id == "res_01ABC"
        assert resource.object == "authorization_resource"
        assert resource.external_id == "ext_123"
        assert resource.name == "Test Resource"
        assert resource.resource_type_slug == "document"
        assert resource.organization_id == "org_01EHT88Z8J8795GZNQ4ZP1J81T"
        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith("/authorization/resources/res_01ABC")

    # --- create_resource ---
    def test_create_resource_without_parent(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 201
        )

        resource = syncify(
            self.authorization.create_resource(
                organization_id="org_01EHT88Z8J8795GZNQ4ZP1J81T",
                resource_type_slug="document",
                external_id="ext_123",
                name="Q4 Budget Report",
                description="Financial report for Q4 2025",
            )
        )

        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith("/authorization/resources")
        assert request_kwargs["json"] == {
            "organization_id": "org_01EHT88Z8J8795GZNQ4ZP1J81T",
            "resource_type_slug": "document",
            "external_id": "ext_123",
            "name": "Q4 Budget Report",
            "description": "Financial report for Q4 2025",
        }
        assert "parent_resource_id" not in request_kwargs["json"]
        assert "parent_resource_external_id" not in request_kwargs["json"]
        assert "parent_resource_type_slug" not in request_kwargs["json"]

        assert resource.object == "authorization_resource"
        assert resource.id == "res_01ABC"

    def test_create_resource_with_parent_resource_id(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 201
        )

        resource = syncify(
            self.authorization.create_resource(
                organization_id="org_01EHT88Z8J8795GZNQ4ZP1J81T",
                resource_type_slug="document",
                external_id="ext_123",
                name="Q4 Budget Report",
                description="Financial report for Q4 2025",
                parent={"parent_resource_id": "res_01PARENT"},
            )
        )

        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith("/authorization/resources")
        assert request_kwargs["json"] == {
            "organization_id": "org_01EHT88Z8J8795GZNQ4ZP1J81T",
            "resource_type_slug": "document",
            "external_id": "ext_123",
            "name": "Q4 Budget Report",
            "description": "Financial report for Q4 2025",
            "parent_resource_id": "res_01PARENT",
        }
        assert "parent_resource_external_id" not in request_kwargs["json"]
        assert "parent_resource_type_slug" not in request_kwargs["json"]

        assert resource.object == "authorization_resource"
        assert resource.id == "res_01ABC"

    def test_create_resource_with_parent_resource_id_and_no_description(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 201
        )

        resource = syncify(
            self.authorization.create_resource(
                organization_id="org_01EHT88Z8J8795GZNQ4ZP1J81T",
                resource_type_slug="document",
                external_id="ext_123",
                name="Q4 Budget Report",
                parent={"parent_resource_id": "res_01PARENT"},
            )
        )

        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith("/authorization/resources")
        assert request_kwargs["json"] == {
            "organization_id": "org_01EHT88Z8J8795GZNQ4ZP1J81T",
            "resource_type_slug": "document",
            "external_id": "ext_123",
            "name": "Q4 Budget Report",
            "parent_resource_id": "res_01PARENT",
        }
        assert resource.object == "authorization_resource"
        assert resource.id == "res_01ABC"

    def test_create_resource_with_parent_resource_id_and_none_description(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 201
        )

        resource = syncify(
            self.authorization.create_resource(
                organization_id="org_01EHT88Z8J8795GZNQ4ZP1J81T",
                resource_type_slug="document",
                external_id="ext_123",
                name="Q4 Budget Report",
                description=None,
                parent={"parent_resource_id": "res_01PARENT"},
            )
        )

        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith("/authorization/resources")
        assert request_kwargs["json"] == {
            "organization_id": "org_01EHT88Z8J8795GZNQ4ZP1J81T",
            "resource_type_slug": "document",
            "external_id": "ext_123",
            "name": "Q4 Budget Report",
            "parent_resource_id": "res_01PARENT",
        }
        assert "parent_resource_external_id" not in request_kwargs["json"]
        assert "parent_resource_type_slug" not in request_kwargs["json"]
        assert "description" not in request_kwargs["json"]
        assert resource.object == "authorization_resource"
        assert resource.id == "res_01ABC"

    def test_create_resource_with_parent_external_id(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 201
        )

        resource = syncify(
            self.authorization.create_resource(
                organization_id="org_01EHT88Z8J8795GZNQ4ZP1J81T",
                resource_type_slug="document",
                external_id="ext_123",
                name="Q4 Budget Report",
                description="Financial report for Q4 2025",
                parent={
                    "parent_resource_external_id": "ext_parent_456",
                    "parent_resource_type_slug": "folder",
                },
            )
        )

        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith("/authorization/resources")
        assert request_kwargs["json"] == {
            "organization_id": "org_01EHT88Z8J8795GZNQ4ZP1J81T",
            "resource_type_slug": "document",
            "external_id": "ext_123",
            "name": "Q4 Budget Report",
            "description": "Financial report for Q4 2025",
            "parent_resource_external_id": "ext_parent_456",
            "parent_resource_type_slug": "folder",
        }
        assert "parent_resource_id" not in request_kwargs["json"]

        assert resource.object == "authorization_resource"
        assert resource.id == "res_01ABC"

    def test_create_resource_with_parent_external_id_and_no_description(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 201
        )

        resource = syncify(
            self.authorization.create_resource(
                organization_id="org_01EHT88Z8J8795GZNQ4ZP1J81T",
                resource_type_slug="document",
                external_id="ext_123",
                name="Q4 Budget Report",
                parent={
                    "parent_resource_external_id": "ext_parent_456",
                    "parent_resource_type_slug": "folder",
                },
            )
        )

        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith("/authorization/resources")
        assert request_kwargs["json"] == {
            "organization_id": "org_01EHT88Z8J8795GZNQ4ZP1J81T",
            "resource_type_slug": "document",
            "external_id": "ext_123",
            "name": "Q4 Budget Report",
            "parent_resource_external_id": "ext_parent_456",
            "parent_resource_type_slug": "folder",
        }
        assert "parent_resource_id" not in request_kwargs["json"]

        assert resource.object == "authorization_resource"
        assert resource.id == "res_01ABC"

    def test_create_resource_with_parent_external_id_and_none_description(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 201
        )

        resource = syncify(
            self.authorization.create_resource(
                organization_id="org_01EHT88Z8J8795GZNQ4ZP1J81T",
                resource_type_slug="document",
                external_id="ext_123",
                name="Q4 Budget Report",
                description=None,
                parent={
                    "parent_resource_external_id": "ext_parent_456",
                    "parent_resource_type_slug": "folder",
                },
            )
        )

        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith("/authorization/resources")
        assert request_kwargs["json"] == {
            "organization_id": "org_01EHT88Z8J8795GZNQ4ZP1J81T",
            "resource_type_slug": "document",
            "external_id": "ext_123",
            "name": "Q4 Budget Report",
            "parent_resource_external_id": "ext_parent_456",
            "parent_resource_type_slug": "folder",
        }
        assert "parent_resource_id" not in request_kwargs["json"]
        assert "description" not in request_kwargs["json"]

        assert resource.object == "authorization_resource"
        assert resource.id == "res_01ABC"

    # --- update_resource ---

    def test_update_resource_with_name_and_description(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 200
        )

        resource = syncify(
            self.authorization.update_resource(
                "res_01ABC",
                name="Updated Name",
                description="Updated description",
            )
        )

        assert resource.id == "res_01ABC"
        assert request_kwargs["method"] == "patch"
        assert request_kwargs["url"].endswith("/authorization/resources/res_01ABC")
        assert request_kwargs["json"] == {
            "name": "Updated Name",
            "description": "Updated description",
        }

    def test_update_resource_clear_description(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 200
        )

        syncify(self.authorization.update_resource("res_01ABC", description=None))

        assert request_kwargs["method"] == "patch"
        assert request_kwargs["json"] == {"description": None}

    def test_update_resource_without_meta(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 200
        )

        syncify(self.authorization.update_resource("res_01ABC"))

        assert request_kwargs["method"] == "patch"
        assert request_kwargs["json"] == {}

    def test_update_resource_without_desc(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 200
        )

        resource = syncify(
            self.authorization.update_resource(
                "res_01ABC",
                name="Updated Name",
            )
        )

        assert resource.id == "res_01ABC"
        assert request_kwargs["method"] == "patch"
        assert request_kwargs["url"].endswith("/authorization/resources/res_01ABC")
        assert request_kwargs["json"] == {"name": "Updated Name"}

    # --- delete_resource ---

    def test_delete_resource_without_cascade(
        self, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client,
            status_code=202,
            headers={"content-type": "text/plain; charset=utf-8"},
        )

        response = syncify(self.authorization.delete_resource("res_01ABC"))

        assert response is None
        assert request_kwargs["method"] == "delete"
        assert request_kwargs["url"].endswith("/authorization/resources/res_01ABC")
        assert request_kwargs.get("params") is None

    def test_delete_resource_with_cascade(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client,
            status_code=202,
            headers={"content-type": "text/plain; charset=utf-8"},
        )

        response = syncify(
            self.authorization.delete_resource("res_01ABC", cascade_delete=True)
        )

        assert response is None
        assert request_kwargs["method"] == "delete"
        assert request_kwargs["url"].endswith("/authorization/resources/res_01ABC")
        assert request_kwargs["params"] == {"cascade_delete": "true"}

    def test_delete_resource_with_cascade_false(
        self, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client,
            status_code=202,
            headers={"content-type": "text/plain; charset=utf-8"},
        )

        response = syncify(
            self.authorization.delete_resource("res_01ABC", cascade_delete=False)
        )

        assert response is None
        assert request_kwargs["method"] == "delete"
        assert request_kwargs["url"].endswith("/authorization/resources/res_01ABC")
        assert request_kwargs["params"] == {"cascade_delete": "false"}
