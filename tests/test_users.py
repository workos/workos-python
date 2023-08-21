import pytest

from tests.utils.fixtures.mock_user import MockUser
from workos.users import Users


class TestUsers(object):
    @pytest.fixture(autouse=True)
    def setup(self, set_api_key, set_client_id):
        self.users = Users()

    @pytest.fixture
    def mock_user(self):
        return MockUser("user_01H7ZGXFP5C6BBQY6Z7277ZCT0").to_dict()

    @pytest.fixture
    def mock_users(self):
        user_list = [MockUser(id=str(i)).to_dict() for i in range(5000)]

        dict_response = {
            "data": user_list,
            "list_metadata": {"before": None, "after": None},
            "metadata": {
                "params": {
                    "organization": None,
                    "email": None,
                    "limit": None,
                    "before": None,
                    "after": None,
                    "order": None,
                    "default_limit": True,
                },
                "method": Users.list_users,
            },
        }
        return dict_response

    @pytest.fixture
    def mock_users_with_limit(self):
        user_list = [MockUser(id=str(i)).to_dict() for i in range(4)]
        dict_response = {
            "data": user_list,
            "list_metadata": {"before": None, "after": None},
            "metadata": {
                "params": {
                    "type": None,
                    "organization": None,
                    "email": None,
                    "limit": 4,
                    "before": None,
                    "after": None,
                    "order": None,
                },
                "method": Users.list_users,
            },
        }
        return self.users.construct_from_response(dict_response)

    @pytest.fixture
    def mock_users_with_default_limit(self):
        user_list = [MockUser(id=str(i)).to_dict() for i in range(10)]

        dict_response = {
            "data": user_list,
            "list_metadata": {"before": None, "after": "user_id_xxx"},
            "metadata": {
                "params": {
                    "type": None,
                    "organization": None,
                    "email": None,
                    "limit": None,
                    "before": None,
                    "after": None,
                    "order": None,
                    "default_limit": True,
                },
                "method": Users.list_users,
            },
        }
        return self.users.construct_from_response(dict_response)

    @pytest.fixture
    def mock_users_pagination_response(self):
        user_list = [MockUser(id=str(i)).to_dict() for i in range(4990)]

        return {
            "data": user_list,
            "list_metadata": {"before": None, "after": None},
            "metadata": {
                "params": {
                    "domains": None,
                    "limit": None,
                    "before": None,
                    "after": None,
                    "order": None,
                    "default_limit": True,
                },
                "method": Users.list_users,
            },
        }

    def test_create_user(self, mock_user, mock_request_method):
        mock_request_method("post", mock_user, 201)

        payload = {
            "email": "marcelina@foo-corp.com",
            "first_name": "Marcelina",
            "last_name": "Hoeger",
            "password": "password",
            "email_verified": False,
        }
        user = self.users.create_user(payload)

        assert user["id"] == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"

    def test_get_user(self, mock_user, capture_and_mock_request):
        url, request_kwargs = capture_and_mock_request("get", mock_user, 201)

        user = self.users.get_user("user_01H7ZGXFP5C6BBQY6Z7277ZCT0")

        assert url[0].endswith("users/user_01H7ZGXFP5C6BBQY6Z7277ZCT0")
        assert user["id"] == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"

    def test_list_users_auto_pagination(
        self,
        mock_users_with_default_limit,
        mock_users_pagination_response,
        mock_users,
        mock_request_method,
    ):
        mock_request_method("get", mock_users_pagination_response, 200)
        users = mock_users_with_default_limit
        all_users = users.auto_paging_iter()
        assert len(*list(all_users)) == len(mock_users["data"])

    def test_list_users_honors_limit(
        self,
        mock_users_with_limit,
        mock_users_pagination_response,
        mock_request_method,
    ):
        mock_request_method("get", mock_users_pagination_response, 200)
        users = mock_users_with_limit
        all_users = users.auto_paging_iter()
        dict_response = users.to_dict()
        assert len(*list(all_users)) == len(dict_response["data"])

    def test_list_users_returns_metadata(
        self,
        mock_users,
        mock_request_method,
    ):
        mock_request_method("get", mock_users, 200)

        users = self.users.list_users(
            email="marcelina@foo-corp.com",
            organization="foo-corp.com",
        )

        dict_users = users.to_dict()
        assert dict_users["metadata"]["params"]["email"] == "marcelina@foo-corp.com"
        assert dict_users["metadata"]["params"]["organization"] == "foo-corp.com"

    def test_add_user_to_organization(self, capture_and_mock_request, mock_user):
        url, _ = capture_and_mock_request("post", mock_user, 200)

        user = self.users.add_user_to_organization("user_123", "org_123")

        assert url[0].endswith("users/user_123/organization/org_123")
        assert user["id"] == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"

    def test_remove_user_from_organization(self, capture_and_mock_request, mock_user):
        url, _ = capture_and_mock_request("delete", mock_user, 200)

        user = self.users.remove_user_from_organization("user_123", "org_123")

        assert url[0].endswith("users/user_123/organization/org_123")
        assert user["id"] == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
