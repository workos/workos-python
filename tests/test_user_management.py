import pytest

from tests.utils.fixtures.mock_auth_factor_totp import MockAuthFactorTotp
from tests.utils.fixtures.mock_invitation import MockInvitation
from tests.utils.fixtures.mock_organization_membership import MockOrganizationMembership
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
    def mock_organization_membership(self):
        return MockOrganizationMembership("om_ABCDE").to_dict()

    @pytest.fixture
    def mock_organization_memberships(self):
        om_list = [MockOrganizationMembership(id=str(i)).to_dict() for i in range(50)]

        dict_response = {
            "data": om_list,
            "list_metadata": {"before": None, "after": None},
            "metadata": {
                "params": {
                    "user_id": None,
                    "organization_id": None,
                    "limit": None,
                    "before": None,
                    "after": None,
                    "order": None,
                    "default_limit": True,
                },
                "method": UserManagement.list_organization_memberships,
            },
        }
        return dict_response

    @pytest.fixture
    def mock_auth_response(self):
        user = MockUser("user_01H7ZGXFP5C6BBQY6Z7277ZCT0").to_dict()

        return {"user": user, "organization_id": "org_12345"}

    @pytest.fixture
    def mock_magic_auth_challenge_response(self):
        return {
            "id": "auth_challenge_01E4ZCR3C56J083X43JQXF3JK5",
        }

    @pytest.fixture
    def mock_enroll_auth_factor_response(self):
        return {
            "authentication_factor": {
                "object": "authentication_factor",
                "id": "auth_factor_01FVYZ5QM8N98T9ME5BCB2BBMJ",
                "created_at": "2022-02-15T15:14:19.392Z",
                "updated_at": "2022-02-15T15:14:19.392Z",
                "type": "totp",
                "totp": {
                    "qr_code": "data:image/png;base64,{base64EncodedPng}",
                    "secret": "NAGCCFS3EYRB422HNAKAKY3XDUORMSRF",
                    "uri": "otpauth://totp/FooCorp:alan.turing@foo-corp.com?secret=NAGCCFS3EYRB422HNAKAKY3XDUORMSRF&issuer=FooCorp",
                },
            },
            "authentication_challenge": {
                "object": "authentication_challenge",
                "id": "auth_challenge_01FVYZWQTZQ5VB6BC5MPG2EYC5",
                "created_at": "2022-02-15T15:26:53.274Z",
                "updated_at": "2022-02-15T15:26:53.274Z",
                "expires_at": "2022-02-15T15:36:53.279Z",
                "authentication_factor_id": "auth_factor_01FVYZ5QM8N98T9ME5BCB2BBMJ",
            },
        }

    @pytest.fixture
    def mock_auth_factors(self):
        auth_factors_list = [MockAuthFactorTotp(id=str(i)).to_dict() for i in range(2)]

        dict_response = {
            "data": auth_factors_list,
            "list_metadata": {"before": None, "after": None},
            "metadata": {
                "params": {
                    "user_id": "user_12345",
                },
                "method": UserManagement.list_auth_factors,
            },
        }
        return dict_response

    @pytest.fixture
    def mock_invitation(self):
        return MockInvitation("invitation_ABCDE").to_dict()

    @pytest.fixture
    def mock_invitations(self):
        invitation_list = [MockInvitation(id=str(i)).to_dict() for i in range(50)]

        dict_response = {
            "data": invitation_list,
            "list_metadata": {"before": None, "after": None},
            "metadata": {
                "params": {
                    "email": None,
                    "organization_id": None,
                    "limit": None,
                    "before": None,
                    "after": None,
                    "order": None,
                    "default_limit": True,
                },
                "method": UserManagement.list_invitations,
            },
        }
        return dict_response

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

    def test_update_user(self, mock_user, capture_and_mock_request):
        url, request = capture_and_mock_request("put", mock_user, 200)

        user = self.user_management.update_user(
            "user_01H7ZGXFP5C6BBQY6Z7277ZCT0",
            {
                "first_name": "Marcelina",
                "last_name": "Hoeger",
                "email_verified": True,
                "password": "password",
            },
        )

        assert url[0].endswith("users/user_01H7ZGXFP5C6BBQY6Z7277ZCT0")
        assert user["id"] == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        assert request["json"]["first_name"] == "Marcelina"
        assert request["json"]["last_name"] == "Hoeger"
        assert request["json"]["email_verified"] == True
        assert request["json"]["password"] == "password"

    def test_delete_user(self, capture_and_mock_request):
        url, request_kwargs = capture_and_mock_request("delete", None, 200)

        user = self.user_management.delete_user("user_01H7ZGXFP5C6BBQY6Z7277ZCT0")

        assert url[0].endswith("user_management/users/user_01H7ZGXFP5C6BBQY6Z7277ZCT0")
        assert user is None

    def test_create_organization_membership(
        self, capture_and_mock_request, mock_organization_membership
    ):
        user_id = "user_12345"
        organization_id = "org_67890"
        url, _ = capture_and_mock_request("post", mock_organization_membership, 201)

        organization_membership = self.user_management.create_organization_membership(
            user_id=user_id, organization_id=organization_id
        )

        assert url[0].endswith("user_management/organization_memberships")
        assert organization_membership["user_id"] == user_id
        assert organization_membership["organization_id"] == organization_id

    def test_get_organization_membership(
        self, mock_organization_membership, capture_and_mock_request
    ):
        url, request_kwargs = capture_and_mock_request(
            "get", mock_organization_membership, 200
        )

        om = self.user_management.get_organization_membership("om_ABCDE")

        assert url[0].endswith("user_management/organization_memberships/om_ABCDE")
        assert om["id"] == "om_ABCDE"

    def test_list_organization_memberships_returns_metadata(
        self,
        mock_organization_memberships,
        mock_request_method,
    ):
        mock_request_method("get", mock_organization_memberships, 200)

        oms = self.user_management.list_organization_memberships(
            organization_id="org_12345",
        )

        dict_oms = oms.to_dict()
        assert dict_oms["metadata"]["params"]["organization_id"] == "org_12345"

    def test_delete_organization_membership(self, capture_and_mock_request):
        url, request_kwargs = capture_and_mock_request("delete", None, 200)

        user = self.user_management.delete_organization_membership("om_ABCDE")

        assert url[0].endswith("user_management/organization_memberships/om_ABCDE")
        assert user is None

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

        assert url[0].endswith("user_management/authenticate")
        assert response["user"]["id"] == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        assert response["organization_id"] == "org_12345"
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

        assert url[0].endswith("user_management/authenticate")
        assert response["user"]["id"] == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        assert response["organization_id"] == "org_12345"
        assert request["json"]["code"] == code
        assert request["json"]["user_agent"] == user_agent
        assert request["json"]["ip_address"] == ip_address
        assert request["json"]["client_id"] == "client_b27needthisforssotemxo"
        assert request["json"]["client_secret"] == "sk_abdsomecharactersm284"
        assert request["json"]["grant_type"] == "authorization_code"

    def test_authenticate_with_magic_auth(
        self, capture_and_mock_request, mock_auth_response
    ):
        code = "test_auth"
        email = "marcelina@foo-corp.com"
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        ip_address = "192.0.0.1"

        url, request = capture_and_mock_request("post", mock_auth_response, 200)

        response = self.user_management.authenticate_with_magic_auth(
            code=code,
            email=email,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        assert url[0].endswith("user_management/authenticate")
        assert response["user"]["id"] == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        assert response["organization_id"] == "org_12345"
        assert request["json"]["code"] == code
        assert request["json"]["user_agent"] == user_agent
        assert request["json"]["email"] == email
        assert request["json"]["ip_address"] == ip_address
        assert request["json"]["client_id"] == "client_b27needthisforssotemxo"
        assert request["json"]["client_secret"] == "sk_abdsomecharactersm284"
        assert (
            request["json"]["grant_type"]
            == "urn:workos:oauth:grant-type:magic-auth:code"
        )

    def test_authenticate_with_email_verification(
        self, capture_and_mock_request, mock_auth_response
    ):
        code = "test_auth"
        pending_authentication_token = "ql1AJgNoLN1tb9llaQ8jyC2dn"
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        ip_address = "192.0.0.1"

        url, request = capture_and_mock_request("post", mock_auth_response, 200)

        response = self.user_management.authenticate_with_email_verification(
            code=code,
            pending_authentication_token=pending_authentication_token,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        assert url[0].endswith("user_management/authenticate")
        assert response["user"]["id"] == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        assert response["organization_id"] == "org_12345"
        assert request["json"]["code"] == code
        assert request["json"]["user_agent"] == user_agent
        assert (
            request["json"]["pending_authentication_token"]
            == pending_authentication_token
        )
        assert request["json"]["ip_address"] == ip_address
        assert request["json"]["client_id"] == "client_b27needthisforssotemxo"
        assert request["json"]["client_secret"] == "sk_abdsomecharactersm284"
        assert (
            request["json"]["grant_type"]
            == "urn:workos:oauth:grant-type:email-verification:code"
        )

    def test_authenticate_with_totp(self, capture_and_mock_request, mock_auth_response):
        code = "test_auth"
        authentication_challenge_id = "auth_challenge_01FVYZWQTZQ5VB6BC5MPG2EYC5"
        pending_authentication_token = "ql1AJgNoLN1tb9llaQ8jyC2dn"
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        ip_address = "192.0.0.1"

        url, request = capture_and_mock_request("post", mock_auth_response, 200)

        response = self.user_management.authenticate_with_totp(
            code=code,
            authentication_challenge_id=authentication_challenge_id,
            pending_authentication_token=pending_authentication_token,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        assert url[0].endswith("user_management/authenticate")
        assert response["user"]["id"] == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        assert response["organization_id"] == "org_12345"
        assert request["json"]["code"] == code
        assert request["json"]["user_agent"] == user_agent
        assert (
            request["json"]["authentication_challenge_id"]
            == authentication_challenge_id
        )
        assert (
            request["json"]["pending_authentication_token"]
            == pending_authentication_token
        )
        assert request["json"]["ip_address"] == ip_address
        assert request["json"]["client_id"] == "client_b27needthisforssotemxo"
        assert request["json"]["client_secret"] == "sk_abdsomecharactersm284"
        assert request["json"]["grant_type"] == "urn:workos:oauth:grant-type:mfa-totp"

    def test_authenticate_with_organization_selection(
        self, capture_and_mock_request, mock_auth_response
    ):
        organization_id = "org_12345"
        pending_authentication_token = "ql1AJgNoLN1tb9llaQ8jyC2dn"
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        ip_address = "192.0.0.1"

        url, request = capture_and_mock_request("post", mock_auth_response, 200)

        response = self.user_management.authenticate_with_organization_selection(
            organization_id=organization_id,
            pending_authentication_token=pending_authentication_token,
            user_agent=user_agent,
            ip_address=ip_address,
        )

        assert url[0].endswith("user_management/authenticate")
        assert response["user"]["id"] == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        assert response["organization_id"] == "org_12345"
        assert request["json"]["organization_id"] == organization_id
        assert request["json"]["user_agent"] == user_agent
        assert (
            request["json"]["pending_authentication_token"]
            == pending_authentication_token
        )
        assert request["json"]["ip_address"] == ip_address
        assert request["json"]["client_id"] == "client_b27needthisforssotemxo"
        assert request["json"]["client_secret"] == "sk_abdsomecharactersm284"
        assert (
            request["json"]["grant_type"]
            == "urn:workos:oauth:grant-type:organization-selection"
        )

    def test_send_password_reset_email(self, capture_and_mock_request):
        email = "marcelina@foo-corp.com"
        password_reset_url = "https://foo-corp.com/reset-password"

        url, request = capture_and_mock_request("post", None, 200)

        response = self.user_management.send_password_reset_email(
            email=email,
            password_reset_url=password_reset_url,
        )

        assert url[0].endswith("user_management/password_reset/send")
        assert request["json"]["email"] == email
        assert request["json"]["password_reset_url"] == password_reset_url
        assert response is None

    def test_reset_password(self, capture_and_mock_request, mock_user):
        token = "token123"
        new_password = "pass123"

        url, request = capture_and_mock_request("post", mock_user, 200)

        response = self.user_management.reset_password(
            token=token,
            new_password=new_password,
        )

        assert url[0].endswith("user_management/password_reset/confirm")
        assert response["id"] == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        assert request["json"]["token"] == token
        assert request["json"]["new_password"] == new_password

    def test_send_verification_email(self, capture_and_mock_request, mock_user):
        user_id = "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"

        url, _ = capture_and_mock_request("post", mock_user, 200)

        response = self.user_management.send_verification_email(user_id=user_id)

        assert url[0].endswith(
            "users/user_01H7ZGXFP5C6BBQY6Z7277ZCT0/send_verification_email"
        )
        assert response["id"] == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"

    def test_verify_email_code(self, capture_and_mock_request, mock_auth_response):
        user_id = "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        code = "code_123"

        url, request = capture_and_mock_request("post", mock_auth_response, 200)

        response = self.user_management.verify_email_code(user_id=user_id, code=code)

        assert url[0].endswith("users/verify_email_code")
        assert request["json"]["user_id"] == user_id
        assert request["json"]["code"] == code
        assert response["id"] == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"

    def test_send_magic_auth_code(self, capture_and_mock_request):
        email = "marcelina@foo-corp.com"

        url, request = capture_and_mock_request("post", None, 200)

        response = self.user_management.send_magic_auth_code(email=email)

        assert url[0].endswith("user_management/magic_auth/send")
        assert request["json"]["email"] == email
        assert response is None

    def test_enroll_auth_factor(
        self, mock_enroll_auth_factor_response, mock_request_method
    ):
        user_id = "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        type = "totp"
        totp_issuer = "WorkOS"
        totp_user = "marcelina@foo-corp.com"

        mock_request_method("post", mock_enroll_auth_factor_response, 200)

        enroll_auth_factor = self.user_management.enroll_auth_factor(
            user_id=user_id,
            type=type,
            totp_issuer=totp_issuer,
            totp_user=totp_user,
        )

        assert enroll_auth_factor == mock_enroll_auth_factor_response

    def test_auth_factors_returns_metadata(
        self,
        mock_auth_factors,
        mock_request_method,
    ):
        mock_request_method("get", mock_auth_factors, 200)

        auth_factors = self.user_management.list_auth_factors(
            user_id="user_12345",
        )

        dict_auth_factors = auth_factors.to_dict()
        assert dict_auth_factors["metadata"]["params"]["user_id"] == "user_12345"

    def test_get_invitation(self, mock_invitation, capture_and_mock_request):
        url, request_kwargs = capture_and_mock_request("get", mock_invitation, 200)

        invitation = self.user_management.get_invitation("invitation_ABCDE")

        assert url[0].endswith("user_management/invitations/invitation_ABCDE")
        assert invitation["id"] == "invitation_ABCDE"

    def test_list_invitations_returns_metadata(
        self,
        mock_invitations,
        mock_request_method,
    ):
        mock_request_method("get", mock_invitations, 200)

        invitations = self.user_management.list_invitations(
            organization_id="org_12345",
        )

        dict_invitations = invitations.to_dict()
        assert dict_invitations["metadata"]["params"]["organization_id"] == "org_12345"

    def test_send_invitation(self, capture_and_mock_request, mock_invitation):
        email = "marcelina@foo-corp.com"
        organization_id = "org_12345"
        url, _ = capture_and_mock_request("post", mock_invitation, 201)

        invitation = self.user_management.send_invitation(
            email=email, organization_id=organization_id
        )

        assert url[0].endswith("user_management/invitations")
        assert invitation["email"] == email
        assert invitation["organization_id"] == organization_id

    def test_revoke_invitation(self, capture_and_mock_request, mock_invitation):
        url, _ = capture_and_mock_request("post", mock_invitation, 200)

        user = self.user_management.revoke_invitation("invitation_ABCDE")

        assert url[0].endswith("user_management/invitations/invitation_ABCDE/revoke")
