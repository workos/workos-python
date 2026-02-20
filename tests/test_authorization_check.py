from typing import Union

import pytest
from tests.utils.syncify import syncify
from workos.authorization import AsyncAuthorization, Authorization


@pytest.mark.sync_and_async(Authorization, AsyncAuthorization)
class TestAuthorizationCheck:
    @pytest.fixture(autouse=True)
    def setup(self, module_instance: Union[Authorization, AsyncAuthorization]):
        self.http_client = module_instance._http_client
        self.authorization = module_instance

    @pytest.fixture
    def mock_check_authorized(self):
        return {"authorized": True}

    @pytest.fixture
    def mock_check_unauthorized(self):
        return {"authorized": False}

    def test_check_authorized(
        self, mock_check_authorized, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_check_authorized, 200
        )

        result = syncify(
            self.authorization.check(
                "om_01ABC",
                permission_slug="documents:read",
                resource_id="res_01ABC",
            )
        )

        assert result.authorized is True
        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith(
            "/authorization/organization_memberships/om_01ABC/check"
        )

    def test_check_unauthorized(
        self, mock_check_unauthorized, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_check_unauthorized, 200
        )

        result = syncify(
            self.authorization.check(
                "om_01ABC",
                permission_slug="documents:write",
                resource_id="res_01ABC",
            )
        )

        assert result.authorized is False
        assert request_kwargs["method"] == "post"

    def test_check_with_resource_id(
        self, mock_check_authorized, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_check_authorized, 200
        )

        syncify(
            self.authorization.check(
                "om_01ABC",
                permission_slug="documents:read",
                resource_id="res_01XYZ",
            )
        )

        assert request_kwargs["json"] == {
            "permission_slug": "documents:read",
            "resource_id": "res_01XYZ",
        }

    def test_check_with_resource_external_id(
        self, mock_check_authorized, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_check_authorized, 200
        )

        syncify(
            self.authorization.check(
                "om_01ABC",
                permission_slug="documents:read",
                resource_external_id="ext_doc_123",
                resource_type_slug="document",
            )
        )

        assert request_kwargs["json"] == {
            "permission_slug": "documents:read",
            "resource_external_id": "ext_doc_123",
            "resource_type_slug": "document",
        }

    def test_check_url_construction(
        self, mock_check_authorized, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_check_authorized, 200
        )

        syncify(
            self.authorization.check(
                "om_01MEMBERSHIP",
                permission_slug="admin:access",
            )
        )

        assert request_kwargs["url"].endswith(
            "/authorization/organization_memberships/om_01MEMBERSHIP/check"
        )
        assert request_kwargs["json"] == {"permission_slug": "admin:access"}

    def test_check_raises_when_both_resource_identifiers_provided(self):
        with pytest.raises(ValueError, match="mutually exclusive"):
            syncify(
                self.authorization.check(
                    "om_01ABC",
                    permission_slug="documents:read",
                    resource_id="res_01ABC",
                    resource_external_id="ext_doc_123",
                    resource_type_slug="document",
                )
            )

    def test_check_raises_when_external_id_without_type_slug(self):
        with pytest.raises(ValueError, match="resource_type_slug is required"):
            syncify(
                self.authorization.check(
                    "om_01ABC",
                    permission_slug="documents:read",
                    resource_external_id="ext_doc_123",
                )
            )
