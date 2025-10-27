from typing import Union

import pytest

from tests.utils.syncify import syncify
from workos.user_management import AsyncUserManagement, UserManagement


@pytest.mark.sync_and_async(UserManagement, AsyncUserManagement)
class TestUserManagementRevokeSession:
    @pytest.fixture(autouse=True)
    def setup(self, module_instance: Union[UserManagement, AsyncUserManagement]):
        self.http_client = module_instance._http_client
        self.user_management = module_instance

    def test_revoke_session(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(self.http_client, {}, 200)

        response = syncify(
            self.user_management.revoke_session(session_id="session_abc")
        )

        assert request_kwargs["url"].endswith("user_management/sessions/revoke")
        assert request_kwargs["method"] == "post"
        assert request_kwargs["json"] == {"session_id": "session_abc"}
        assert response is None
