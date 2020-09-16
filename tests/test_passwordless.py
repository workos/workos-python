import json
from requests import Response

import pytest

import workos
from workos.passwordless import Passwordless


class TestPasswordless(object):
    @pytest.fixture(autouse=True)
    def setup(self, set_api_key_and_project_id):
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
        mock_response = Response()
        mock_response.status_code = 201
        mock_response.response_dict = mock_passwordless_session
        mock_request_method("post", mock_response, 201)

        session_options = {
            "email": "demo@workos-okta.com",
            "type": "MagicLink",
        }
        response = self.passwordless.create_session(session_options)

        assert response.status_code == 201
        assert response.response_dict == mock_passwordless_session

    def test_get_send_session_succeeds(self, mock_request_method):
        response = {
            "success": True,
        }
        mock_request_method("post", response, 200)

        response = self.passwordless.send_session(
            "passwordless_session_01EHDAK2BFGWCSZXP9HGZ3VK8C"
        )
        assert response == True
