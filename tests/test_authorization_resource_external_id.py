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
        return MockAuthorizationResource().dict()

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

        assert response.dict() == MockAuthorizationResource().dict()

    def test_get_resource_by_external_id_without_parent(
        self, capture_and_mock_http_client_request
    ):
        mock_resource = MockAuthorizationResource(parent_resource_id=None).dict()
        capture_and_mock_http_client_request(self.http_client, mock_resource, 200)

        response = syncify(
            self.authorization.get_resource_by_external_id(
                MOCK_ORG_ID, MOCK_RESOURCE_TYPE, MOCK_EXTERNAL_ID
            )
        )

        assert (
            response.dict() == MockAuthorizationResource(parent_resource_id=None).dict()
        )

    def test_get_resource_by_external_id_without_description(
        self, capture_and_mock_http_client_request
    ):
        mock_resource = MockAuthorizationResource(description=None).dict()
        capture_and_mock_http_client_request(self.http_client, mock_resource, 200)

        response = syncify(
            self.authorization.get_resource_by_external_id(
                MOCK_ORG_ID, MOCK_RESOURCE_TYPE, MOCK_EXTERNAL_ID
            )
        )

        assert response.dict() == MockAuthorizationResource(description=None).dict()

    def test_get_resource_by_external_id_without_parent_and_description(
        self, capture_and_mock_http_client_request
    ):
        mock_resource = MockAuthorizationResource(
            parent_resource_id=None, description=None
        ).dict()
        capture_and_mock_http_client_request(self.http_client, mock_resource, 200)

        response = syncify(
            self.authorization.get_resource_by_external_id(
                MOCK_ORG_ID, MOCK_RESOURCE_TYPE, MOCK_EXTERNAL_ID
            )
        )

        assert (
            response.dict()
            == MockAuthorizationResource(
                parent_resource_id=None, description=None
            ).dict()
        )

    # --- update_resource_by_external_id ---

    def test_update_resource_by_external_id_name_only(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        updated_resource = MockAuthorizationResource(name="New Name").dict()
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, updated_resource, 200
        )

        response = syncify(
            self.authorization.update_resource_by_external_id(
                MOCK_ORG_ID, MOCK_RESOURCE_TYPE, MOCK_EXTERNAL_ID, name="New Name"
            )
        )

        assert request_kwargs["method"] == "patch"
        assert request_kwargs["url"].endswith(
            f"/authorization/organizations/{MOCK_ORG_ID}/resources/{MOCK_RESOURCE_TYPE}/{MOCK_EXTERNAL_ID}"
        )
        assert request_kwargs["json"] == {"name": "New Name"}

        assert (
            response.dict()
            == MockAuthorizationResource(
                name="New Name",
            ).dict()
        )

    def test_update_resource_by_external_id_description_only(
        self, capture_and_mock_http_client_request
    ):
        updated_resource = MockAuthorizationResource(
            description="Updated description only",
        ).dict()
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, updated_resource, 200
        )

        response = syncify(
            self.authorization.update_resource_by_external_id(
                MOCK_ORG_ID,
                MOCK_RESOURCE_TYPE,
                MOCK_EXTERNAL_ID,
                description="Updated description only",
            )
        )

        assert request_kwargs["method"] == "patch"
        assert request_kwargs["url"].endswith(
            f"/authorization/organizations/{MOCK_ORG_ID}/resources/{MOCK_RESOURCE_TYPE}/{MOCK_EXTERNAL_ID}"
        )
        assert request_kwargs["json"] == {
            "description": "Updated description only",
        }

        assert (
            response.dict()
            == MockAuthorizationResource(
                description="Updated description only",
            ).dict()
        )

    def test_update_resource_by_external_id_name_and_description(
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

        assert (
            response.dict()
            == MockAuthorizationResource(
                name="Updated Name",
                description="Updated description",
            ).dict()
        )

    def test_update_resource_by_external_id_remove_description(
        self, capture_and_mock_http_client_request
    ):
        updated_resource = MockAuthorizationResource(description=None).dict()
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, updated_resource, 200
        )

        response = syncify(
            self.authorization.update_resource_by_external_id(
                MOCK_ORG_ID,
                MOCK_RESOURCE_TYPE,
                MOCK_EXTERNAL_ID,
                description=None,
            )
        )

        assert request_kwargs["method"] == "patch"
        assert request_kwargs["url"].endswith(
            f"/authorization/organizations/{MOCK_ORG_ID}/resources/{MOCK_RESOURCE_TYPE}/{MOCK_EXTERNAL_ID}"
        )
        assert request_kwargs["json"] == {"description": None}

        assert (
            response.dict()
            == MockAuthorizationResource(
                description=None,
            ).dict()
        )

    # --- delete_resource_by_external_id ---

    def test_delete_resource_by_external_id_without_cascade(
        self, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client,
            status_code=204,
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

    def test_delete_resource_by_external_id_with_cascade_true(
        self, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client,
            status_code=204,
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
            status_code=204,
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
