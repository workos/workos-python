import pytest

from tests.utils.fixtures.mock_session import MockSession
from tests.utils.fixtures.mock_user import MockUser
from workos.user_management import UserManagement


class TestUserManagement(object):
    @pytest.fixture(autouse=True)
    def setup(self, set_api_key, set_client_id):
        self.user_management = UserManagement()

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
                    "organization_id": None,
                    "email": None,
                    "limit": None,
                    "before": None,
                    "after": None,
                    "order": None,
                    "default_limit": True,
                },
                "method": UserManagement.list_users,
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
                    "organization_id": None,
                    "email": None,
                    "limit": 4,
                    "before": None,
                    "after": None,
                    "order": None,
                },
                "method": UserManagement.list_users,
            },
        }
        return self.user_management.construct_from_response(dict_response)

    @pytest.fixture
    def mock_users_with_default_limit(self):
        user_list = [MockUser(id=str(i)).to_dict() for i in range(10)]

        dict_response = {
            "data": user_list,
            "list_metadata": {"before": None, "after": "user_id_xxx"},
            "metadata": {
                "params": {
                    "type": None,
                    "organization_id": None,
                    "email": None,
                    "limit": None,
                    "before": None,
                    "after": None,
                    "order": None,
                    "default_limit": True,
                },
                "method": UserManagement.list_users,
            },
        }
        return self.user_management.construct_from_response(dict_response)

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
                "method": UserManagement.list_users,
            },
        }

    @pytest.fixture
    def mock_auth_response(self):
        user = MockUser("user_01H7ZGXFP5C6BBQY6Z7277ZCT0").to_dict()
        session = MockSession("session_01E4ZCR3C56J083X43JQXF3JK5").to_dict()

        return {
            "user": user,
        }

    @pytest.fixture
    def mock_password_challenge_response(self):
        user = MockUser("user_01H7ZGXFP5C6BBQY6Z7277ZCT0").to_dict()

        return {
            "user": user,
            "token": "token_123",
        }

    @pytest.fixture
    def mock_magic_auth_challenge_response(self):
        return {
            "id": "auth_challenge_01E4ZCR3C56J083X43JQXF3JK5",
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
        user = self.user_management.create_user(payload)

        assert user["id"] == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"

    def test_get_user(self, mock_user, capture_and_mock_request):
        url, request_kwargs = capture_and_mock_request("get", mock_user, 200)

        user = self.user_management.get_user("user_01H7ZGXFP5C6BBQY6Z7277ZCT0")

        assert url[0].endswith("user_management/users/user_01H7ZGXFP5C6BBQY6Z7277ZCT0")
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

        users = self.user_management.list_users(
            email="marcelina@foo-corp.com",
            organization_id="org_12345",
        )

        dict_users = users.to_dict()
        assert dict_users["metadata"]["params"]["email"] == "marcelina@foo-corp.com"
        assert dict_users["metadata"]["params"]["organization_id"] == "org_12345"

    def test_delete_user(self, capture_and_mock_request):
        url, request_kwargs = capture_and_mock_request("delete", None, 200)

        user = self.user_management.delete_user("user_01H7ZGXFP5C6BBQY6Z7277ZCT0")

        assert url[0].endswith("user_management/users/user_01H7ZGXFP5C6BBQY6Z7277ZCT0")
        assert user is None

    def test_update_user(self, mock_user, capture_and_mock_request):
        url, request = capture_and_mock_request("put", mock_user, 200)

        user = self.user_management.update_user(
            "user_01H7ZGXFP5C6BBQY6Z7277ZCT0",
            {
                "first_name": "Marcelina",
                "last_name": "Hoeger",
                "email_verified": True,
            },
        )

        assert url[0].endswith("users/user_01H7ZGXFP5C6BBQY6Z7277ZCT0")
        assert user["id"] == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        assert request["json"]["first_name"] == "Marcelina"
        assert request["json"]["last_name"] == "Hoeger"
        assert request["json"]["email_verified"] == True

    def test_update_user_password(self, mock_user, capture_and_mock_request):
        url, request = capture_and_mock_request("put", mock_user, 200)

        user = self.user_management.update_user_password(
            "user_01H7ZGXFP5C6BBQY6Z7277ZCT0", "pass_123"
        )

        assert url[0].endswith("users/user_01H7ZGXFP5C6BBQY6Z7277ZCT0/password")
        assert user["id"] == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        assert request["json"]["password"] == "pass_123"

    def test_add_user_to_organization(self, capture_and_mock_request, mock_user):
        url, _ = capture_and_mock_request("post", mock_user, 200)

        user = self.user_management.add_user_to_organization("user_123", "org_123")

        assert url[0].endswith("users/user_123/organization/org_123")
        assert user["id"] == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"

    def test_remove_user_from_organization(self, capture_and_mock_request, mock_user):
        url, _ = capture_and_mock_request("delete", mock_user, 200)

        user = self.user_management.remove_user_from_organization("user_123", "org_123")

        assert url[0].endswith("users/user_123/organization/org_123")
        assert user["id"] == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"

    def test_authenticate_with_magic_auth(
        self, capture_and_mock_request, mock_auth_response
    ):
        code = "test_auth"
        user = "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        ip_address = "192.0.0.1"

        url, request = capture_and_mock_request("post", mock_auth_response, 200)

        response = self.user_management.authenticate_with_magic_auth(
            code=code,
            user=user,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        assert url[0].endswith("users/authenticate")
        assert response["user"]["id"] == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        assert request["json"]["code"] == code
        assert request["json"]["user_agent"] == user_agent
        assert request["json"]["user_id"] == user
        assert request["json"]["ip_address"] == ip_address
        assert request["json"]["client_id"] == "client_b27needthisforssotemxo"
        assert request["json"]["client_secret"] == "sk_abdsomecharactersm284"
        assert (
            request["json"]["grant_type"]
            == "urn:workos:oauth:grant-type:magic-auth:code"
        )

    def test_authenticate_with_password(
        self, capture_and_mock_request, mock_auth_response
    ):
        email = "marcelina@foo-corp.com"
        password = "test123"
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        ip_address = "192.0.0.1"

        url, request = capture_and_mock_request("post", mock_auth_response, 200)

        response = self.user_management.authenticate_with_password(
            email=email,
            password=password,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        assert url[0].endswith("users/authenticate")
        assert response["user"]["id"] == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        assert request["json"]["email"] == email
        assert request["json"]["password"] == password
        assert request["json"]["user_agent"] == user_agent
        assert request["json"]["ip_address"] == ip_address
        assert request["json"]["client_id"] == "client_b27needthisforssotemxo"
        assert request["json"]["client_secret"] == "sk_abdsomecharactersm284"
        assert request["json"]["grant_type"] == "password"

    def test_authenticate_with_code(self, capture_and_mock_request, mock_auth_response):
        code = "test_code"
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        ip_address = "192.0.0.1"

        url, request = capture_and_mock_request("post", mock_auth_response, 200)

        response = self.user_management.authenticate_with_code(
            code=code,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        assert url[0].endswith("users/authenticate")
        assert response["user"]["id"] == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        assert request["json"]["code"] == code
        assert request["json"]["user_agent"] == user_agent
        assert request["json"]["ip_address"] == ip_address
        assert request["json"]["client_id"] == "client_b27needthisforssotemxo"
        assert request["json"]["client_secret"] == "sk_abdsomecharactersm284"
        assert request["json"]["grant_type"] == "authorization_code"

    def test_create_password_challenge(
        self, capture_and_mock_request, mock_password_challenge_response
    ):
        email = "marcelina@foo-corp.com"
        password_reset_url = "https://foo-corp.com/reset-password"

        url, request = capture_and_mock_request(
            "post", mock_password_challenge_response, 200
        )

        response = self.user_management.create_password_reset_challenge(
            email=email,
            password_reset_url=password_reset_url,
        )

        assert url[0].endswith("users/password_reset_challenge")
        assert response["user"]["id"] == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        assert response["token"] == "token_123"
        assert request["json"]["email"] == email
        assert request["json"]["password_reset_url"] == password_reset_url

    def test_complete_password_reset(self, capture_and_mock_request, mock_user):
        token = "token123"
        new_password = "pass123"

        url, request = capture_and_mock_request("post", mock_user, 200)

        response = self.user_management.complete_password_reset(
            token=token,
            new_password=new_password,
        )

        assert url[0].endswith("users/password_reset")
        assert response["id"] == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        assert request["json"]["token"] == token
        assert request["json"]["new_password"] == new_password

    def test_send_verification_email(self, capture_and_mock_request, mock_user):
        user = "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"

        url, _ = capture_and_mock_request("post", mock_user, 200)

        response = self.user_management.send_verification_email(user=user)

        assert url[0].endswith(
            "users/user_01H7ZGXFP5C6BBQY6Z7277ZCT0/send_verification_email"
        )
        assert response["id"] == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"

    def test_verify_email_code(self, capture_and_mock_request, mock_auth_response):
        user = "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        code = "code_123"

        url, request = capture_and_mock_request("post", mock_auth_response, 200)

        response = self.user_management.verify_email_code(user=user, code=code)

        assert url[0].endswith("users/verify_email_code")
        assert request["json"]["user_id"] == user
        assert request["json"]["code"] == code
        assert response["id"] == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"

    def test_send_magic_auth_code(self, capture_and_mock_request, mock_user):
        email = "marcelina@foo-corp.com"

        url, request = capture_and_mock_request("post", mock_user, 200)

        response = self.user_management.send_magic_auth_code(email=email)

        assert url[0].endswith("user_management/magic_auth/send")
        assert request["json"]["email"] == email
        assert response["id"] == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
