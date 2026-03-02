from typing import Union

import pytest
from tests.utils.fixtures.mock_role_assignment import MockRoleAssignment
from tests.utils.syncify import syncify
from workos.authorization import AsyncAuthorization, Authorization


@pytest.mark.sync_and_async(Authorization, AsyncAuthorization)
class TestAuthorizationRoleAssignments:
    @pytest.fixture(autouse=True)
    def setup(self, module_instance: Union[Authorization, AsyncAuthorization]):
        self.http_client = module_instance._http_client
        self.authorization = module_instance

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