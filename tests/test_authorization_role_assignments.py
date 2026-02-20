from typing import Union

import pytest
from tests.utils.fixtures.mock_role_assignment import MockRoleAssignment
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
    def mock_role_assignment(self):
        return MockRoleAssignment(id="ra_01ABC").dict()

    @pytest.fixture
    def mock_role_assignments(self):
        assignment_list = [
            MockRoleAssignment(id=f"ra_{i}", role_slug=f"role-{i}").dict()
            for i in range(5)
        ]
        return {
            "data": assignment_list,
            "list_metadata": {"before": None, "after": None},
            "object": "list",
        }

    @pytest.fixture
    def mock_role_assignments_multiple_data_pages(self):
        assignment_list = [
            MockRoleAssignment(id=f"ra_{i}", role_slug=f"role-{i}").dict()
            for i in range(40)
        ]
        return list_response_of(data=assignment_list)

    # --- list_role_assignments ---

    def test_list_role_assignments(
        self, mock_role_assignments, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_role_assignments, 200
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
        assert "organization_membership_id" not in request_kwargs["params"]
        assert len(response.data) == 5

    def test_list_role_assignments_with_params(
        self, mock_role_assignments, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_role_assignments, 200
        )

        syncify(
            self.authorization.list_role_assignments(
                organization_membership_id="om_01ABC",
                limit=5,
                after="ra_cursor",
                order="asc",
            )
        )

        assert request_kwargs["params"]["limit"] == 5
        assert request_kwargs["params"]["after"] == "ra_cursor"
        assert request_kwargs["params"]["order"] == "asc"

    def test_list_role_assignments_auto_pagination(
        self,
        mock_role_assignments_multiple_data_pages,
        test_auto_pagination,
    ):
        test_auto_pagination(
            http_client=self.http_client,
            list_function=self.authorization.list_role_assignments,
            expected_all_page_data=mock_role_assignments_multiple_data_pages["data"],
            list_function_params={
                "organization_membership_id": "om_01ABC",
            },
        )

    # --- assign_role ---

    def test_assign_role(
        self, mock_role_assignment, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_role_assignment, 201
        )

        role_assignment = syncify(
            self.authorization.assign_role("om_01ABC", role_slug="admin")
        )

        assert role_assignment.id == "ra_01ABC"
        assert role_assignment.role.slug == "admin"
        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith(
            "/authorization/organization_memberships/om_01ABC/role_assignments"
        )
        assert request_kwargs["json"] == {"role_slug": "admin"}

    # --- remove_role ---

    def test_remove_role(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client,
            status_code=202,
            headers={"content-type": "text/plain; charset=utf-8"},
        )

        response = syncify(
            self.authorization.remove_role("om_01ABC", role_slug="admin")
        )

        assert response is None
        assert request_kwargs["method"] == "delete"
        assert request_kwargs["url"].endswith(
            "/authorization/organization_memberships/om_01ABC/role_assignments"
        )
        assert request_kwargs["json"] == {"role_slug": "admin"}

    # --- remove_role_assignment ---

    def test_remove_role_assignment(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client,
            status_code=202,
            headers={"content-type": "text/plain; charset=utf-8"},
        )

        response = syncify(
            self.authorization.remove_role_assignment("om_01ABC", "ra_01ABC")
        )

        assert response is None
        assert request_kwargs["method"] == "delete"
        assert request_kwargs["url"].endswith(
            "/authorization/organization_memberships/om_01ABC/role_assignments/ra_01ABC"
        )
