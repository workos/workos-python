from typing import Union

import pytest
from tests.utils.syncify import syncify
from workos.authorization import AsyncAuthorization, Authorization
from workos.types.authorization.resource_identifier import (
    ResourceIdentifierByExternalId,
    ResourceIdentifierById,
)

MOCK_ORG_MEMBERSHIP_ID = "org_membership_01ABC"
MOCK_PERMISSION_SLUG = "document:read"
MOCK_RESOURCE_ID = "res_01ABC"
MOCK_RESOURCE_TYPE = "document"
MOCK_EXTERNAL_ID = "ext_123"


@pytest.mark.sync_and_async(Authorization, AsyncAuthorization)
class TestAuthorizationCheck:
    @pytest.fixture(autouse=True)
    def setup(self, module_instance: Union[Authorization, AsyncAuthorization]):
        self.http_client = module_instance._http_client
        self.authorization = module_instance

    def test_check_authorized_by_resource_id(
        self, capture_and_mock_http_client_request
    ):
        mock_response = {"authorized": True}
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_response, 200
        )

        resource: ResourceIdentifierById = {"resource_id": MOCK_RESOURCE_ID}
        response = syncify(
            self.authorization.check(
                MOCK_ORG_MEMBERSHIP_ID,
                permission_slug=MOCK_PERMISSION_SLUG,
                resource=resource,
            )
        )

        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith(
            f"/authorization/organization_memberships/{MOCK_ORG_MEMBERSHIP_ID}/check"
        )
        assert request_kwargs["json"] == {
            "permission_slug": MOCK_PERMISSION_SLUG,
            "resource_id": MOCK_RESOURCE_ID,
        }

        assert response.authorized is True

    def test_check_authorized_by_external_id(
        self, capture_and_mock_http_client_request
    ):
        mock_response = {"authorized": True}
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_response, 200
        )

        resource: ResourceIdentifierByExternalId = {
            "resource_external_id": MOCK_EXTERNAL_ID,
            "resource_type_slug": MOCK_RESOURCE_TYPE,
        }
        response = syncify(
            self.authorization.check(
                MOCK_ORG_MEMBERSHIP_ID,
                permission_slug=MOCK_PERMISSION_SLUG,
                resource=resource,
            )
        )

        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith(
            f"/authorization/organization_memberships/{MOCK_ORG_MEMBERSHIP_ID}/check"
        )
        assert request_kwargs["json"] == {
            "permission_slug": MOCK_PERMISSION_SLUG,
            "resource_external_id": MOCK_EXTERNAL_ID,
            "resource_type_slug": MOCK_RESOURCE_TYPE,
        }

        assert response.authorized is True

    def test_check_not_authorized_by_resource_id(
        self, capture_and_mock_http_client_request
    ):
        mock_response = {"authorized": False}
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_response, 200
        )

        resource: ResourceIdentifierById = {"resource_id": MOCK_RESOURCE_ID}
        response = syncify(
            self.authorization.check(
                MOCK_ORG_MEMBERSHIP_ID,
                permission_slug=MOCK_PERMISSION_SLUG,
                resource=resource,
            )
        )

        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith(
            f"/authorization/organization_memberships/{MOCK_ORG_MEMBERSHIP_ID}/check"
        )
        assert request_kwargs["json"] == {
            "permission_slug": MOCK_PERMISSION_SLUG,
            "resource_id": MOCK_RESOURCE_ID,
        }

        assert response.authorized is False

    def test_check_not_authorized_by_external_id(
        self, capture_and_mock_http_client_request
    ):
        mock_response = {"authorized": False}
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_response, 200
        )

        resource: ResourceIdentifierByExternalId = {
            "resource_external_id": MOCK_EXTERNAL_ID,
            "resource_type_slug": MOCK_RESOURCE_TYPE,
        }
        response = syncify(
            self.authorization.check(
                MOCK_ORG_MEMBERSHIP_ID,
                permission_slug=MOCK_PERMISSION_SLUG,
                resource=resource,
            )
        )

        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith(
            f"/authorization/organization_memberships/{MOCK_ORG_MEMBERSHIP_ID}/check"
        )
        assert request_kwargs["json"] == {
            "permission_slug": MOCK_PERMISSION_SLUG,
            "resource_external_id": MOCK_EXTERNAL_ID,
            "resource_type_slug": MOCK_RESOURCE_TYPE,
        }
        assert response.authorized is False
