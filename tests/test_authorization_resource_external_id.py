from typing import Union

import pytest
from tests.utils.fixtures.mock_resource import MockResource
from tests.utils.list_resource import list_response_of
from tests.utils.syncify import syncify
from tests.types.test_auto_pagination_function import TestAutoPaginationFunction
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
        return MockResource(
            id="res_01ABC",
            external_id=MOCK_EXTERNAL_ID,
            resource_type_slug=MOCK_RESOURCE_TYPE,
            organization_id=MOCK_ORG_ID,
        ).dict()

    @pytest.fixture
    def mock_resources_list(self, mock_resource):
        return list_response_of(data=[mock_resource])

    @pytest.fixture
    def mock_resources_empty_list(self):
        return list_response_of(data=[])

    @pytest.fixture
    def mock_resources_multiple(self):
        resources = [
            MockResource(id=f"res_{i:05d}", external_id=f"ext_{i}").dict()
            for i in range(15)
        ]
        return resources

    # --- get_resource_by_external_id ---

    def test_get_resource_by_external_id(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 200
        )

        resource = syncify(
            self.authorization.get_resource_by_external_id(
                MOCK_ORG_ID, MOCK_RESOURCE_TYPE, MOCK_EXTERNAL_ID
            )
        )

        assert resource.id == "res_01ABC"
        assert resource.external_id == MOCK_EXTERNAL_ID
        assert resource.object == "authorization_resource"
        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith(
            f"/authorization/organizations/{MOCK_ORG_ID}/resources/{MOCK_RESOURCE_TYPE}/{MOCK_EXTERNAL_ID}"
        )

    def test_get_resource_by_external_id_url_construction(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        org_id = "org_different"
        res_type = "folder"
        ext_id = "my-folder-123"

        mock_res = MockResource(
            id="res_02XYZ",
            external_id=ext_id,
            resource_type_slug=res_type,
            organization_id=org_id,
        ).dict()

        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_res, 200
        )

        resource = syncify(
            self.authorization.get_resource_by_external_id(org_id, res_type, ext_id)
        )

        assert resource.id == "res_02XYZ"
        assert request_kwargs["url"].endswith(
            f"/authorization/organizations/{org_id}/resources/{res_type}/{ext_id}"
        )

    # --- update_resource_by_external_id ---

    def test_update_resource_by_external_id_with_name(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 200
        )

        resource = syncify(
            self.authorization.update_resource_by_external_id(
                MOCK_ORG_ID,
                MOCK_RESOURCE_TYPE,
                MOCK_EXTERNAL_ID,
                name="Updated Name",
                description="Updated description",
            )
        )

        assert resource.id == "res_01ABC"
        assert request_kwargs["method"] == "patch"
        assert request_kwargs["url"].endswith(
            f"/authorization/organizations/{MOCK_ORG_ID}/resources/{MOCK_RESOURCE_TYPE}/{MOCK_EXTERNAL_ID}"
        )
        assert request_kwargs["json"] == {
            "name": "Updated Name",
            "description": "Updated description",
        }

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
        assert request_kwargs["json"] == {"description": None}

    def test_update_resource_by_external_id_without_description(
        self, mock_resource, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resource, 200
        )

        resource = syncify(
            self.authorization.update_resource_by_external_id(
                MOCK_ORG_ID, MOCK_RESOURCE_TYPE, MOCK_EXTERNAL_ID, name="Updated Name"
            )
        )

        assert resource.id == "res_01ABC"
        assert request_kwargs["method"] == "patch"
        assert request_kwargs["json"] == {"name": "Updated Name"}

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

        assert response is None
        assert request_kwargs["method"] == "delete"
        assert request_kwargs["url"].endswith(
            f"/authorization/organizations/{MOCK_ORG_ID}/resources/{MOCK_RESOURCE_TYPE}/{MOCK_EXTERNAL_ID}"
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
                MOCK_ORG_ID,
                MOCK_RESOURCE_TYPE,
                MOCK_EXTERNAL_ID,
                cascade_delete=True,
            )
        )

        assert response is None
        assert request_kwargs["method"] == "delete"
        assert request_kwargs["url"].endswith(
            f"/authorization/organizations/{MOCK_ORG_ID}/resources/{MOCK_RESOURCE_TYPE}/{MOCK_EXTERNAL_ID}"
        )
        assert request_kwargs["params"] == {"cascade_delete": "true"}

    # --- list_resources ---

    def test_list_resources_with_results(
        self, mock_resources_list, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list, 200
        )

        resources_response = syncify(
            self.authorization.list_resources(organization_id=MOCK_ORG_ID)
        )

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith("/authorization/resources")
        assert request_kwargs["params"]["organization_id"] == MOCK_ORG_ID
        assert len(resources_response.data) == 1
        assert resources_response.data[0].id == "res_01ABC"

    def test_list_resources_empty_results(
        self, mock_resources_empty_list, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_empty_list, 200
        )

        resources_response = syncify(
            self.authorization.list_resources(organization_id=MOCK_ORG_ID)
        )

        assert request_kwargs["method"] == "get"
        assert len(resources_response.data) == 0

    def test_list_resources_with_resource_type_slug_filter(
        self, mock_resources_list, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list, 200
        )

        syncify(
            self.authorization.list_resources(
                organization_id=MOCK_ORG_ID, resource_type_slug="document"
            )
        )

        assert request_kwargs["method"] == "get"
        assert request_kwargs["params"]["resource_type_slug"] == "document"

    def test_list_resources_with_pagination_params(
        self, mock_resources_list, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list, 200
        )

        syncify(
            self.authorization.list_resources(
                organization_id=MOCK_ORG_ID,
                limit=5,
                after="res_cursor_abc",
                before="res_cursor_xyz",
                order="asc",
            )
        )

        assert request_kwargs["params"]["limit"] == 5
        assert request_kwargs["params"]["after"] == "res_cursor_abc"
        assert request_kwargs["params"]["before"] == "res_cursor_xyz"
        assert request_kwargs["params"]["order"] == "asc"

    def test_list_resources_auto_pagination(
        self,
        mock_resources_multiple,
        test_auto_pagination: TestAutoPaginationFunction,
    ):
        test_auto_pagination(
            http_client=self.http_client,
            list_function=self.authorization.list_resources,
            expected_all_page_data=mock_resources_multiple,
            list_function_params={"organization_id": MOCK_ORG_ID},
        )
