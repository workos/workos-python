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
        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith("/authorization/resources/res_01ABC")

    # --- create_resource ---

    def test_create_resource_required_fields_only(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 201
        )

        resource = syncify(
            self.authorization.create_resource(
                resource_type="document",
                organization_id="org_01EHT88Z8J8795GZNQ4ZP1J81T",
            )
        )

        assert resource.id == "res_01ABC"
        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith("/authorization/resources")
        assert request_kwargs["json"] == {
            "resource_type": "document",
            "organization_id": "org_01EHT88Z8J8795GZNQ4ZP1J81T",
        }

    def test_create_resource_with_all_optional_fields(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 201
        )

        syncify(
            self.authorization.create_resource(
                resource_type="document",
                organization_id="org_01EHT88Z8J8795GZNQ4ZP1J81T",
                external_id="ext_123",
                meta={"key": "value"},
                parent={"resource_id": "res_01PARENT"},
            )
        )

        assert request_kwargs["json"] == {
            "resource_type": "document",
            "organization_id": "org_01EHT88Z8J8795GZNQ4ZP1J81T",
            "external_id": "ext_123",
            "meta": {"key": "value"},
            "parent": {"resource_id": "res_01PARENT"},
        }

    def test_create_resource_with_parent_by_id(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 201
        )

        syncify(
            self.authorization.create_resource(
                resource_type="document",
                organization_id="org_01EHT88Z8J8795GZNQ4ZP1J81T",
                parent={"resource_id": "res_01PARENT"},
            )
        )

        assert request_kwargs["json"]["parent"] == {"resource_id": "res_01PARENT"}

    def test_create_resource_with_parent_by_external_id(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 201
        )

        syncify(
            self.authorization.create_resource(
                resource_type="document",
                organization_id="org_01EHT88Z8J8795GZNQ4ZP1J81T",
                parent={
                    "organization_id": "org_01EHT88Z8J8795GZNQ4ZP1J81T",
                    "resource_type": "folder",
                    "external_id": "ext_parent_456",
                },
            )
        )

        assert request_kwargs["json"]["parent"] == {
            "organization_id": "org_01EHT88Z8J8795GZNQ4ZP1J81T",
            "resource_type": "folder",
            "external_id": "ext_parent_456",
        }

    # --- update_resource ---

    def test_update_resource_with_meta(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 200
        )

        resource = syncify(
            self.authorization.update_resource(
                "res_01ABC",
                meta={"updated_key": "updated_value"},
            )
        )

        assert resource.id == "res_01ABC"
        assert request_kwargs["method"] == "patch"
        assert request_kwargs["url"].endswith("/authorization/resources/res_01ABC")
        assert request_kwargs["json"] == {"meta": {"updated_key": "updated_value"}}

    def test_update_resource_without_meta(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 200
        )

        syncify(self.authorization.update_resource("res_01ABC"))

        assert request_kwargs["method"] == "patch"
        assert request_kwargs["json"] == {}

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
        assert request_kwargs["json"] == {"cascade_delete": True}
