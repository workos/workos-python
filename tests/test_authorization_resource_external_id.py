from typing import Union

import pytest
from tests.utils.fixtures.mock_resource import MockAuthorizationResource
from tests.utils.syncify import syncify
from workos.authorization import AsyncAuthorization, Authorization


MOCK_ORG_ID = "org_01EHT88Z8J8795GZNQ4ZP1J81T"
MOCK_RESOURCE_TYPE = "document"
MOCK_EXTERNAL_ID = "ext_123"


@pytest.mark.sync_and_async(Authorization, AsyncAuthorization)
class TestAuthorizationResourceExternalId:
    @pytest.fixture(autouse=True)
    def setup(self, module_instance: Union[Authorization, AsyncAuthorization]):
        self.http_client = module_instance._http_client
        self.authorization = module_instance

    @pytest.fixture
    def mock_resource(self):
        return MockAuthorizationResource(
            id="res_01ABC",
            external_id=MOCK_EXTERNAL_ID,
            resource_type_slug=MOCK_RESOURCE_TYPE,
            organization_id=MOCK_ORG_ID,
        ).dict()

    # --- get_resource_by_external_id ---

    def test_get_resource_by_external_id(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 200
        )

        response = syncify(
            self.authorization.get_resource_by_external_id(
                MOCK_ORG_ID, MOCK_RESOURCE_TYPE, MOCK_EXTERNAL_ID
            )
        )

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith(
            f"/authorization/organizations/{MOCK_ORG_ID}/resources/{MOCK_RESOURCE_TYPE}/{MOCK_EXTERNAL_ID}"
        )
        assert response.id == "res_01ABC"
        assert response.external_id == MOCK_EXTERNAL_ID
        assert response.object == "authorization_resource"
        assert response.description == "A test resource for unit tests"
        assert response.parent_resource_id == "res_01XYZ"
        assert response.created_at == "2024-01-15T12:00:00.000Z"
        assert response.updated_at == "2024-01-15T12:00:00.000Z"

    def test_get_resource_by_external_id_url_construction(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        org_id = "org_different"
        res_type = "folder"
        ext_id = "my-folder-123"

        mock_res = MockAuthorizationResource(
            id="res_02XYZ",
            external_id=ext_id,
            resource_type_slug=res_type,
            organization_id=org_id,
        ).dict()

        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_res, 200
        )

        response = syncify(
            self.authorization.get_resource_by_external_id(org_id, res_type, ext_id)
        )

        assert request_kwargs["url"].endswith(
            f"/authorization/organizations/{org_id}/resources/{res_type}/{ext_id}"
        )
        assert response.id == "res_02XYZ"
        assert response.description == "A test resource for unit tests"
        assert response.parent_resource_id == "res_01XYZ"
        assert response.created_at == "2024-01-15T12:00:00.000Z"
        assert response.updated_at == "2024-01-15T12:00:00.000Z"

    # --- update_resource_by_external_id ---

    def test_update_resource_by_external_id_with_name(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 200
        )

        response = syncify(
            self.authorization.update_resource_by_external_id(
                MOCK_ORG_ID,
                MOCK_RESOURCE_TYPE,
                MOCK_EXTERNAL_ID,
                name="Updated Name",
                description="Updated description",
            )
        )

        assert request_kwargs["method"] == "patch"
        assert request_kwargs["url"].endswith(
            f"/authorization/organizations/{MOCK_ORG_ID}/resources/{MOCK_RESOURCE_TYPE}/{MOCK_EXTERNAL_ID}"
        )
        assert request_kwargs["json"] == {
            "name": "Updated Name",
            "description": "Updated description",
        }
        assert response.id == "res_01ABC"

    def test_update_resource_by_external_id_empty(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 200
        )

        syncify(
            self.authorization.update_resource_by_external_id(
                MOCK_ORG_ID, MOCK_RESOURCE_TYPE, MOCK_EXTERNAL_ID
            )
        )

        assert request_kwargs["method"] == "patch"
        assert request_kwargs["url"].endswith(
            f"/authorization/organizations/{MOCK_ORG_ID}/resources/{MOCK_RESOURCE_TYPE}/{MOCK_EXTERNAL_ID}"
        )
        assert request_kwargs["json"] == {}

    def test_update_resource_by_external_id_clear_description(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 200
        )

        syncify(
            self.authorization.update_resource_by_external_id(
                MOCK_ORG_ID, MOCK_RESOURCE_TYPE, MOCK_EXTERNAL_ID, description=None
            )
        )

        assert request_kwargs["method"] == "patch"
        assert request_kwargs["url"].endswith(
            f"/authorization/organizations/{MOCK_ORG_ID}/resources/{MOCK_RESOURCE_TYPE}/{MOCK_EXTERNAL_ID}"
        )
        assert request_kwargs["json"] == {"description": None}

    def test_update_resource_by_external_id_without_description(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 200
        )

        response = syncify(
            self.authorization.update_resource_by_external_id(
                MOCK_ORG_ID, MOCK_RESOURCE_TYPE, MOCK_EXTERNAL_ID, name="Updated Name"
            )
        )

        assert request_kwargs["method"] == "patch"
        assert request_kwargs["url"].endswith(
            f"/authorization/organizations/{MOCK_ORG_ID}/resources/{MOCK_RESOURCE_TYPE}/{MOCK_EXTERNAL_ID}"
        )
        assert request_kwargs["json"] == {"name": "Updated Name"}
        assert response.id == "res_01ABC"

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
                MOCK_ORG_ID, MOCK_RESOURCE_TYPE, MOCK_EXTERNAL_ID
            )
        )

        assert request_kwargs["method"] == "delete"
        assert request_kwargs["url"].endswith(
            f"/authorization/organizations/{MOCK_ORG_ID}/resources/{MOCK_RESOURCE_TYPE}/{MOCK_EXTERNAL_ID}"
        )
        assert request_kwargs.get("params") is None
        assert response is None

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
                MOCK_ORG_ID,
                MOCK_RESOURCE_TYPE,
                MOCK_EXTERNAL_ID,
                cascade_delete=True,
            )
        )

        assert request_kwargs["method"] == "delete"
        assert request_kwargs["url"].endswith(
            f"/authorization/organizations/{MOCK_ORG_ID}/resources/{MOCK_RESOURCE_TYPE}/{MOCK_EXTERNAL_ID}"
        )
        assert request_kwargs["params"] == {"cascade_delete": "true"}
        assert response is None

    def test_delete_resource_by_external_id_with_cascade_false(
        self, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client,
            status_code=202,
            headers={"content-type": "text/plain; charset=utf-8"},
        )

        response = syncify(
            self.authorization.delete_resource_by_external_id(
                MOCK_ORG_ID,
                MOCK_RESOURCE_TYPE,
                MOCK_EXTERNAL_ID,
                cascade_delete=False,
            )
        )

        assert request_kwargs["method"] == "delete"
        assert request_kwargs["url"].endswith(
            f"/authorization/organizations/{MOCK_ORG_ID}/resources/{MOCK_RESOURCE_TYPE}/{MOCK_EXTERNAL_ID}"
        )
        assert request_kwargs["params"] == {"cascade_delete": "false"}
        assert response is None
