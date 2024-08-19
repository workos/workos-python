import pytest
from workos.passwordless import Passwordless


class TestPasswordless:
    @pytest.fixture(autouse=True)
    def setup(self, sync_http_client_for_test):
        self.http_client = sync_http_client_for_test
        self.passwordless = Passwordless(http_client=self.http_client)

    @pytest.fixture
    def mock_passwordless_session(self):
        return {
            "id": "passwordless_session_01EHDAK2BFGWCSZXP9HGZ3VK8C",
            "email": "demo@workos-okta.com",
            "expires_at": "2020-08-13T05:50:00.000Z",
            "link": "https://auth.workos.com/passwordless/4TeRexuejWCKs9rrFOIuLRYEr/confirm",
            "object": "passwordless_session",
        }

    def test_create_session_succeeds(
        self, mock_passwordless_session, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_passwordless_session, 201
        )

        session_options = {
            "email": "demo@workos-okta.com",
            "type": "MagicLink",
            "expires_in": 300,
        }
        passwordless_session = self.passwordless.create_session(**session_options)

        assert request_kwargs["url"].endswith("/passwordless/sessions")
        assert request_kwargs["method"] == "post"
        assert request_kwargs["json"] == session_options
        assert passwordless_session.dict() == mock_passwordless_session

    def test_get_send_session_succeeds(self, capture_and_mock_http_client_request):
        response = {
            "success": True,
        }
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, response, 200
        )

        response = self.passwordless.send_session(
            "passwordless_session_01EHDAK2BFGWCSZXP9HGZ3VK8C"
        )

        assert request_kwargs["url"].endswith(
            "/passwordless/sessions/passwordless_session_01EHDAK2BFGWCSZXP9HGZ3VK8C/send"
        )
        assert request_kwargs["method"] == "post"
        assert response == True
