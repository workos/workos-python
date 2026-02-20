from typing import Union

import pytest
from tests.utils.fixtures.mock_resource import MockResource
from tests.utils.list_resource import list_response_of
from tests.utils.syncify import syncify
from workos.authorization import AsyncAuthorization, Authorization


def _mock_membership(
    membership_id: str = "om_01ABC",
    user_id: str = "user_123",
    organization_id: str = "org_456",
    organization_name: str = "Acme Inc",
    status: str = "active",
) -> dict:
    return {
        "object": "organization_membership",
        "id": membership_id,
        "user_id": user_id,
        "organization_id": organization_id,
        "organization_name": organization_name,
        "status": status,
        "custom_attributes": None,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.mark.sync_and_async(Authorization, AsyncAuthorization)
class TestListResourcesForMembership:
    @pytest.fixture(autouse=True)
    def setup(self, module_instance: Union[Authorization, AsyncAuthorization]):
        self.http_client = module_instance._http_client
        self.authorization = module_instance

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

        result = syncify(
            self.authorization.list_resources_for_membership(
                "om_01ABC",
                permission_slug="documents:read",
            )
        )

        assert len(result.data) == 3
        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith(
            "/authorization/organization_memberships/om_01ABC/resources"
        )
        assert request_kwargs["params"]["permission_slug"] == "documents:read"

    def test_list_resources_for_membership_with_parent_resource_id(
        self, mock_resources_list, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list, 200
        )

        syncify(
            self.authorization.list_resources_for_membership(
                "om_01ABC",
                permission_slug="documents:read",
                parent_resource_id="res_parent_01",
            )
        )

        assert request_kwargs["params"]["parent_resource_id"] == "res_parent_01"
        assert "parent_resource_type_slug" not in request_kwargs["params"]
        assert "parent_resource_external_id" not in request_kwargs["params"]

    def test_list_resources_for_membership_with_parent_external_id(
        self, mock_resources_list, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list, 200
        )

        syncify(
            self.authorization.list_resources_for_membership(
                "om_01ABC",
                permission_slug="documents:read",
                parent_resource_type_slug="folder",
                parent_resource_external_id="folder_abc",
            )
        )

        assert request_kwargs["params"]["parent_resource_type_slug"] == "folder"
        assert request_kwargs["params"]["parent_resource_external_id"] == "folder_abc"
        assert "parent_resource_id" not in request_kwargs["params"]

    def test_list_resources_for_membership_rejects_both_parent_id_and_external_id(
        self,
    ):
        with pytest.raises(ValueError, match="Cannot specify both"):
            syncify(
                self.authorization.list_resources_for_membership(
                    "om_01ABC",
                    permission_slug="documents:read",
                    parent_resource_id="res_parent_01",
                    parent_resource_external_id="folder_abc",
                )
            )

    def test_list_resources_for_membership_rejects_type_slug_without_external_id(
        self,
    ):
        with pytest.raises(ValueError, match="must be provided together"):
            syncify(
                self.authorization.list_resources_for_membership(
                    "om_01ABC",
                    permission_slug="documents:read",
                    parent_resource_type_slug="folder",
                )
            )

    def test_list_resources_for_membership_rejects_external_id_without_type_slug(
        self,
    ):
        with pytest.raises(ValueError, match="must be provided together"):
            syncify(
                self.authorization.list_resources_for_membership(
                    "om_01ABC",
                    permission_slug="documents:read",
                    parent_resource_external_id="folder_abc",
                )
            )

    def test_list_resources_for_membership_auto_pagination(
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
                "permission_slug": "documents:read",
            },
            url_path_keys=["organization_membership_id"],
        )


