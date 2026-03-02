from typing import Union

import pytest
from tests.types.test_auto_pagination_function import TestAutoPaginationFunction
from tests.utils.fixtures.mock_resource import MockAuthorizationResource
from tests.utils.fixtures.mock_resource_list import MockAuthorizationResourceList
from tests.utils.list_resource import list_response_of
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
        return MockAuthorizationResource().dict()

    @pytest.fixture
    def mock_resources_list_two(self):
        return MockAuthorizationResourceList().dict()

    @pytest.fixture
    def mock_resources_empty_list(self):
        return list_response_of(data=[])

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
            status_code=204,
        )

        response = syncify(self.authorization.delete_resource("res_01ABC"))

        assert request_kwargs["method"] == "delete"
        assert request_kwargs["url"].endswith("/authorization/resources/res_01ABC")
        assert request_kwargs.get("params") is None
        assert response is None

    def test_delete_resource_with_cascade_true(
        self, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client,
            status_code=204,
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
            status_code=204,
        )

        response = syncify(
            self.authorization.delete_resource("res_01ABC", cascade_delete=False)
        )

        assert request_kwargs["method"] == "delete"
        assert request_kwargs["url"].endswith("/authorization/resources/res_01ABC")
        assert request_kwargs["params"] == {"cascade_delete": "false"}
        assert response is None

    # --- list_resources ---
    def test_list_resources_returns_paginated_list(
        self,
        mock_resources_list_two,
        capture_and_mock_http_client_request,
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list_two, 200
        )

        response = syncify(self.authorization.list_resources())

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith("/authorization/resources")
        assert request_kwargs["params"] == {"limit": 10, "order": "desc"}

        assert response.object == "list"
        assert len(response.data) == 2

        assert response.data[0].object == "authorization_resource"
        assert response.data[0].id == "authz_resource_01HXYZ123ABC456DEF789ABC"
        assert response.data[0].external_id == "doc-12345678"
        assert response.data[0].name == "Q5 Budget Report"
        assert response.data[0].description == "Financial report for Q5 2025"
        assert response.data[0].resource_type_slug == "document"
        assert response.data[0].organization_id == "org_01HXYZ123ABC456DEF789ABC"
        assert (
            response.data[0].parent_resource_id
            == "authz_resource_01HXYZ123ABC456DEF789XYZ"
        )
        assert response.data[0].created_at == "2024-01-15T09:30:00.000Z"
        assert response.data[0].updated_at == "2024-01-15T09:30:00.000Z"

        assert response.data[1].object == "authorization_resource"
        assert response.data[1].id == "authz_resource_01HXYZ123ABC456DEF789DEF"
        assert response.data[1].external_id == "folder-123"
        assert response.data[1].name == "Finance Folder"
        assert response.data[1].description is None
        assert response.data[1].resource_type_slug == "folder"
        assert response.data[1].organization_id == "org_01HXYZ123ABC456DEF789ABC"
        assert response.data[1].parent_resource_id is None
        assert response.data[1].created_at == "2024-01-14T08:00:00.000Z"
        assert response.data[1].updated_at == "2024-01-14T08:00:00.000Z"

        assert response.list_metadata.before is None
        assert response.list_metadata.after == "authz_resource_01HXYZ123ABC456DEF789DEF"

    def test_list_resources_returns_empty_list(
        self,
        mock_resources_empty_list,
        capture_and_mock_http_client_request,
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_empty_list, 200
        )

        response = syncify(self.authorization.list_resources())

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith("/authorization/resources")
        assert request_kwargs["params"] == {"limit": 10, "order": "desc"}

        assert len(response.data) == 0
        assert response.list_metadata.before is None
        assert response.list_metadata.after is None

    def test_list_resources_request_with_no_parameters(
        self,
        mock_resources_list_two,
        capture_and_mock_http_client_request,
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list_two, 200
        )

        syncify(self.authorization.list_resources())

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith("/authorization/resources")
        assert request_kwargs["params"]["limit"] == 10
        assert request_kwargs["params"]["order"] == "desc"

        assert "organization_id" not in request_kwargs["params"]
        assert "resource_type_slug" not in request_kwargs["params"]
        assert "parent_resource_id" not in request_kwargs["params"]
        assert "parent_resource_type_slug" not in request_kwargs["params"]
        assert "parent_external_id" not in request_kwargs["params"]
        assert "search" not in request_kwargs["params"]
        assert "before" not in request_kwargs["params"]
        assert "after" not in request_kwargs["params"]

    def test_list_resources_with_organization_id(
        self, mock_resources_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list_two, 200
        )

        syncify(self.authorization.list_resources(organization_id="org_123"))

        assert request_kwargs["params"]["organization_id"] == "org_123"
        assert request_kwargs["params"]["limit"] == 10
        assert request_kwargs["params"]["order"] == "desc"

        assert "resource_type_slug" not in request_kwargs["params"]
        assert "parent_resource_id" not in request_kwargs["params"]
        assert "parent_resource_type_slug" not in request_kwargs["params"]
        assert "parent_external_id" not in request_kwargs["params"]
        assert "search" not in request_kwargs["params"]
        assert "before" not in request_kwargs["params"]
        assert "after" not in request_kwargs["params"]

    def test_list_resources_with_resource_type_slug(
        self, mock_resources_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list_two, 200
        )

        syncify(self.authorization.list_resources(resource_type_slug="document"))

        assert request_kwargs["params"]["resource_type_slug"] == "document"
        assert request_kwargs["params"]["limit"] == 10
        assert request_kwargs["params"]["order"] == "desc"

        assert "organization_id" not in request_kwargs["params"]
        assert "parent_resource_id" not in request_kwargs["params"]
        assert "parent_resource_type_slug" not in request_kwargs["params"]
        assert "parent_external_id" not in request_kwargs["params"]
        assert "search" not in request_kwargs["params"]
        assert "before" not in request_kwargs["params"]
        assert "after" not in request_kwargs["params"]

    def test_list_resources_with_parent_resource_id(
        self, mock_resources_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list_two, 200
        )

        syncify(self.authorization.list_resources(parent_resource_id="res_parent_123"))

        assert request_kwargs["params"]["parent_resource_id"] == "res_parent_123"
        assert request_kwargs["params"]["limit"] == 10
        assert request_kwargs["params"]["order"] == "desc"

        assert "organization_id" not in request_kwargs["params"]
        assert "resource_type_slug" not in request_kwargs["params"]
        assert "parent_resource_type_slug" not in request_kwargs["params"]
        assert "parent_external_id" not in request_kwargs["params"]
        assert "search" not in request_kwargs["params"]
        assert "before" not in request_kwargs["params"]
        assert "after" not in request_kwargs["params"]

    def test_list_resources_with_parent_resource_type_slug(
        self, mock_resources_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list_two, 200
        )

        syncify(self.authorization.list_resources(parent_resource_type_slug="folder"))

        assert request_kwargs["params"]["parent_resource_type_slug"] == "folder"
        assert request_kwargs["params"]["limit"] == 10
        assert request_kwargs["params"]["order"] == "desc"

        assert "organization_id" not in request_kwargs["params"]
        assert "resource_type_slug" not in request_kwargs["params"]
        assert "parent_resource_id" not in request_kwargs["params"]
        assert "parent_external_id" not in request_kwargs["params"]
        assert "search" not in request_kwargs["params"]
        assert "before" not in request_kwargs["params"]
        assert "after" not in request_kwargs["params"]

    def test_list_resources_with_parent_external_id(
        self, mock_resources_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list_two, 200
        )

        syncify(self.authorization.list_resources(parent_external_id="parent_ext_456"))

        assert request_kwargs["params"]["parent_external_id"] == "parent_ext_456"
        assert request_kwargs["params"]["limit"] == 10
        assert request_kwargs["params"]["order"] == "desc"
        assert "organization_id" not in request_kwargs["params"]
        assert "resource_type_slug" not in request_kwargs["params"]
        assert "parent_resource_id" not in request_kwargs["params"]
        assert "parent_resource_type_slug" not in request_kwargs["params"]
        assert "search" not in request_kwargs["params"]
        assert "before" not in request_kwargs["params"]
        assert "after" not in request_kwargs["params"]

    def test_list_resources_with_search(
        self, mock_resources_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list_two, 200
        )

        syncify(self.authorization.list_resources(search="Budget"))

        assert request_kwargs["params"]["search"] == "Budget"
        assert request_kwargs["params"]["limit"] == 10
        assert request_kwargs["params"]["order"] == "desc"

        assert "organization_id" not in request_kwargs["params"]
        assert "resource_type_slug" not in request_kwargs["params"]
        assert "parent_resource_id" not in request_kwargs["params"]
        assert "parent_resource_type_slug" not in request_kwargs["params"]
        assert "parent_external_id" not in request_kwargs["params"]
        assert "before" not in request_kwargs["params"]
        assert "after" not in request_kwargs["params"]

    def test_list_resources_with_limit(
        self, mock_resources_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list_two, 200
        )

        syncify(self.authorization.list_resources(limit=25))

        assert request_kwargs["params"]["limit"] == 25
        assert request_kwargs["params"]["order"] == "desc"

        assert "organization_id" not in request_kwargs["params"]
        assert "resource_type_slug" not in request_kwargs["params"]
        assert "parent_resource_id" not in request_kwargs["params"]
        assert "parent_resource_type_slug" not in request_kwargs["params"]
        assert "parent_external_id" not in request_kwargs["params"]
        assert "search" not in request_kwargs["params"]
        assert "before" not in request_kwargs["params"]
        assert "after" not in request_kwargs["params"]

    def test_list_resources_with_before(
        self, mock_resources_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list_two, 200
        )

        syncify(self.authorization.list_resources(before="cursor_before"))

        assert request_kwargs["params"]["before"] == "cursor_before"
        assert request_kwargs["params"]["limit"] == 10
        assert request_kwargs["params"]["order"] == "desc"

        assert "organization_id" not in request_kwargs["params"]
        assert "resource_type_slug" not in request_kwargs["params"]
        assert "parent_resource_id" not in request_kwargs["params"]
        assert "parent_resource_type_slug" not in request_kwargs["params"]
        assert "parent_external_id" not in request_kwargs["params"]
        assert "search" not in request_kwargs["params"]
        assert "after" not in request_kwargs["params"]

    def test_list_resources_with_after(
        self, mock_resources_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list_two, 200
        )

        syncify(self.authorization.list_resources(after="cursor_after"))

        assert request_kwargs["params"]["after"] == "cursor_after"
        assert request_kwargs["params"]["limit"] == 10
        assert request_kwargs["params"]["order"] == "desc"

        assert "organization_id" not in request_kwargs["params"]
        assert "resource_type_slug" not in request_kwargs["params"]
        assert "parent_resource_id" not in request_kwargs["params"]
        assert "parent_resource_type_slug" not in request_kwargs["params"]
        assert "parent_external_id" not in request_kwargs["params"]
        assert "search" not in request_kwargs["params"]
        assert "before" not in request_kwargs["params"]

    def test_list_resources_with_order_asc(
        self, mock_resources_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list_two, 200
        )

        syncify(self.authorization.list_resources(order="asc"))

        assert request_kwargs["params"]["order"] == "asc"
        assert request_kwargs["params"]["limit"] == 10

        assert "organization_id" not in request_kwargs["params"]
        assert "resource_type_slug" not in request_kwargs["params"]
        assert "parent_resource_id" not in request_kwargs["params"]
        assert "parent_resource_type_slug" not in request_kwargs["params"]
        assert "parent_external_id" not in request_kwargs["params"]
        assert "search" not in request_kwargs["params"]
        assert "before" not in request_kwargs["params"]
        assert "after" not in request_kwargs["params"]

    def test_list_resources_with_order_desc(
        self, mock_resources_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list_two, 200
        )

        syncify(self.authorization.list_resources(order="desc"))

        assert request_kwargs["params"]["order"] == "desc"
        assert request_kwargs["params"]["limit"] == 10

        assert "organization_id" not in request_kwargs["params"]
        assert "resource_type_slug" not in request_kwargs["params"]
        assert "parent_resource_id" not in request_kwargs["params"]
        assert "parent_resource_type_slug" not in request_kwargs["params"]
        assert "parent_external_id" not in request_kwargs["params"]
        assert "search" not in request_kwargs["params"]
        assert "before" not in request_kwargs["params"]
        assert "after" not in request_kwargs["params"]

    def test_list_resources_with_all_parameters(
        self, mock_resources_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list_two, 200
        )

        syncify(
            self.authorization.list_resources(
                organization_id="org_123",
                resource_type_slug="document",
                parent_resource_id="res_parent_123",
                parent_resource_type_slug="folder",
                parent_external_id="parent_ext_456",
                search="Budget",
                limit=5,
                before="cursor_before",
                after="cursor_after",
                order="asc",
            )
        )

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith("/authorization/resources")
        assert request_kwargs["params"]["organization_id"] == "org_123"
        assert request_kwargs["params"]["resource_type_slug"] == "document"
        assert request_kwargs["params"]["parent_resource_id"] == "res_parent_123"
        assert request_kwargs["params"]["parent_resource_type_slug"] == "folder"
        assert request_kwargs["params"]["parent_external_id"] == "parent_ext_456"
        assert request_kwargs["params"]["search"] == "Budget"
        assert request_kwargs["params"]["limit"] == 5
        assert request_kwargs["params"]["before"] == "cursor_before"
        assert request_kwargs["params"]["after"] == "cursor_after"
        assert request_kwargs["params"]["order"] == "asc"
