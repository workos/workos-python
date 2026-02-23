from typing import Union

import pytest
from tests.utils.syncify import syncify
from workos.authorization import AsyncAuthorization, Authorization
from workos.types.authorization.resource_identifier import (
    ResourceIdentifierByExternalId,
    ResourceIdentifierById,
)


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
                resource=ResourceIdentifierById(resource_id="res_01ABC"),
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
                resource=ResourceIdentifierById(resource_id="res_01ABC"),
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
                resource=ResourceIdentifierById(resource_id="res_01XYZ"),
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
                resource=ResourceIdentifierByExternalId(
                    resource_external_id="ext_doc_123",
                    resource_type_slug="document",
                ),
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
                resource=ResourceIdentifierById(resource_id="res_01ABC"),
            )
        )

        assert request_kwargs["url"].endswith(
            "/authorization/organization_memberships/om_01MEMBERSHIP/check"
        )