@pytest.mark.sync_and_async(Authorization, AsyncAuthorization)
class TestListMembershipsForResource:
    @pytest.fixture(autouse=True)
    def setup(self, module_instance: Union[Authorization, AsyncAuthorization]):
        self.http_client = module_instance._http_client
        self.authorization = module_instance

    @pytest.fixture
    def mock_memberships_list(self):
        memberships = [_mock_membership(membership_id=f"om_{i}") for i in range(3)]
        return {
            "data": memberships,
            "list_metadata": {"before": None, "after": None},
            "object": "list",
        }

    @pytest.fixture
    def mock_empty_memberships_list(self):
        return {
            "data": [],
            "list_metadata": {"before": None, "after": None},
            "object": "list",
        }

    @pytest.fixture
    def mock_memberships_multiple_pages(self):
        memberships = [_mock_membership(membership_id=f"om_{i}") for i in range(40)]
        return list_response_of(data=memberships)

    def test_list_memberships_for_resource(
        self, mock_memberships_list, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_memberships_list, 200
        )

        result = syncify(
            self.authorization.list_memberships_for_resource(
                "res_01ABC",
                permission_slug="documents:read",
            )
        )

        assert len(result.data) == 3
        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith(
            "/authorization/resources/res_01ABC/organization_memberships"
        )
        assert request_kwargs["params"]["permission_slug"] == "documents:read"

    def test_list_memberships_for_resource_empty(
        self, mock_empty_memberships_list, capture_and_mock_http_client_request
    ):
        capture_and_mock_http_client_request(
            self.http_client, mock_empty_memberships_list, 200
        )

        result = syncify(
            self.authorization.list_memberships_for_resource(
                "res_01ABC",
                permission_slug="documents:read",
            )
        )

        assert len(result.data) == 0

    def test_list_memberships_for_resource_with_assignment(
        self, mock_memberships_list, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_memberships_list, 200
        )

        syncify(
            self.authorization.list_memberships_for_resource(
                "res_01ABC",
                permission_slug="documents:read",
                assignment="direct",
            )
        )

        assert request_kwargs["params"]["assignment"] == "direct"

    def test_list_memberships_for_resource_auto_pagination(
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
                "permission_slug": "documents:read",
            },
            url_path_keys=["resource_id"],
        )


@pytest.mark.sync_and_async(Authorization, AsyncAuthorization)
class TestListMembershipsForResourceByExternalId:
    @pytest.fixture(autouse=True)
    def setup(self, module_instance: Union[Authorization, AsyncAuthorization]):
        self.http_client = module_instance._http_client
        self.authorization = module_instance

    @pytest.fixture
    def mock_memberships_list(self):
        memberships = [_mock_membership(membership_id=f"om_{i}") for i in range(3)]
        return {
            "data": memberships,
            "list_metadata": {"before": None, "after": None},
            "object": "list",
        }

    @pytest.fixture
    def mock_memberships_multiple_pages(self):
        memberships = [_mock_membership(membership_id=f"om_{i}") for i in range(40)]
        return list_response_of(data=memberships)

    def test_list_memberships_for_resource_by_external_id(
        self, mock_memberships_list, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_memberships_list, 200
        )

        result = syncify(
            self.authorization.list_memberships_for_resource_by_external_id(
                "org_456",
                "document",
                "doc_abc",
                permission_slug="documents:read",
            )
        )

        assert len(result.data) == 3
        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith(
            "/authorization/organizations/org_456/resources/document/doc_abc/organization_memberships"
        )
        assert request_kwargs["params"]["permission_slug"] == "documents:read"

    def test_list_memberships_for_resource_by_external_id_with_assignment(
        self, mock_memberships_list, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_memberships_list, 200
        )

        syncify(
            self.authorization.list_memberships_for_resource_by_external_id(
                "org_456",
                "document",
                "doc_abc",
                permission_slug="documents:read",
                assignment="indirect",
            )
        )

        assert request_kwargs["params"]["assignment"] == "indirect"

    def test_list_memberships_for_resource_by_external_id_auto_pagination(
        self,
        mock_memberships_multiple_pages,
        test_auto_pagination,
    ):
        test_auto_pagination(
            http_client=self.http_client,
            list_function=self.authorization.list_memberships_for_resource_by_external_id,
            expected_all_page_data=mock_memberships_multiple_pages["data"],
            list_function_params={
                "organization_id": "org_456",
                "resource_type_slug": "document",
                "external_id": "doc_abc",
                "permission_slug": "documents:read",
            },
            url_path_keys=["organization_id", "resource_type_slug", "external_id"],
        )
