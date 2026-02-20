from typing import Union

import pytest
from tests.types.test_auto_pagination_function import TestAutoPaginationFunction
from tests.utils.list_resource import list_response_of
from tests.utils.syncify import syncify
from workos.authorization import AsyncAuthorization, Authorization


MOCK_ROLE_ASSIGNMENT = {
    "object": "role_assignment",
    "id": "ra_01ABC",
    "role": {"slug": "admin"},
    "resource": {
        "id": "res_01ABC",
        "external_id": "ext_123",
        "resource_type_slug": "document",
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
}

MOCK_OM_ID = "om_01MEMBERSHIP"


def _mock_role_assignment(id: str) -> dict:
    return {
        "object": "role_assignment",
        "id": id,
        "role": {"slug": "admin"},
        "resource": {
            "id": "res_01ABC",
            "external_id": "ext_123",
            "resource_type_slug": "document",
        },
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.mark.sync_and_async(Authorization, AsyncAuthorization)
class TestAuthorizationRoleAssignments:
    @pytest.fixture(autouse=True)
    def setup(self, module_instance: Union[Authorization, AsyncAuthorization]):
        self.http_client = module_instance._http_client
        self.authorization = module_instance

    # --- list_role_assignments ---

    def test_list_role_assignments(self, capture_and_mock_http_client_request):
        mock_list = list_response_of(
            data=[MOCK_ROLE_ASSIGNMENT],
            before=None,
            after=None,
        )
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_list, 200
        )

        result = syncify(self.authorization.list_role_assignments(MOCK_OM_ID))

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith(
            f"/authorization/organization_memberships/{MOCK_OM_ID}/role_assignments"
        )
        assert len(result.data) == 1
        assert result.data[0].id == "ra_01ABC"
        assert result.data[0].role.slug == "admin"

    def test_list_role_assignments_empty(self, capture_and_mock_http_client_request):
        mock_list = list_response_of(data=[], before=None, after=None)
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_list, 200
        )

        result = syncify(self.authorization.list_role_assignments(MOCK_OM_ID))

        assert request_kwargs["method"] == "get"
        assert len(result.data) == 0

    def test_list_role_assignments_with_pagination_params(
        self, capture_and_mock_http_client_request
    ):
        mock_list = list_response_of(data=[], before=None, after=None)
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_list, 200
        )

        syncify(
            self.authorization.list_role_assignments(
                MOCK_OM_ID,
                limit=5,
                before="before_cursor",
                after="after_cursor",
                order="asc",
            )
        )

        assert request_kwargs["method"] == "get"
        assert request_kwargs["params"]["limit"] == 5
        assert request_kwargs["params"]["before"] == "before_cursor"
        assert request_kwargs["params"]["after"] == "after_cursor"
        assert request_kwargs["params"]["order"] == "asc"

    @pytest.fixture
    def mock_role_assignments_multiple_data_pages(self):
        data = [_mock_role_assignment(f"ra_{i:03d}") for i in range(40)]
        return list_response_of(data=data)

    def test_list_role_assignments_auto_pagination(
        self,
        mock_role_assignments_multiple_data_pages,
        test_auto_pagination: TestAutoPaginationFunction,
    ):
        test_auto_pagination(
            http_client=self.http_client,
            list_function=self.authorization.list_role_assignments,
            expected_all_page_data=mock_role_assignments_multiple_data_pages["data"],
            list_function_params={
                "organization_membership_id": MOCK_OM_ID,
            },
        )

    # --- assign_role ---

    def test_assign_role(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, MOCK_ROLE_ASSIGNMENT, 201
        )

        result = syncify(self.authorization.assign_role(MOCK_OM_ID, role_slug="admin"))

        assert result.id == "ra_01ABC"
        assert result.object == "role_assignment"
        assert result.role.slug == "admin"
        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith(
            f"/authorization/organization_memberships/{MOCK_OM_ID}/role_assignments"
        )
        assert request_kwargs["json"] == {"role_slug": "admin"}

    # --- remove_role ---

    def test_remove_role(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client,
            status_code=204,
            headers={"content-type": "text/plain; charset=utf-8"},
        )

        result = syncify(self.authorization.remove_role(MOCK_OM_ID, role_slug="admin"))

        assert result is None
        assert request_kwargs["method"] == "delete"
        assert request_kwargs["url"].endswith(
            f"/authorization/organization_memberships/{MOCK_OM_ID}/role_assignments"
        )
        assert request_kwargs["json"] == {"role_slug": "admin"}

    # --- remove_role_assignment ---

    def test_remove_role_assignment(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client,
            status_code=204,
            headers={"content-type": "text/plain; charset=utf-8"},
        )

        result = syncify(
            self.authorization.remove_role_assignment(MOCK_OM_ID, "ra_01ABC")
        )

        assert result is None
        assert request_kwargs["method"] == "delete"
        assert request_kwargs["url"].endswith(
            f"/authorization/organization_memberships/{MOCK_OM_ID}/role_assignments/ra_01ABC"
        )
