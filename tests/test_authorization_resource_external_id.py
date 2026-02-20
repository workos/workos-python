from typing import Union

import pytest
from tests.utils.list_resource import list_response_of
from tests.utils.syncify import syncify
from workos.authorization import AsyncAuthorization, Authorization


@pytest.mark.sync_and_async(Authorization, AsyncAuthorization)
class TestAuthorizationResourceByExternalId:
    @pytest.fixture(autouse=True)
    def setup(self, module_instance: Union[Authorization, AsyncAuthorization]):
        self.http_client = module_instance._http_client
        self.authorization = module_instance

    @pytest.fixture
    def mock_authorization_resource(self):
        return {
            "resource_type": "document",
            "resource_id": "doc_123",
            "meta": {"title": "Test Document"},
            "created_at": "2024-01-01T00:00:00Z",
        }

    # --- get_resource_by_external_id ---

    def test_get_resource_by_external_id(
        self, mock_authorization_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_authorization_resource, 200
        )

        resource = syncify(
            self.authorization.get_resource_by_external_id(
                "org_01EHT88Z8J8795GZNQ4ZP1J81T",
                "document",
                "ext_123",
            )
        )

        assert resource.resource_type == "document"
        assert resource.resource_id == "doc_123"
        assert resource.meta == {"title": "Test Document"}
        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith(
            "/authorization/organizations/org_01EHT88Z8J8795GZNQ4ZP1J81T"
            "/resources/document/ext_123"
        )

    # --- update_resource_by_external_id ---

    def test_update_resource_by_external_id_with_meta(
        self, mock_authorization_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_authorization_resource, 200
        )

        resource = syncify(
            self.authorization.update_resource_by_external_id(
                "org_01EHT88Z8J8795GZNQ4ZP1J81T",
                "document",
                "ext_123",
                meta={"title": "Updated Document"},
            )
        )

        assert resource.resource_type == "document"
        assert resource.resource_id == "doc_123"
        assert request_kwargs["method"] == "patch"
        assert request_kwargs["url"].endswith(
            "/authorization/organizations/org_01EHT88Z8J8795GZNQ4ZP1J81T"
            "/resources/document/ext_123"
        )
        assert request_kwargs["json"] == {"meta": {"title": "Updated Document"}}

    def test_update_resource_by_external_id_without_meta(
        self, mock_authorization_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_authorization_resource, 200
        )

        syncify(
            self.authorization.update_resource_by_external_id(
                "org_01EHT88Z8J8795GZNQ4ZP1J81T",
                "document",
                "ext_123",
            )
        )

        assert request_kwargs["method"] == "patch"
        assert request_kwargs["json"] == {}

    # --- delete_resource_by_external_id ---

    def test_delete_resource_by_external_id_without_cascade(
        self, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client,
            status_code=202,
            headers={"content-type": "text/plain; charset=utf-8"},
        )

        response = syncify(
            self.authorization.delete_resource_by_external_id(
                "org_01EHT88Z8J8795GZNQ4ZP1J81T",
                "document",
                "ext_123",
            )
        )

        assert response is None
        assert request_kwargs["method"] == "delete"
        assert request_kwargs["url"].endswith(
            "/authorization/organizations/org_01EHT88Z8J8795GZNQ4ZP1J81T"
            "/resources/document/ext_123"
        )

    def test_delete_resource_by_external_id_with_cascade(
        self, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client,
            status_code=202,
            headers={"content-type": "text/plain; charset=utf-8"},
        )

        response = syncify(
            self.authorization.delete_resource_by_external_id(
                "org_01EHT88Z8J8795GZNQ4ZP1J81T",
                "document",
                "ext_123",
                cascade_delete=True,
            )
        )

        assert response is None
        assert request_kwargs["method"] == "delete"
        assert request_kwargs["url"].endswith(
            "/authorization/organizations/org_01EHT88Z8J8795GZNQ4ZP1J81T"
            "/resources/document/ext_123"
        )
        assert request_kwargs["json"] == {"cascade_delete": True}

    # --- list_resources ---

    def test_list_resources_with_results(self, capture_and_mock_http_client_request):
        mock_resources = [
            {
                "resource_type": "document",
                "resource_id": "doc_1",
                "meta": {"title": "Doc 1"},
                "created_at": "2024-01-01T00:00:00Z",
            },
            {
                "resource_type": "document",
                "resource_id": "doc_2",
                "meta": None,
                "created_at": "2024-01-02T00:00:00Z",
            },
        ]
        mock_response = list_response_of(data=mock_resources)
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_response, 200
        )

        result = syncify(
            self.authorization.list_resources(
                "org_01EHT88Z8J8795GZNQ4ZP1J81T",
            )
        )

        assert len(result.data) == 2
        assert result.data[0].resource_type == "document"
        assert result.data[0].resource_id == "doc_1"
        assert result.data[1].resource_id == "doc_2"
        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith(
            "/authorization/organizations/org_01EHT88Z8J8795GZNQ4ZP1J81T/resources"
        )

    def test_list_resources_empty(self, capture_and_mock_http_client_request):
        mock_response = list_response_of(data=[])
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_response, 200
        )

        result = syncify(
            self.authorization.list_resources(
                "org_01EHT88Z8J8795GZNQ4ZP1J81T",
            )
        )

        assert len(result.data) == 0
        assert request_kwargs["method"] == "get"

    def test_list_resources_with_resource_type_slug_filter(
        self, capture_and_mock_http_client_request
    ):
        mock_response = list_response_of(
            data=[
                {
                    "resource_type": "document",
                    "resource_id": "doc_1",
                    "created_at": "2024-01-01T00:00:00Z",
                }
            ]
        )
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_response, 200
        )

        syncify(
            self.authorization.list_resources(
                "org_01EHT88Z8J8795GZNQ4ZP1J81T",
                resource_type_slug="document",
            )
        )

        assert request_kwargs["params"]["resource_type_slug"] == "document"

    def test_list_resources_with_pagination_params(
        self, capture_and_mock_http_client_request
    ):
        mock_response = list_response_of(data=[])
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_response, 200
        )

        syncify(
            self.authorization.list_resources(
                "org_01EHT88Z8J8795GZNQ4ZP1J81T",
                limit=5,
                after="cursor_abc",
                order="asc",
            )
        )

        assert request_kwargs["params"]["limit"] == 5
        assert request_kwargs["params"]["after"] == "cursor_abc"
        assert request_kwargs["params"]["order"] == "asc"
