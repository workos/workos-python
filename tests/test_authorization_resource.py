from typing import Union

import pytest
from tests.utils.fixtures.mock_resource import MockAuthorizationResource
from tests.utils.syncify import syncify
from workos.authorization import AsyncAuthorization, Authorization
from workos.exceptions import BadRequestException


@pytest.mark.sync_and_async(Authorization, AsyncAuthorization)
class TestAuthorizationResourceCRUD:
    @pytest.fixture(autouse=True)
    def setup(self, module_instance: Union[Authorization, AsyncAuthorization]):
        self.http_client = module_instance._http_client
        self.authorization = module_instance

    @pytest.fixture
    def mock_resource(self):
        return MockAuthorizationResource(id="res_01ABC").dict()

    # --- get_resource ---

    def test_get_resource(self, mock_resource, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 200
        )

        response = syncify(self.authorization.get_resource("res_01ABC"))

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith("/authorization/resources/res_01ABC")

        assert response.object == "authorization_resource"
        assert response.id == "res_01ABC"
        assert response.external_id == "ext_123"
        assert response.name == "Test Resource"
        assert response.description == "A test resource for unit tests"
        assert response.resource_type_slug == "document"
        assert response.organization_id == "org_01EHT88Z8J8795GZNQ4ZP1J81T"
        assert response.parent_resource_id == "res_01XYZ"
        assert response.created_at == "2024-01-15T12:00:00.000Z"
        assert response.updated_at == "2024-01-15T12:00:00.000Z"

    def test_get_resource_without_parent(self, capture_and_mock_http_client_request):
        mock_resource = MockAuthorizationResource(parent_resource_id=None).dict()
        capture_and_mock_http_client_request(self.http_client, mock_resource, 200)

        response = syncify(self.authorization.get_resource("res_01ABC"))

        assert response.parent_resource_id is None

    def test_get_resource_without_description(
        self, capture_and_mock_http_client_request
    ):
        mock_resource = MockAuthorizationResource(description=None).dict()
        capture_and_mock_http_client_request(self.http_client, mock_resource, 200)

        response = syncify(self.authorization.get_resource("res_01ABC"))

        assert response.description is None

    def test_get_resource_without_parent_and_description(
        self, capture_and_mock_http_client_request
    ):
        mock_resource = MockAuthorizationResource(
            parent_resource_id=None, description=None
        ).dict()
        capture_and_mock_http_client_request(self.http_client, mock_resource, 200)

        response = syncify(self.authorization.get_resource("res_01ABC"))

        assert response.parent_resource_id is None
        assert response.description is None

    # --- create_resource ---

    def test_create_resource_with_parent_by_id(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 200
        )

        response = syncify(
            self.authorization.create_resource(
                external_id="ext_123",
                name="Test Resource",
                description="A test resource",
                resource_type_slug="document",
                organization_id="org_01EHT88Z8J8795GZNQ4ZP1J81T",
                parent={"parent_resource_id": "res_01XYZ"},
            )
        )

        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith("/authorization/resources")
        assert request_kwargs["json"] == {
            "resource_type_slug": "document",
            "organization_id": "org_01EHT88Z8J8795GZNQ4ZP1J81T",
            "external_id": "ext_123",
            "name": "Test Resource",
            "description": "A test resource",
            "parent_resource_id": "res_01XYZ",
        }
        assert "parent_resource_external_id" not in request_kwargs["json"]
        assert "parent_resource_type_slug" not in request_kwargs["json"]

        assert response.object == "authorization_resource"
        assert response.id == "res_01ABC"
        assert response.external_id == "ext_123"
        assert response.name == "Test Resource"
        assert response.description == "A test resource for unit tests"
        assert response.resource_type_slug == "document"
        assert response.organization_id == "org_01EHT88Z8J8795GZNQ4ZP1J81T"
        assert response.parent_resource_id == "res_01XYZ"
        assert response.created_at == "2024-01-15T12:00:00.000Z"
        assert response.updated_at == "2024-01-15T12:00:00.000Z"

    def test_create_resource_with_parent_by_id_no_description(
        self, capture_and_mock_http_client_request
    ):
        mock_resource = MockAuthorizationResource(description=None).dict()
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 200
        )

        response = syncify(
            self.authorization.create_resource(
                external_id="ext_123",
                name="Test Resource",
                description=None,
                resource_type_slug="document",
                organization_id="org_01EHT88Z8J8795GZNQ4ZP1J81T",
                parent={"parent_resource_id": "res_01XYZ"},
            )
        )

        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith("/authorization/resources")
        assert request_kwargs["json"] == {
            "resource_type_slug": "document",
            "organization_id": "org_01EHT88Z8J8795GZNQ4ZP1J81T",
            "external_id": "ext_123",
            "name": "Test Resource",
            "parent_resource_id": "res_01XYZ",
        }
        assert "description" not in request_kwargs["json"]
        assert "parent_resource_external_id" not in request_kwargs["json"]
        assert "parent_resource_type_slug" not in request_kwargs["json"]

        assert response.description is None

    def test_create_resource_with_parent_by_external_id(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 200
        )

        response = syncify(
            self.authorization.create_resource(
                external_id="ext_123",
                name="Test Resource",
                description="A test resource",
                resource_type_slug="document",
                organization_id="org_01EHT88Z8J8795GZNQ4ZP1J81T",
                parent={
                    "parent_resource_external_id": "parent_ext_456",
                    "parent_resource_type_slug": "folder",
                },
            )
        )

        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith("/authorization/resources")
        assert request_kwargs["json"] == {
            "resource_type_slug": "document",
            "organization_id": "org_01EHT88Z8J8795GZNQ4ZP1J81T",
            "external_id": "ext_123",
            "name": "Test Resource",
            "description": "A test resource",
            "parent_resource_external_id": "parent_ext_456",
            "parent_resource_type_slug": "folder",
        }

        assert "parent_resource_id" not in request_kwargs["json"]

        assert response.object == "authorization_resource"
        assert response.id == "res_01ABC"
        assert response.external_id == "ext_123"
        assert response.name == "Test Resource"
        assert response.description == "A test resource for unit tests"
        assert response.resource_type_slug == "document"
        assert response.organization_id == "org_01EHT88Z8J8795GZNQ4ZP1J81T"
        assert response.parent_resource_id == "res_01XYZ"
        assert response.created_at == "2024-01-15T12:00:00.000Z"
        assert response.updated_at == "2024-01-15T12:00:00.000Z"

    def test_create_resource_with_parent_by_external_id_no_description(
        self, capture_and_mock_http_client_request
    ):
        mock_resource = MockAuthorizationResource(description=None).dict()
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 200
        )

        response = syncify(
            self.authorization.create_resource(
                external_id="ext_123",
                name="Test Resource",
                description=None,
                resource_type_slug="document",
                organization_id="org_01EHT88Z8J8795GZNQ4ZP1J81T",
                parent={
                    "parent_resource_external_id": "parent_ext_456",
                    "parent_resource_type_slug": "folder",
                },
            )
        )

        assert request_kwargs["method"] == "post"
        assert request_kwargs["json"] == {
            "resource_type_slug": "document",
            "organization_id": "org_01EHT88Z8J8795GZNQ4ZP1J81T",
            "external_id": "ext_123",
            "name": "Test Resource",
            "parent_resource_external_id": "parent_ext_456",
            "parent_resource_type_slug": "folder",
        }

        assert "description" not in request_kwargs["json"]
        assert "parent_resource_id" not in request_kwargs["json"]

        assert response.description is None

    # --- update_resource ---
    def test_update_resource_name_only(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        updated_resource = MockAuthorizationResource(
            name="New Name",
        ).dict()
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, updated_resource, 200
        )

        response = syncify(
            self.authorization.update_resource("res_01ABC", name="New Name")
        )

        assert request_kwargs["method"] == "patch"
        assert request_kwargs["url"].endswith("/authorization/resources/res_01ABC")
        assert request_kwargs["json"] == {"name": "New Name"}

        assert response.id == "res_01ABC"
        assert response.name == "New Name"
        assert response.description == "A test resource for unit tests"

    def test_update_resource_description_only(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        updated_resource = MockAuthorizationResource(
            description="Updated description only",
        ).dict()
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, updated_resource, 200
        )

        response = syncify(
            self.authorization.update_resource(
                "res_01ABC", description="Updated description only"
            )
        )

        assert request_kwargs["method"] == "patch"
        assert request_kwargs["url"].endswith("/authorization/resources/res_01ABC")
        assert request_kwargs["json"] == {
            "description": "Updated description only",
        }
        assert response.id == "res_01ABC"
        assert response.name == "Test Resource"
        assert response.description == "Updated description only"

    def test_update_resource_remove_description(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        updated_resource = MockAuthorizationResource(description=None).dict()
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, updated_resource, 200
        )

        response = syncify(
            self.authorization.update_resource("res_01ABC", description=None)
        )

        assert request_kwargs["method"] == "patch"
        assert request_kwargs["url"].endswith("/authorization/resources/res_01ABC")
        assert request_kwargs["json"] == {"description": None}
        assert response.id == "res_01ABC"
        assert response.description is None

    def test_update_resource_with_name_and_description(
        self, capture_and_mock_http_client_request
    ):
        updated_resource = MockAuthorizationResource(
            name="Updated Name",
            description="Updated description",
        ).dict()
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, updated_resource, 200
        )

        response = syncify(
            self.authorization.update_resource(
                "res_01ABC",
                name="Updated Name",
                description="Updated description",
            )
        )

        assert request_kwargs["method"] == "patch"
        assert request_kwargs["url"].endswith("/authorization/resources/res_01ABC")
        assert request_kwargs["json"] == {
            "name": "Updated Name",
            "description": "Updated description",
        }
        assert response.id == "res_01ABC"
        assert response.name == "Updated Name"
        assert response.description == "Updated description"

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

        assert request_kwargs["method"] == "delete"
        assert request_kwargs["url"].endswith("/authorization/resources/res_01ABC")
        assert request_kwargs.get("params") is None
        assert response is None

    def test_delete_resource_with_cascade(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client,
            status_code=202,
            headers={"content-type": "text/plain; charset=utf-8"},
        )

        response = syncify(
            self.authorization.delete_resource("res_01ABC", cascade_delete=True)
        )

        assert request_kwargs["method"] == "delete"
        assert request_kwargs["url"].endswith("/authorization/resources/res_01ABC")
        assert request_kwargs["params"] == {"cascade_delete": "true"}
        assert response is None

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

        assert request_kwargs["method"] == "delete"
        assert request_kwargs["url"].endswith("/authorization/resources/res_01ABC")
        assert request_kwargs["params"] == {"cascade_delete": "false"}
        assert response is None
