import json

import pytest

from workos.passwordless import Passwordless


class TestPasswordless(object):
    @pytest.fixture(autouse=True)
    def setup(self, set_api_key_and_client_id):
        self.passwordless = Passwordless()

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
        self, mock_passwordless_session, mock_request_method
    ):
        mock_request_method("post", json.dumps(mock_passwordless_session), 201)

        session_options = {
            "email": "demo@workos-okta.com",
            "type": "MagicLink",
        }
        response = self.passwordless.create_session(session_options)

        assert response == mock_passwordless_session

    def test_get_send_session_succeeds(self, mock_request_method):
        response = {
            "success": True,
        }
        mock_request_method("post", json.dumps(response), 200)

        response = self.passwordless.send_session(
            "passwordless_session_01EHDAK2BFGWCSZXP9HGZ3VK8C"
        )
        assert response is True
