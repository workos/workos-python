from typing import Union

import pytest
from tests.utils.fixtures.mock_organization_membership import (
    MockAuthorizationOrganizationMembershipList,
)
from tests.utils.fixtures.mock_resource_list import MockAuthorizationResourceList
from tests.utils.syncify import syncify
from workos.authorization import AsyncAuthorization, Authorization
from workos.types.authorization.parent_resource_identifier import (
    ParentResourceByExternalId,
    ParentResourceById,
)


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
    def mock_resources_list_two(self):
        return MockAuthorizationResourceList().dict()

    # --- list_resources_for_membership with ParentResourceById ---

    def test_list_resources_for_membership_with_parent_by_id_returns_paginated_list(
        self, mock_resources_list_two, capture_and_mock_http_client_request
    ):
        parent = ParentResourceById(parent_resource_id="res_parent_123")
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list_two, 200
        )

        response = syncify(
            self.authorization.list_resources_for_membership(
                "om_01ABC",
                permission_slug="document:read",
                parent_resource=parent,
            )
        )

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith(
            "/authorization/organization_memberships/om_01ABC/resources"
        )
        assert request_kwargs["params"]["parent_resource_id"] == "res_parent_123"
        assert request_kwargs["params"]["permission_slug"] == "document:read"
        assert request_kwargs["params"]["limit"] == 10
        assert request_kwargs["params"]["order"] == "desc"

        assert response.object == "list"
        assert len(response.data) == 2
        assert response.data[0].id == "authz_resource_01HXYZ123ABC456DEF789ABC"
        assert response.data[0].external_id == "doc-12345678"
        assert response.list_metadata.before is None
        assert response.list_metadata.after == "authz_resource_01HXYZ123ABC456DEF789DEF"

    def test_list_resources_for_membership_with_parent_by_id_with_limit(
        self, mock_resources_list_two, capture_and_mock_http_client_request
    ):
        parent = ParentResourceById(parent_resource_id="res_parent_123")
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list_two, 200
        )

        syncify(
            self.authorization.list_resources_for_membership(
                "om_01ABC",
                permission_slug="document:read",
                parent_resource=parent,
                limit=25,
            )
        )

        assert request_kwargs["params"]["parent_resource_id"] == "res_parent_123"
        assert request_kwargs["params"]["permission_slug"] == "document:read"
        assert request_kwargs["params"]["limit"] == 25
        assert request_kwargs["params"]["order"] == "desc"

    def test_list_resources_for_membership_with_parent_by_id_with_before(
        self, mock_resources_list_two, capture_and_mock_http_client_request
    ):
        parent = ParentResourceById(parent_resource_id="res_parent_123")
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list_two, 200
        )

        syncify(
            self.authorization.list_resources_for_membership(
                "om_01ABC",
                permission_slug="document:read",
                parent_resource=parent,
                before="cursor_before",
            )
        )

        assert request_kwargs["params"]["parent_resource_id"] == "res_parent_123"
        assert request_kwargs["params"]["before"] == "cursor_before"
        assert request_kwargs["params"]["limit"] == 10
        assert request_kwargs["params"]["order"] == "desc"

    def test_list_resources_for_membership_with_parent_by_id_with_after(
        self, mock_resources_list_two, capture_and_mock_http_client_request
    ):
        parent = ParentResourceById(parent_resource_id="res_parent_123")
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list_two, 200
        )

        syncify(
            self.authorization.list_resources_for_membership(
                "om_01ABC",
                permission_slug="document:read",
                parent_resource=parent,
                after="cursor_after",
            )
        )

        assert request_kwargs["params"]["parent_resource_id"] == "res_parent_123"
        assert request_kwargs["params"]["after"] == "cursor_after"
        assert request_kwargs["params"]["limit"] == 10
        assert request_kwargs["params"]["order"] == "desc"

    def test_list_resources_for_membership_with_parent_by_id_with_order_asc(
        self, mock_resources_list_two, capture_and_mock_http_client_request
    ):
        parent = ParentResourceById(parent_resource_id="res_parent_123")
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list_two, 200
        )

        syncify(
            self.authorization.list_resources_for_membership(
                "om_01ABC",
                permission_slug="document:read",
                parent_resource=parent,
                order="asc",
            )
        )

        assert request_kwargs["params"]["parent_resource_id"] == "res_parent_123"
        assert request_kwargs["params"]["order"] == "asc"
        assert request_kwargs["params"]["limit"] == 10

    def test_list_resources_for_membership_with_parent_by_id_with_order_desc(
        self, mock_resources_list_two, capture_and_mock_http_client_request
    ):
        parent = ParentResourceById(parent_resource_id="res_parent_123")
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list_two, 200
        )

        syncify(
            self.authorization.list_resources_for_membership(
                "om_01ABC",
                permission_slug="document:read",
                parent_resource=parent,
                order="desc",
            )
        )

        assert request_kwargs["params"]["parent_resource_id"] == "res_parent_123"
        assert request_kwargs["params"]["order"] == "desc"
        assert request_kwargs["params"]["limit"] == 10

    def test_list_resources_for_membership_with_parent_by_id_with_all_parameters(
        self, mock_resources_list_two, capture_and_mock_http_client_request
    ):
        parent = ParentResourceById(parent_resource_id="res_parent_123")
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list_two, 200
        )

        response = syncify(
            self.authorization.list_resources_for_membership(
                "om_01ABC",
                permission_slug="document:read",
                parent_resource=parent,
                limit=5,
                before="cursor_before",
                after="cursor_after",
                order="asc",
            )
        )

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith(
            "/authorization/organization_memberships/om_01ABC/resources"
        )
        assert request_kwargs["params"]["parent_resource_id"] == "res_parent_123"
        assert request_kwargs["params"]["permission_slug"] == "document:read"
        assert request_kwargs["params"]["limit"] == 5
        assert request_kwargs["params"]["before"] == "cursor_before"
        assert request_kwargs["params"]["after"] == "cursor_after"
        assert request_kwargs["params"]["order"] == "asc"

        assert response.object == "list"
        assert len(response.data) == 2

    # --- list_resources_for_membership with ParentResourceByExternalId ---

    def test_list_resources_for_membership_with_parent_by_external_id_returns_paginated_list(
        self, mock_resources_list_two, capture_and_mock_http_client_request
    ):
        parent = ParentResourceByExternalId(
            parent_resource_external_id="parent_ext_456",
            parent_resource_type_slug="folder",
        )
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list_two, 200
        )

        response = syncify(
            self.authorization.list_resources_for_membership(
                "om_01ABC",
                permission_slug="document:read",
                parent_resource=parent,
            )
        )

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith(
            "/authorization/organization_memberships/om_01ABC/resources"
        )
        assert (
            request_kwargs["params"]["parent_resource_external_id"] == "parent_ext_456"
        )
        assert request_kwargs["params"]["parent_resource_type_slug"] == "folder"
        assert request_kwargs["params"]["permission_slug"] == "document:read"
        assert request_kwargs["params"]["limit"] == 10
        assert request_kwargs["params"]["order"] == "desc"
        assert "parent_resource_id" not in request_kwargs["params"]

        assert response.object == "list"
        assert len(response.data) == 2
        assert response.data[0].id == "authz_resource_01HXYZ123ABC456DEF789ABC"
        assert response.list_metadata.before is None

    def test_list_resources_for_membership_with_parent_by_external_id_with_limit(
        self, mock_resources_list_two, capture_and_mock_http_client_request
    ):
        parent = ParentResourceByExternalId(
            parent_resource_external_id="parent_ext_456",
            parent_resource_type_slug="folder",
        )
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list_two, 200
        )

        syncify(
            self.authorization.list_resources_for_membership(
                "om_01ABC",
                permission_slug="document:read",
                parent_resource=parent,
                limit=25,
            )
        )

        assert (
            request_kwargs["params"]["parent_resource_external_id"] == "parent_ext_456"
        )
        assert request_kwargs["params"]["parent_resource_type_slug"] == "folder"
        assert request_kwargs["params"]["limit"] == 25
        assert request_kwargs["params"]["order"] == "desc"

    def test_list_resources_for_membership_with_parent_by_external_id_with_before(
        self, mock_resources_list_two, capture_and_mock_http_client_request
    ):
        parent = ParentResourceByExternalId(
            parent_resource_external_id="parent_ext_456",
            parent_resource_type_slug="folder",
        )
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list_two, 200
        )

        syncify(
            self.authorization.list_resources_for_membership(
                "om_01ABC",
                permission_slug="document:read",
                parent_resource=parent,
                before="cursor_before",
            )
        )

        assert (
            request_kwargs["params"]["parent_resource_external_id"] == "parent_ext_456"
        )
        assert request_kwargs["params"]["before"] == "cursor_before"
        assert request_kwargs["params"]["limit"] == 10
        assert request_kwargs["params"]["order"] == "desc"

    def test_list_resources_for_membership_with_parent_by_external_id_with_after(
        self, mock_resources_list_two, capture_and_mock_http_client_request
    ):
        parent = ParentResourceByExternalId(
            parent_resource_external_id="parent_ext_456",
            parent_resource_type_slug="folder",
        )
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list_two, 200
        )

        syncify(
            self.authorization.list_resources_for_membership(
                "om_01ABC",
                permission_slug="document:read",
                parent_resource=parent,
                after="cursor_after",
            )
        )

        assert (
            request_kwargs["params"]["parent_resource_external_id"] == "parent_ext_456"
        )
        assert request_kwargs["params"]["after"] == "cursor_after"
        assert request_kwargs["params"]["limit"] == 10
        assert request_kwargs["params"]["order"] == "desc"

    def test_list_resources_for_membership_with_parent_by_external_id_with_order_asc(
        self, mock_resources_list_two, capture_and_mock_http_client_request
    ):
        parent = ParentResourceByExternalId(
            parent_resource_external_id="parent_ext_456",
            parent_resource_type_slug="folder",
        )
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list_two, 200
        )

        syncify(
            self.authorization.list_resources_for_membership(
                "om_01ABC",
                permission_slug="document:read",
                parent_resource=parent,
                order="asc",
            )
        )

        assert (
            request_kwargs["params"]["parent_resource_external_id"] == "parent_ext_456"
        )
        assert request_kwargs["params"]["order"] == "asc"
        assert request_kwargs["params"]["limit"] == 10

    def test_list_resources_for_membership_with_parent_by_external_id_with_order_desc(
        self, mock_resources_list_two, capture_and_mock_http_client_request
    ):
        parent = ParentResourceByExternalId(
            parent_resource_external_id="parent_ext_456",
            parent_resource_type_slug="folder",
        )
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list_two, 200
        )

        syncify(
            self.authorization.list_resources_for_membership(
                "om_01ABC",
                permission_slug="document:read",
                parent_resource=parent,
                order="desc",
            )
        )

        assert (
            request_kwargs["params"]["parent_resource_external_id"] == "parent_ext_456"
        )
        assert request_kwargs["params"]["order"] == "desc"
        assert request_kwargs["params"]["limit"] == 10

    def test_list_resources_for_membership_with_parent_by_external_id_with_all_parameters(
        self, mock_resources_list_two, capture_and_mock_http_client_request
    ):
        parent = ParentResourceByExternalId(
            parent_resource_external_id="parent_ext_456",
            parent_resource_type_slug="folder",
        )
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_resources_list_two, 200
        )

        response = syncify(
            self.authorization.list_resources_for_membership(
                "om_01ABC",
                permission_slug="document:read",
                parent_resource=parent,
                limit=5,
                before="cursor_before",
                after="cursor_after",
                order="asc",
            )
        )

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith(
            "/authorization/organization_memberships/om_01ABC/resources"
        )
        assert (
            request_kwargs["params"]["parent_resource_external_id"] == "parent_ext_456"
        )
        assert request_kwargs["params"]["parent_resource_type_slug"] == "folder"
        assert request_kwargs["params"]["permission_slug"] == "document:read"
        assert request_kwargs["params"]["limit"] == 5
        assert request_kwargs["params"]["before"] == "cursor_before"
        assert request_kwargs["params"]["after"] == "cursor_after"
        assert request_kwargs["params"]["order"] == "asc"
        assert "parent_resource_id" not in request_kwargs["params"]

        assert response.object == "list"
        assert len(response.data) == 2


