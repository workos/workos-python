from typing import Union

import pytest
from tests.utils.fixtures.mock_role_assignment import (
    MockRoleAssignment,
    MockRoleAssignmentsList,
)
from tests.utils.list_resource import list_response_of
from tests.utils.syncify import syncify
from workos.authorization import AsyncAuthorization, Authorization


@pytest.mark.sync_and_async(Authorization, AsyncAuthorization)
class TestAuthorizationRoleAssignments:
    @pytest.fixture(autouse=True)
    def setup(self, module_instance: Union[Authorization, AsyncAuthorization]):
        self.http_client = module_instance._http_client
        self.authorization = module_instance

    @pytest.fixture
    def mock_role_assignments_list(self):
        return MockRoleAssignmentsList().dict()

    @pytest.fixture
    def mock_role_assignments_empty_list(self):
        return list_response_of(data=[])

    def test_assign_role_by_resource_id(self, capture_and_mock_http_client_request):
        mock_role_assignment = MockRoleAssignment().dict()
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_role_assignment, 201
        )

        response = syncify(
            self.authorization.assign_role(
                "om_01ABC",
                role_slug="admin",
                resource_identifier={"resource_id": "res_01XYZ"},
            )
        )

        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith(
            "/authorization/organization_memberships/om_01ABC/role_assignments"
        )
        assert request_kwargs["json"] == {
            "role_slug": "admin",
            "resource_id": "res_01XYZ",
        }
        assert "resource_external_id" not in request_kwargs["json"]
        assert "resource_type_slug" not in request_kwargs["json"]

        assert response.dict() == mock_role_assignment

    def test_assign_role_by_external_id_and_resource_type_slug(
        self, capture_and_mock_http_client_request
    ):
        mock_role_assignment = MockRoleAssignment().dict()
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_role_assignment, 201
        )

        response = syncify(
            self.authorization.assign_role(
                "om_01ABC",
                role_slug="editor",
                resource_identifier={
                    "resource_external_id": "ext_doc_456",
                    "resource_type_slug": "document",
                },
            )
        )

        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith(
            "/authorization/organization_memberships/om_01ABC/role_assignments"
        )
        assert request_kwargs["json"] == {
            "role_slug": "editor",
            "resource_external_id": "ext_doc_456",
            "resource_type_slug": "document",
        }
        assert "resource_id" not in request_kwargs["json"]

        assert response.dict() == mock_role_assignment

    def test_remove_role_by_resource_id(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, status_code=204
        )

        syncify(
            self.authorization.remove_role(
                "om_01ABC",
                role_slug="admin",
                resource_identifier={"resource_id": "res_01XYZ"},
            )
        )

        assert request_kwargs["method"] == "delete"
        assert request_kwargs["url"].endswith(
            "/authorization/organization_memberships/om_01ABC/role_assignments"
        )
        assert request_kwargs["json"] == {
            "role_slug": "admin",
            "resource_id": "res_01XYZ",
        }
        assert "resource_external_id" not in request_kwargs["json"]
        assert "resource_type_slug" not in request_kwargs["json"]

    def test_remove_role_by_external_id_and_resource_type_slug(
        self, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, status_code=204
        )

        syncify(
            self.authorization.remove_role(
                "om_01ABC",
                role_slug="editor",
                resource_identifier={
                    "resource_external_id": "ext_doc_456",
                    "resource_type_slug": "document",
                },
            )
        )

        assert request_kwargs["method"] == "delete"
        assert request_kwargs["url"].endswith(
            "/authorization/organization_memberships/om_01ABC/role_assignments"
        )
        assert request_kwargs["json"] == {
            "role_slug": "editor",
            "resource_external_id": "ext_doc_456",
            "resource_type_slug": "document",
        }
        assert "resource_id" not in request_kwargs["json"]

    def test_remove_role_assignment(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, status_code=204
        )

        syncify(
            self.authorization.remove_role_assignment(
                "om_01ABC",
                role_assignment_id="ra_01XYZ",
            )
        )

        assert request_kwargs["method"] == "delete"
        assert request_kwargs["url"].endswith(
            "/authorization/organization_memberships/om_01ABC/role_assignments/ra_01XYZ"
        )

    def test_list_role_assignments_returns_paginated_list(
        self,
        mock_role_assignments_list,
        capture_and_mock_http_client_request,
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_role_assignments_list, 200
        )

        response = syncify(
            self.authorization.list_role_assignments(
                organization_membership_id="om_01ABC"
            )
        )

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith(
            "/authorization/organization_memberships/om_01ABC/role_assignments"
        )
        assert request_kwargs["params"] == {"limit": 10, "order": "desc"}

        assert response.object == "list"
        assert len(response.data) == 2

        assert response.data[0].object == "role_assignment"
        assert response.data[0].id == "ra_01ABC"
        assert response.data[0].role.slug == "admin"
        assert response.data[0].resource.id == "res_01ABC"
        assert response.data[0].resource.external_id == "ext_123"
        assert response.data[0].resource.resource_type_slug == "document"
        assert response.data[0].created_at == "2024-01-15T09:30:00.000Z"
        assert response.data[0].updated_at == "2024-01-15T09:30:00.000Z"

        assert response.data[1].object == "role_assignment"
        assert response.data[1].id == "ra_01DEF"
        assert response.data[1].role.slug == "editor"
        assert response.data[1].resource.id == "res_01XYZ"
        assert response.data[1].resource.external_id == "ext_456"
        assert response.data[1].resource.resource_type_slug == "folder"
        assert response.data[1].created_at == "2024-01-14T08:00:00.000Z"
        assert response.data[1].updated_at == "2024-01-14T08:00:00.000Z"

        assert response.list_metadata.before is None
        assert response.list_metadata.after == "ra_01DEF"

    def test_list_role_assignments_returns_empty_list(
        self,
        mock_role_assignments_empty_list,
        capture_and_mock_http_client_request,
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_role_assignments_empty_list, 200
        )

        response = syncify(
            self.authorization.list_role_assignments(
                organization_membership_id="om_01ABC"
            )
        )

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith(
            "/authorization/organization_memberships/om_01ABC/role_assignments"
        )
        assert request_kwargs["params"] == {"limit": 10, "order": "desc"}

        assert len(response.data) == 0
        assert response.list_metadata.before is None
        assert response.list_metadata.after is None

    def test_list_role_assignments_with_limit(
        self,
        mock_role_assignments_list,
        capture_and_mock_http_client_request,
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_role_assignments_list, 200
        )

        syncify(
            self.authorization.list_role_assignments(
                organization_membership_id="om_01ABC",
                limit=25,
            )
        )

        assert request_kwargs["params"]["limit"] == 25
        assert request_kwargs["params"]["order"] == "desc"
        assert "before" not in request_kwargs["params"]
        assert "after" not in request_kwargs["params"]

    def test_list_role_assignments_with_before(
        self,
        mock_role_assignments_list,
        capture_and_mock_http_client_request,
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_role_assignments_list, 200
        )

        syncify(
            self.authorization.list_role_assignments(
                organization_membership_id="om_01ABC",
                before="cursor_before",
            )
        )

        assert request_kwargs["params"]["before"] == "cursor_before"
        assert request_kwargs["params"]["limit"] == 10
        assert request_kwargs["params"]["order"] == "desc"
        assert "after" not in request_kwargs["params"]

    def test_list_role_assignments_with_after(
        self,
        mock_role_assignments_list,
        capture_and_mock_http_client_request,
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_role_assignments_list, 200
        )

        syncify(
            self.authorization.list_role_assignments(
                organization_membership_id="om_01ABC",
                after="cursor_after",
            )
        )

        assert request_kwargs["params"]["after"] == "cursor_after"
        assert request_kwargs["params"]["limit"] == 10
        assert request_kwargs["params"]["order"] == "desc"
        assert "before" not in request_kwargs["params"]

    def test_list_role_assignments_with_order_desc(
        self,
        mock_role_assignments_list,
        capture_and_mock_http_client_request,
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_role_assignments_list, 200
        )

        syncify(
            self.authorization.list_role_assignments(
                organization_membership_id="om_01ABC",
                order="desc",
            )
        )

        assert request_kwargs["params"]["order"] == "desc"
        assert request_kwargs["params"]["limit"] == 10
        assert "before" not in request_kwargs["params"]
        assert "after" not in request_kwargs["params"]

    def test_list_role_assignments_with_order_asc(
        self,
        mock_role_assignments_list,
        capture_and_mock_http_client_request,
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_role_assignments_list, 200
        )

        syncify(
            self.authorization.list_role_assignments(
                organization_membership_id="om_01ABC",
                order="asc",
            )
        )

        assert request_kwargs["params"]["order"] == "asc"
        assert request_kwargs["params"]["limit"] == 10
        assert "before" not in request_kwargs["params"]
        assert "after" not in request_kwargs["params"]

    def test_list_role_assignments_with_all_parameters(
        self,
        mock_role_assignments_list,
        capture_and_mock_http_client_request,
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_role_assignments_list, 200
        )

        syncify(
            self.authorization.list_role_assignments(
                organization_membership_id="om_01ABC",
                limit=5,
                before="cursor_before",
                after="cursor_after",
                order="asc",
            )
        )

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith(
            "/authorization/organization_memberships/om_01ABC/role_assignments"
        )
        assert request_kwargs["params"]["limit"] == 5
        assert request_kwargs["params"]["before"] == "cursor_before"
        assert request_kwargs["params"]["after"] == "cursor_after"
        assert request_kwargs["params"]["order"] == "asc"
