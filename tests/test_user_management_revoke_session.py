from typing import Union

import pytest

from tests.utils.syncify import syncify
from workos.user_management import AsyncUserManagement, UserManagement


def _mock_session(id: str):
    now = "2025-07-23T14:00:00.000Z"
    return {
        "object": "session",
        "id": id,
        "user_id": "user_123",
        "organization_id": "org_123",
        "status": "revoked",
        "auth_method": "password",
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0",
        "expires_at": "2025-07-23T15:00:00.000Z",
        "ended_at": now,
        "created_at": now,
        "updated_at": now,
    }


@pytest.mark.sync_and_async(UserManagement, AsyncUserManagement)
class TestUserManagementRevokeSession:
    @pytest.fixture(autouse=True)
    def setup(self, module_instance: Union[UserManagement, AsyncUserManagement]):
        self.http_client = module_instance._http_client
        self.user_management = module_instance

    def test_revoke_session(self, capture_and_mock_http_client_request):
        mock = _mock_session("session_abc")
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock, 200
        )

        response = syncify(
            self.user_management.revoke_session(session_id="session_abc")
        )

        assert request_kwargs["url"].endswith("user_management/sessions/revoke")
        assert request_kwargs["method"] == "post"
        assert request_kwargs["json"] == {"session_id": "session_abc"}
        assert response.id == "session_abc"
