# type: ignore
import pytest

from tests.utils.fixtures.mock_api_key import MockApiKey
from tests.utils.syncify import syncify
from workos.api_keys import API_KEY_VALIDATION_PATH, ApiKeys, AsyncApiKeys


@pytest.mark.sync_and_async(ApiKeys, AsyncApiKeys)
class TestApiKeys:
    @pytest.fixture
    def mock_api_key(self):
        return MockApiKey().dict()

    @pytest.fixture
    def api_key(self):
        return "sk_my_api_key"

    def test_validate_api_key_with_valid_key(
        self,
        module_instance,
        api_key,
        mock_api_key,
        capture_and_mock_http_client_request,
    ):
        response_body = {"api_key": mock_api_key}
        request_kwargs = capture_and_mock_http_client_request(
            module_instance._http_client, response_body, 200
        )

        api_key_details = syncify(module_instance.validate_api_key(value=api_key))

        assert request_kwargs["url"].endswith(API_KEY_VALIDATION_PATH)
        assert request_kwargs["method"] == "post"
        assert api_key_details.id == mock_api_key["id"]
        assert api_key_details.name == mock_api_key["name"]
        assert api_key_details.object == "api_key"

    def test_validate_api_key_with_invalid_key(
        self,
        module_instance,
        mock_http_client_with_response,
    ):
        mock_http_client_with_response(
            module_instance._http_client,
            {"api_key": None},
            200,
        )

        assert syncify(module_instance.validate_api_key(value="invalid-key")) is None