@pytest.mark.sync_and_async(Authorization, AsyncAuthorization)
class TestListMembershipsForResource:
    @pytest.fixture(autouse=True)
    def setup(self, module_instance: Union[Authorization, AsyncAuthorization]):
        self.http_client = module_instance._http_client
        self.authorization = module_instance

    @pytest.fixture
    def mock_memberships_list_two(self):
        return MockAuthorizationOrganizationMembershipList().model_dump()

    # --- list_memberships_for_resource (by resource_id) ---

    def test_list_memberships_for_resource_returns_paginated_list(
        self, mock_memberships_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_memberships_list_two, 200
        )

        response = syncify(
            self.authorization.list_memberships_for_resource(
                "authz_resource_01HXYZ123ABC456DEF789ABC",
                permission_slug="document:read",
            )
        )

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith(
            "/authorization/resources/authz_resource_01HXYZ123ABC456DEF789ABC/organization_memberships"
        )
        assert request_kwargs["params"]["permission_slug"] == "document:read"
        assert request_kwargs["params"]["limit"] == 10
        assert request_kwargs["params"]["order"] == "desc"

        assert response.object == "list"
        assert len(response.data) == 2
        assert response.data[0].id == "om_01ABC"
        assert response.data[0].user_id == "user_123"
        assert response.list_metadata.before is None
        assert response.list_metadata.after == "om_01DEF"

    def test_list_memberships_for_resource_with_assignment_direct(
        self, mock_memberships_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_memberships_list_two, 200
        )

        syncify(
            self.authorization.list_memberships_for_resource(
                "authz_resource_01HXYZ",
                permission_slug="document:read",
                assignment="direct",
            )
        )

        assert request_kwargs["params"]["permission_slug"] == "document:read"
        assert request_kwargs["params"]["assignment"] == "direct"
        assert request_kwargs["params"]["limit"] == 10
        assert request_kwargs["params"]["order"] == "desc"

    def test_list_memberships_for_resource_with_assignment_indirect(
        self, mock_memberships_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_memberships_list_two, 200
        )

        syncify(
            self.authorization.list_memberships_for_resource(
                "authz_resource_01HXYZ",
                permission_slug="document:read",
                assignment="indirect",
            )
        )

        assert request_kwargs["params"]["assignment"] == "indirect"
        assert request_kwargs["params"]["permission_slug"] == "document:read"

    def test_list_memberships_for_resource_with_limit(
        self, mock_memberships_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_memberships_list_two, 200
        )

        syncify(
            self.authorization.list_memberships_for_resource(
                "authz_resource_01HXYZ",
                permission_slug="document:read",
                limit=25,
            )
        )

        assert request_kwargs["params"]["permission_slug"] == "document:read"
        assert request_kwargs["params"]["limit"] == 25
        assert request_kwargs["params"]["order"] == "desc"

    def test_list_memberships_for_resource_with_before(
        self, mock_memberships_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_memberships_list_two, 200
        )

        syncify(
            self.authorization.list_memberships_for_resource(
                "authz_resource_01HXYZ",
                permission_slug="document:read",
                before="cursor_before",
            )
        )

        assert request_kwargs["params"]["before"] == "cursor_before"
        assert request_kwargs["params"]["limit"] == 10
        assert request_kwargs["params"]["order"] == "desc"

    def test_list_memberships_for_resource_with_after(
        self, mock_memberships_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_memberships_list_two, 200
        )

        syncify(
            self.authorization.list_memberships_for_resource(
                "authz_resource_01HXYZ",
                permission_slug="document:read",
                after="cursor_after",
            )
        )

        assert request_kwargs["params"]["after"] == "cursor_after"
        assert request_kwargs["params"]["limit"] == 10
        assert request_kwargs["params"]["order"] == "desc"

    def test_list_memberships_for_resource_with_order_asc(
        self, mock_memberships_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_memberships_list_two, 200
        )

        syncify(
            self.authorization.list_memberships_for_resource(
                "authz_resource_01HXYZ",
                permission_slug="document:read",
                order="asc",
            )
        )

        assert request_kwargs["params"]["order"] == "asc"
        assert request_kwargs["params"]["limit"] == 10

    def test_list_memberships_for_resource_with_order_desc(
        self, mock_memberships_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_memberships_list_two, 200
        )

        syncify(
            self.authorization.list_memberships_for_resource(
                "authz_resource_01HXYZ",
                permission_slug="document:read",
                order="desc",
            )
        )

        assert request_kwargs["params"]["order"] == "desc"
        assert request_kwargs["params"]["limit"] == 10

    def test_list_memberships_for_resource_with_all_parameters(
        self, mock_memberships_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_memberships_list_two, 200
        )

        response = syncify(
            self.authorization.list_memberships_for_resource(
                "authz_resource_01HXYZ",
                permission_slug="document:read",
                assignment="direct",
                limit=5,
                before="cursor_before",
                after="cursor_after",
                order="asc",
            )
        )

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith(
            "/authorization/resources/authz_resource_01HXYZ/organization_memberships"
        )
        assert request_kwargs["params"]["permission_slug"] == "document:read"
        assert request_kwargs["params"]["assignment"] == "direct"
        assert request_kwargs["params"]["limit"] == 5
        assert request_kwargs["params"]["before"] == "cursor_before"
        assert request_kwargs["params"]["after"] == "cursor_after"
        assert request_kwargs["params"]["order"] == "asc"

        assert response.object == "list"
        assert len(response.data) == 2

    # --- list_memberships_for_resource_by_external_id ---

    def test_list_memberships_for_resource_by_external_id_returns_paginated_list(
        self, mock_memberships_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_memberships_list_two, 200
        )

        response = syncify(
            self.authorization.list_memberships_for_resource_by_external_id(
                organization_id="org_123",
                resource_type_slug="document",
                external_id="doc-ext-456",
                permission_slug="document:read",
            )
        )

        assert request_kwargs["method"] == "get"
        assert (
            "/authorization/organizations/org_123/resources/document/doc-ext-456/organization_memberships"
            in request_kwargs["url"]
        )
        assert request_kwargs["params"]["permission_slug"] == "document:read"
        assert request_kwargs["params"]["limit"] == 10
        assert request_kwargs["params"]["order"] == "desc"

        assert response.object == "list"
        assert len(response.data) == 2
        assert response.data[0].id == "om_01ABC"
        assert response.list_metadata.before is None
        assert response.list_metadata.after == "om_01DEF"

    def test_list_memberships_for_resource_by_external_id_with_assignment_direct(
        self, mock_memberships_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_memberships_list_two, 200
        )

        syncify(
            self.authorization.list_memberships_for_resource_by_external_id(
                organization_id="org_123",
                resource_type_slug="document",
                external_id="doc-ext-456",
                permission_slug="document:read",
                assignment="direct",
            )
        )

        assert request_kwargs["params"]["permission_slug"] == "document:read"
        assert request_kwargs["params"]["assignment"] == "direct"
        assert request_kwargs["params"]["limit"] == 10
        assert request_kwargs["params"]["order"] == "desc"

    def test_list_memberships_for_resource_by_external_id_with_assignment_indirect(
        self, mock_memberships_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_memberships_list_two, 200
        )

        syncify(
            self.authorization.list_memberships_for_resource_by_external_id(
                organization_id="org_123",
                resource_type_slug="folder",
                external_id="folder-ext-789",
                permission_slug="document:read",
                assignment="indirect",
            )
        )

        assert request_kwargs["params"]["assignment"] == "indirect"
        assert (
            "/authorization/organizations/org_123/resources/folder/folder-ext-789/organization_memberships"
            in request_kwargs["url"]
        )

    def test_list_memberships_for_resource_by_external_id_with_limit(
        self, mock_memberships_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_memberships_list_two, 200
        )

        syncify(
            self.authorization.list_memberships_for_resource_by_external_id(
                organization_id="org_123",
                resource_type_slug="document",
                external_id="doc-ext-456",
                permission_slug="document:read",
                limit=25,
            )
        )

        assert request_kwargs["params"]["permission_slug"] == "document:read"
        assert request_kwargs["params"]["limit"] == 25
        assert request_kwargs["params"]["order"] == "desc"

    def test_list_memberships_for_resource_by_external_id_with_before(
        self, mock_memberships_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_memberships_list_two, 200
        )

        syncify(
            self.authorization.list_memberships_for_resource_by_external_id(
                organization_id="org_123",
                resource_type_slug="document",
                external_id="doc-ext-456",
                permission_slug="document:read",
                before="cursor_before",
            )
        )

        assert request_kwargs["params"]["before"] == "cursor_before"
        assert request_kwargs["params"]["limit"] == 10
        assert request_kwargs["params"]["order"] == "desc"

    def test_list_memberships_for_resource_by_external_id_with_after(
        self, mock_memberships_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_memberships_list_two, 200
        )

        syncify(
            self.authorization.list_memberships_for_resource_by_external_id(
                organization_id="org_123",
                resource_type_slug="document",
                external_id="doc-ext-456",
                permission_slug="document:read",
                after="cursor_after",
            )
        )

        assert request_kwargs["params"]["after"] == "cursor_after"
        assert request_kwargs["params"]["limit"] == 10
        assert request_kwargs["params"]["order"] == "desc"

    def test_list_memberships_for_resource_by_external_id_with_order_asc(
        self, mock_memberships_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_memberships_list_two, 200
        )

        syncify(
            self.authorization.list_memberships_for_resource_by_external_id(
                organization_id="org_123",
                resource_type_slug="document",
                external_id="doc-ext-456",
                permission_slug="document:read",
                order="asc",
            )
        )

        assert request_kwargs["params"]["order"] == "asc"
        assert request_kwargs["params"]["limit"] == 10

    def test_list_memberships_for_resource_by_external_id_with_order_desc(
        self, mock_memberships_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_memberships_list_two, 200
        )

        syncify(
            self.authorization.list_memberships_for_resource_by_external_id(
                organization_id="org_123",
                resource_type_slug="document",
                external_id="doc-ext-456",
                permission_slug="document:read",
                order="desc",
            )
        )

        assert request_kwargs["params"]["order"] == "desc"
        assert request_kwargs["params"]["limit"] == 10

    def test_list_memberships_for_resource_by_external_id_with_all_parameters(
        self, mock_memberships_list_two, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_memberships_list_two, 200
        )

        response = syncify(
            self.authorization.list_memberships_for_resource_by_external_id(
                organization_id="org_123",
                resource_type_slug="document",
                external_id="doc-ext-456",
                permission_slug="document:read",
                assignment="direct",
                limit=5,
                before="cursor_before",
                after="cursor_after",
                order="asc",
            )
        )

        assert request_kwargs["method"] == "get"
        assert (
            "/authorization/organizations/org_123/resources/document/doc-ext-456/organization_memberships"
            in request_kwargs["url"]
        )
        assert request_kwargs["params"]["permission_slug"] == "document:read"
        assert request_kwargs["params"]["assignment"] == "direct"
        assert request_kwargs["params"]["limit"] == 5
        assert request_kwargs["params"]["before"] == "cursor_before"
        assert request_kwargs["params"]["after"] == "cursor_after"
        assert request_kwargs["params"]["order"] == "asc"

        assert response.object == "list"
        assert len(response.data) == 2
