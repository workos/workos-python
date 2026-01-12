import pytest

from tests.utils.syncify import syncify
from workos.pipes import AsyncPipes, Pipes


@pytest.mark.sync_and_async(Pipes, AsyncPipes)
class TestPipes:
    @pytest.fixture
    def mock_access_token(self):
        return {
            "object": "access_token",
            "access_token": "test_access_token_123",
            "expires_at": "2026-01-09T12:00:00.000Z",
            "scopes": ["read:users", "write:users"],
            "missing_scopes": [],
        }

    def test_get_access_token_success_with_expiry(
        self,
        module_instance,
        mock_access_token,
        capture_and_mock_http_client_request,
    ):
        response_body = {
            "active": True,
            "access_token": mock_access_token,
        }
        request_kwargs = capture_and_mock_http_client_request(
            module_instance._http_client, response_body, 200
        )

        result = syncify(
            module_instance.get_access_token(
                provider="test-provider",
                user_id="user_123",
            )
        )

        assert request_kwargs["url"].endswith("data-integrations/test-provider/token")
        assert request_kwargs["method"] == "post"
        assert request_kwargs["json"]["user_id"] == "user_123"
        assert result.active is True
        assert result.access_token.access_token == mock_access_token["access_token"]
        assert result.access_token.scopes == mock_access_token["scopes"]

    def test_get_access_token_success_without_expiry(
        self,
        module_instance,
        capture_and_mock_http_client_request,
    ):
        response_body = {
            "active": True,
            "access_token": {
                "object": "access_token",
                "access_token": "test_token",
                "expires_at": None,
                "scopes": ["read"],
                "missing_scopes": [],
            },
        }
        capture_and_mock_http_client_request(
            module_instance._http_client, response_body, 200
        )

        result = syncify(
            module_instance.get_access_token(
                provider="test-provider",
                user_id="user_123",
            )
        )

        assert result.active is True
        assert result.access_token.expires_at is None

    def test_get_access_token_with_organization_id(
        self,
        module_instance,
        mock_access_token,
        capture_and_mock_http_client_request,
    ):
        response_body = {
            "active": True,
            "access_token": mock_access_token,
        }
        request_kwargs = capture_and_mock_http_client_request(
            module_instance._http_client, response_body, 200
        )

        syncify(
            module_instance.get_access_token(
                provider="test-provider",
                user_id="user_123",
                organization_id="org_456",
            )
        )

        assert request_kwargs["json"]["organization_id"] == "org_456"

    def test_get_access_token_without_organization_id(
        self,
        module_instance,
        mock_access_token,
        capture_and_mock_http_client_request,
    ):
        response_body = {
            "active": True,
            "access_token": mock_access_token,
        }
        request_kwargs = capture_and_mock_http_client_request(
            module_instance._http_client, response_body, 200
        )

        syncify(
            module_instance.get_access_token(
                provider="test-provider",
                user_id="user_123",
            )
        )

        assert "organization_id" not in request_kwargs["json"]

    def test_get_access_token_not_installed(
        self,
        module_instance,
        capture_and_mock_http_client_request,
    ):
        response_body = {
            "active": False,
            "error": "not_installed",
        }
        capture_and_mock_http_client_request(
            module_instance._http_client, response_body, 200
        )

        result = syncify(
            module_instance.get_access_token(
                provider="test-provider",
                user_id="user_123",
            )
        )

        assert result.active is False
        assert result.error == "not_installed"

    def test_get_access_token_needs_reauthorization(
        self,
        module_instance,
        capture_and_mock_http_client_request,
    ):
        response_body = {
            "active": False,
            "error": "needs_reauthorization",
        }
        capture_and_mock_http_client_request(
            module_instance._http_client, response_body, 200
        )

        result = syncify(
            module_instance.get_access_token(
                provider="test-provider",
                user_id="user_123",
            )
        )

        assert result.active is False
        assert result.error == "needs_reauthorization"
