from typing import Union

import pytest
from tests.utils.fixtures.mock_resource import MockResource
from tests.utils.list_resource import list_response_of
from tests.utils.syncify import syncify
from workos.authorization import AsyncAuthorization, Authorization


def _mock_membership(
    id: str = "om_01ABC",
    user_id: str = "user_01ABC",
    organization_id: str = "org_01ABC",
) -> dict:
    """Build a minimal organization-membership dict for test responses.

    Includes ``custom_attributes: None`` so that the dict round-trips
    identically through the Pydantic model's ``.dict()`` serialisation
    (the model defines a default of ``None`` for that field).
    """
    return {
        "object": "organization_membership",
        "id": id,
        "user_id": user_id,
        "organization_id": organization_id,
        "organization_name": "Test Org",
        "status": "active",
        "custom_attributes": None,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.mark.sync_and_async(Authorization, AsyncAuthorization)
class TestAuthorizationResourceMemberships:
    @pytest.fixture(autouse=True)
    def setup(self, module_instance: Union[Authorization, AsyncAuthorization]):
        self.http_client = module_instance._http_client
        self.authorization = module_instance

    # ------------------------------------------------------------------
    # list_resources_for_membership
    # ------------------------------------------------------------------

    @pytest.fixture
    def mock_resources_list(self):
        resources = [MockResource(id=f"res_{i}").dict() for i in range(3)]
        return {
            "data": resources,
            "list_metadata": {"before": None, "after": None},
            "object": "list",
        }

    @pytest.fixture
    def mock_resources_multiple_pages(self):
        resources = [MockResource(id=f"res_{i}").dict() for i in range(40)]
        return list_response_of(data=resources)

    def test_list_resources_for_membership(
        self, mock_resources_list, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list, 200
        )

        result = syncify(self.authorization.list_resources_for_membership("om_01ABC"))

        assert len(result.data) == 3
        assert result.data[0].id == "res_0"
        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith(
            "/authorization/organization_memberships/om_01ABC/resources"
        )

    def test_list_resources_for_membership_with_resource_type_filter(
        self, mock_resources_list, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list, 200
        )

        syncify(
            self.authorization.list_resources_for_membership(
                "om_01ABC", resource_type="document"
            )
        )

        assert request_kwargs["params"]["resource_type"] == "document"

    def test_list_resources_for_membership_with_parent_by_id(
        self, mock_resources_list, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list, 200
        )

        syncify(
            self.authorization.list_resources_for_membership(
                "om_01ABC", parent_resource_id="res_01PARENT"
            )
        )

        assert request_kwargs["params"]["parent_resource_id"] == "res_01PARENT"
        assert "parent_organization_id" not in request_kwargs["params"]

    def test_list_resources_for_membership_with_parent_by_external_id(
        self, mock_resources_list, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list, 200
        )

        syncify(
            self.authorization.list_resources_for_membership(
                "om_01ABC",
                parent_organization_id="org_01ABC",
                parent_resource_type="folder",
                parent_external_id="ext_parent_456",
            )
        )

        assert request_kwargs["params"]["parent_organization_id"] == "org_01ABC"
        assert request_kwargs["params"]["parent_resource_type"] == "folder"
        assert request_kwargs["params"]["parent_external_id"] == "ext_parent_456"
        assert "parent_resource_id" not in request_kwargs["params"]

    def test_list_resources_for_membership_mutual_exclusivity(self):
        with pytest.raises(ValueError, match="mutually exclusive"):
            syncify(
                self.authorization.list_resources_for_membership(
                    "om_01ABC",
                    parent_resource_id="res_01PARENT",
                    parent_organization_id="org_01ABC",
                )
            )

    def test_list_resources_for_membership_pagination(
        self,
        mock_resources_multiple_pages,
        test_auto_pagination,
    ):
        test_auto_pagination(
            http_client=self.http_client,
            list_function=self.authorization.list_resources_for_membership,
            expected_all_page_data=mock_resources_multiple_pages["data"],
            list_function_params={
                "organization_membership_id": "om_01ABC",
            },
            url_path_keys=["organization_membership_id"],
        )

    # ------------------------------------------------------------------
    # list_memberships_for_resource
    # ------------------------------------------------------------------

    @pytest.fixture
    def mock_memberships_list(self):
        memberships = [_mock_membership(id=f"om_{i}") for i in range(3)]
        return {
            "data": memberships,
            "list_metadata": {"before": None, "after": None},
            "object": "list",
        }

    @pytest.fixture
    def mock_memberships_empty(self):
        return {
            "data": [],
            "list_metadata": {"before": None, "after": None},
            "object": "list",
        }

    @pytest.fixture
    def mock_memberships_multiple_pages(self):
        memberships = [_mock_membership(id=f"om_{i}") for i in range(40)]
        return list_response_of(data=memberships)

    def test_list_memberships_for_resource(
        self, mock_memberships_list, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_memberships_list, 200
        )

        result = syncify(self.authorization.list_memberships_for_resource("res_01ABC"))

        assert len(result.data) == 3
        assert result.data[0].id == "om_0"
        assert result.data[0].object == "organization_membership"
        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith(
            "/authorization/resources/res_01ABC/organization_memberships"
        )

    def test_list_memberships_for_resource_empty(
        self, mock_memberships_empty, capture_and_mock_http_client_request
    ):
        capture_and_mock_http_client_request(
            self.http_client, mock_memberships_empty, 200
        )

        result = syncify(self.authorization.list_memberships_for_resource("res_01ABC"))

        assert len(result.data) == 0

    def test_list_memberships_for_resource_pagination(
        self,
        mock_memberships_multiple_pages,
        test_auto_pagination,
    ):
        test_auto_pagination(
            http_client=self.http_client,
            list_function=self.authorization.list_memberships_for_resource,
            expected_all_page_data=mock_memberships_multiple_pages["data"],
            list_function_params={
                "resource_id": "res_01ABC",
            },
            url_path_keys=["resource_id"],
        )

    # ------------------------------------------------------------------
    # list_memberships_for_resource_by_external_id
    # ------------------------------------------------------------------

    def test_list_memberships_for_resource_by_external_id(
        self, mock_memberships_list, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_memberships_list, 200
        )

        result = syncify(
            self.authorization.list_memberships_for_resource_by_external_id(
                "org_01ABC", "document", "ext_123"
            )
        )

        assert len(result.data) == 3
        assert result.data[0].id == "om_0"
        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith(
            "/authorization/organizations/org_01ABC/resources/document/ext_123/organization_memberships"
        )

    def test_list_memberships_for_resource_by_external_id_pagination(
        self,
        mock_memberships_multiple_pages,
        test_auto_pagination,
    ):
        test_auto_pagination(
            http_client=self.http_client,
            list_function=self.authorization.list_memberships_for_resource_by_external_id,
            expected_all_page_data=mock_memberships_multiple_pages["data"],
            list_function_params={
                "organization_id": "org_01ABC",
                "resource_type": "document",
                "external_id": "ext_123",
            },
            url_path_keys=["organization_id", "resource_type", "external_id"],
        )
