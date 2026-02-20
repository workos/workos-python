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

    # --- check: authorized result ---

    def test_check_authorized(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, {"authorized": True}, 200
        )

        result = syncify(
            self.authorization.check(
                "om_01ABC123",
                resource={"resource_id": "res_01ABC"},
                relation="viewer",
            )
        )

        assert result.authorized is True
        assert request_kwargs["method"] == "post"

    # --- check: unauthorized result ---

    def test_check_unauthorized(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, {"authorized": False}, 200
        )

        result = syncify(
            self.authorization.check(
                "om_01ABC123",
                resource={"resource_id": "res_01ABC"},
                relation="editor",
            )
        )

        assert result.authorized is False
        assert request_kwargs["method"] == "post"

    # --- check: resource by internal ID ---

    def test_check_resource_by_internal_id(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, {"authorized": True}, 200
        )

        syncify(
            self.authorization.check(
                "om_01ABC123",
                resource={"resource_id": "res_01ABC"},
                relation="viewer",
            )
        )

        assert request_kwargs["json"] == {
            "resource": {"resource_id": "res_01ABC"},
            "relation": "viewer",
        }

    # --- check: resource by external ID ---

    def test_check_resource_by_external_id(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, {"authorized": True}, 200
        )

        syncify(
            self.authorization.check(
                "om_01ABC123",
                resource={"resource_type": "document", "external_id": "my-doc-456"},
                relation="editor",
            )
        )

        assert request_kwargs["json"] == {
            "resource": {"resource_type": "document", "external_id": "my-doc-456"},
            "relation": "editor",
        }

    # --- check: URL construction ---

    def test_check_url_contains_org_membership_id(
        self, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, {"authorized": True}, 200
        )

        syncify(
            self.authorization.check(
                "om_01MEMBERSHIP",
                resource={"resource_id": "res_01ABC"},
                relation="viewer",
            )
        )

        assert request_kwargs["url"].endswith(
            "/authorization/organization_memberships/om_01MEMBERSHIP/check"
        )
