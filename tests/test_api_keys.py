import pytest

from tests.utils.fixtures.mock_api_key import MockApiKey
from tests.utils.syncify import syncify
from workos.api_key import ApiKey, AsyncApiKey
from workos.exceptions import AuthenticationException


@pytest.mark.sync_and_async(ApiKey, AsyncApiKey)
class TestApiKey:
    @pytest.fixture
    def mock_api_key_details(self):
        api_key_details = MockApiKey()
        return api_key_details.model_dump()

    def test_validate_api_key_with_valid_key(
        self,
        module_instance,
        mock_api_key_details,
        capture_and_mock_http_client_request,
    ):
        request_kwargs = capture_and_mock_http_client_request(
            module_instance._http_client, mock_api_key_details, 200
        )

        api_key_details = syncify(module_instance.validate_api_key())

        assert request_kwargs["url"].endswith("/api_keys/validate")
        assert request_kwargs["method"] == "post"
        assert api_key_details.id == mock_api_key_details["id"]
        assert api_key_details.name == mock_api_key_details["name"]
        assert api_key_details.object == "api_key"

    def test_validate_api_key_with_invalid_key(
        self,
        module_instance,
        mock_http_client_with_response,
    ):
        mock_http_client_with_response(
            module_instance._http_client,
            {"message": "Invalid API key", "error": "invalid_api_key"},
            401,
        )

        with pytest.raises(AuthenticationException):
            syncify(module_instance.validate_api_key())
