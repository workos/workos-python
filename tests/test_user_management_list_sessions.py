from typing import Union

import pytest

from tests.utils.list_resource import list_response_of
from tests.utils.syncify import syncify
from tests.types.test_auto_pagination_function import TestAutoPaginationFunction
from workos.user_management import AsyncUserManagement, UserManagement


def _mock_session(id: str):
    now = "2025-07-23T14:00:00.000Z"
    return {
        "object": "session",
        "id": id,
        "user_id": "user_123",
        "organization_id": "org_123",
        "status": "active",
        "auth_method": "password",
        "impersonator": None,
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0",
        "expires_at": "2025-07-23T15:00:00.000Z",
        "ended_at": None,
        "created_at": now,
        "updated_at": now,
    }


@pytest.mark.sync_and_async(UserManagement, AsyncUserManagement)
class TestUserManagementListSessions:
    @pytest.fixture(autouse=True)
    def setup(self, module_instance: Union[UserManagement, AsyncUserManagement]):
        self.http_client = module_instance._http_client
        self.user_management = module_instance

    def test_list_sessions_query_and_parsing(
        self, capture_and_mock_http_client_request
    ):
        sessions = [_mock_session("session_1"), _mock_session("session_2")]
        response = list_response_of(data=sessions)
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, response, 200
        )

        result = syncify(
            self.user_management.list_sessions(
                user_id="user_123", limit=10, before="before_id", order="desc"
            )
        )

        assert request_kwargs["url"].endswith("user_management/users/user_123/sessions")
        assert request_kwargs["method"] == "get"
        assert request_kwargs["params"]["limit"] == 10
        assert request_kwargs["params"]["before"] == "before_id"
        assert request_kwargs["params"]["order"] == "desc"
        assert "after" not in request_kwargs["params"]
        assert len(result.data) == 2
        assert result.data[0].id == "session_1"
        assert result.list_metadata.before is None
        assert result.list_metadata.after is None

    def test_list_sessions_auto_pagination(
        self, test_auto_pagination: TestAutoPaginationFunction
    ):
        data = [_mock_session(str(i)) for i in range(40)]
        test_auto_pagination(
            http_client=self.http_client,
            list_function=self.user_management.list_sessions,
            list_function_params={"user_id": "user_123"},
            expected_all_page_data=data,
            url_path_keys=["user_id"],
        )
