import json

from six.moves.urllib.parse import parse_qsl, urlparse
import pytest

from tests.utils.fixtures.mock_auth_factor_totp import MockAuthFactorTotp
from tests.utils.fixtures.mock_email_verification import MockEmailVerification
from tests.utils.fixtures.mock_invitation import MockInvitation
from tests.utils.fixtures.mock_magic_auth import MockMagicAuth
from tests.utils.fixtures.mock_organization_membership import MockOrganizationMembership
from tests.utils.fixtures.mock_password_reset import MockPasswordReset
from tests.utils.fixtures.mock_user import MockUser

from tests.utils.list_resource import list_response_of
import workos
from workos.user_management import UserManagement
from workos.utils.http_client import SyncHTTPClient
from workos.utils.request_helper import RESPONSE_TYPE_CODE


class TestUserManagement(object):
    @pytest.fixture(autouse=True)
    def setup(self, set_api_key, set_client_id):
        self.http_client = SyncHTTPClient(
            base_url="https://api.workos.test", version="test"
        )
        self.user_management = UserManagement(http_client=self.http_client)

    @pytest.fixture
    def mock_user(self):
        return MockUser("user_01H7ZGXFP5C6BBQY6Z7277ZCT0").to_dict()

    @pytest.fixture
    def mock_users_multiple_pages(self):
        users_list = [MockUser(id=str(i)).to_dict() for i in range(40)]
        return list_response_of(data=users_list)

    @pytest.fixture
    def mock_organization_membership(self):
        return MockOrganizationMembership("om_ABCDE").to_dict()

    @pytest.fixture
    def mock_organization_memberships_multiple_pages(self):
        organization_memberships_list = [
            MockOrganizationMembership(id=str(i)).to_dict() for i in range(40)
        ]
        return list_response_of(data=organization_memberships_list)

    @pytest.fixture
    def mock_auth_response(self):
        user = MockUser("user_01H7ZGXFP5C6BBQY6Z7277ZCT0").to_dict()

        return {
            "user": user,
            "organization_id": "org_12345",
            "access_token": "access_token_12345",
            "refresh_token": "refresh_token_12345",
        }

    @pytest.fixture
    def base_authentication_params(self):
        return {
            "client_id": "client_b27needthisforssotemxo",
            "client_secret": "sk_test",
        }

    @pytest.fixture
    def mock_auth_refresh_token_response(self):
        return {
            "access_token": "access_token_12345",
            "refresh_token": "refresh_token_12345",
        }

    @pytest.fixture
    def mock_auth_response_with_impersonator(self):
        user = MockUser("user_01H7ZGXFP5C6BBQY6Z7277ZCT0").to_dict()

        return {
            "user": user,
            "access_token": "access_token_12345",
            "refresh_token": "refresh_token_12345",
            "organization_id": "org_12345",
            "impersonator": {
                "email": "admin@foocorp.com",
                "reason": "Debugging an account issue.",
            },
        }

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
                "user_id": "user_12345",
                "created_at": "2022-02-15T15:14:19.392Z",
                "updated_at": "2022-02-15T15:14:19.392Z",
                "type": "totp",
                "totp": {
                    "issuer": "FooCorp",
                    "user": "test@example.com",
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
                "code": None,
                "authentication_factor_id": "auth_factor_01FVYZ5QM8N98T9ME5BCB2BBMJ",
            },
        }

    @pytest.fixture
    def mock_auth_factors_multiple_pages(self):
        auth_factors_list = [MockAuthFactorTotp(id=str(i)).to_dict() for i in range(40)]
        return list_response_of(data=auth_factors_list)

    @pytest.fixture
    def mock_email_verification(self):
        return MockEmailVerification("email_verification_ABCDE").to_dict()

    @pytest.fixture
    def mock_magic_auth(self):
        return MockMagicAuth("magic_auth_ABCDE").to_dict()

    @pytest.fixture
    def mock_password_reset(self):
        return MockPasswordReset("password_reset_ABCDE").to_dict()

    @pytest.fixture
    def mock_invitation(self):
        return MockInvitation("invitation_ABCDE").to_dict()

    @pytest.fixture
    def mock_invitations_multiple_pages(self):
        invitations_list = [MockInvitation(id=str(i)).to_dict() for i in range(40)]
        return list_response_of(data=invitations_list)

    def test_get_user(self, mock_user, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_user, 200
        )

        user = self.user_management.get_user("user_01H7ZGXFP5C6BBQY6Z7277ZCT0")

        assert request_kwargs["url"].endswith(
            "user_management/users/user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        )
        assert user.id == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        assert user.profile_picture_url == "https://example.com/profile-picture.jpg"

    def test_list_users_auto_pagination(
        self, mock_users_multiple_pages, test_sync_auto_pagination
    ):
        test_sync_auto_pagination(
            http_client=self.http_client,
            list_function=self.user_management.list_users,
            expected_all_page_data=mock_users_multiple_pages["data"],
        )

    def test_create_user(self, mock_user, mock_http_client_with_response):
        mock_http_client_with_response(self.http_client, mock_user, 201)

        payload = {
            "email": "marcelina@foo-corp.com",
            "first_name": "Marcelina",
            "last_name": "Hoeger",
            "password": "password",
            "email_verified": False,
        }
        user = self.user_management.create_user(**payload)

        assert user.id == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"

    def test_update_user(self, mock_user, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_user, 200
        )

        params = {
            "first_name": "Marcelina",
            "last_name": "Hoeger",
            "email_verified": True,
            "password": "password",
        }
        user = self.user_management.update_user(
            "user_01H7ZGXFP5C6BBQY6Z7277ZCT0", **params
        )

        assert request_kwargs["url"].endswith("users/user_01H7ZGXFP5C6BBQY6Z7277ZCT0")
        assert user.id == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        assert request_kwargs["json"]["first_name"] == "Marcelina"
        assert request_kwargs["json"]["last_name"] == "Hoeger"
        assert request_kwargs["json"]["email_verified"] == True
        assert request_kwargs["json"]["password"] == "password"

    def test_delete_user(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            http_client=self.http_client, status_code=204
        )

        user = self.user_management.delete_user("user_01H7ZGXFP5C6BBQY6Z7277ZCT0")

        assert request_kwargs["url"].endswith(
            "user_management/users/user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        )
        assert user is None

    def test_create_organization_membership(
        self, capture_and_mock_http_client_request, mock_organization_membership
    ):
        user_id = "user_12345"
        organization_id = "org_67890"
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_organization_membership, 201
        )

        organization_membership = self.user_management.create_organization_membership(
            user_id=user_id, organization_id=organization_id
        )

        assert request_kwargs["url"].endswith(
            "user_management/organization_memberships"
        )
        assert organization_membership.user_id == user_id
        assert organization_membership.organization_id == organization_id

    def test_update_organization_membership(
        self, capture_and_mock_http_client_request, mock_organization_membership
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_organization_membership, 201
        )

        organization_membership = self.user_management.update_organization_membership(
            organization_membership_id="om_ABCDE",
            role_slug="member",
        )

        assert request_kwargs["url"].endswith(
            "user_management/organization_memberships/om_ABCDE"
        )
        assert organization_membership.id == "om_ABCDE"
        assert organization_membership.role == {"slug": "member"}

    def test_get_organization_membership(
        self, mock_organization_membership, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_organization_membership, 200
        )

        om = self.user_management.get_organization_membership("om_ABCDE")

        assert request_kwargs["url"].endswith(
            "user_management/organization_memberships/om_ABCDE"
        )
        assert om.id == "om_ABCDE"

    def test_delete_organization_membership(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            http_client=self.http_client, status_code=200
        )

        user = self.user_management.delete_organization_membership("om_ABCDE")

        assert request_kwargs["url"].endswith(
            "user_management/organization_memberships/om_ABCDE"
        )
        assert user is None

    def test_list_organization_memberships_auto_pagination(
        self, mock_organization_memberships_multiple_pages, test_sync_auto_pagination
    ):
        test_sync_auto_pagination(
            http_client=self.http_client,
            list_function=self.user_management.list_organization_memberships,
            expected_all_page_data=mock_organization_memberships_multiple_pages["data"],
        )

    def test_deactivate_organization_membership(
        self, mock_organization_membership, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_organization_membership, 200
        )

        om = self.user_management.deactivate_organization_membership("om_ABCDE")

        assert request_kwargs["url"].endswith(
            "user_management/organization_memberships/om_ABCDE/deactivate"
        )
        assert om.id == "om_ABCDE"

    def test_reactivate_organization_membership(
        self, mock_organization_membership, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_organization_membership, 200
        )

        om = self.user_management.reactivate_organization_membership("om_ABCDE")

        assert request_kwargs["url"].endswith(
            "user_management/organization_memberships/om_ABCDE/reactivate"
        )
        assert om.id == "om_ABCDE"

    def test_authorization_url_throws_value_error_with_missing_connection_organization_and_provider(
        self,
    ):
        redirect_uri = "https://localhost/auth/callback"
        with pytest.raises(ValueError, match=r"Incomplete arguments.*"):
            self.user_management.get_authorization_url(redirect_uri=redirect_uri)

    def test_authorization_url_has_expected_query_params_with_connection_id(self):
        connection_id = "connection_123"
        redirect_uri = "https://localhost/auth/callback"
        authorization_url = self.user_management.get_authorization_url(
            connection_id=connection_id,
            redirect_uri=redirect_uri,
        )

        parsed_url = urlparse(authorization_url)
        assert parsed_url.path == "/user_management/authorize"
        assert dict(parse_qsl(str(parsed_url.query))) == {
            "connection_id": connection_id,
            "client_id": workos.client_id,
            "redirect_uri": redirect_uri,
            "response_type": RESPONSE_TYPE_CODE,
        }

    def test_authorization_url_has_expected_query_params_with_organization_id(self):
        organization_id = "organization_123"
        redirect_uri = "https://localhost/auth/callback"
        authorization_url = self.user_management.get_authorization_url(
            organization_id=organization_id,
            redirect_uri=redirect_uri,
        )

        parsed_url = urlparse(authorization_url)
        assert parsed_url.path == "/user_management/authorize"
        assert dict(parse_qsl(str(parsed_url.query))) == {
            "organization_id": organization_id,
            "client_id": workos.client_id,
            "redirect_uri": redirect_uri,
            "response_type": RESPONSE_TYPE_CODE,
        }

    def test_authorization_url_has_expected_query_params_with_provider(self):
        provider = "GoogleOAuth"
        redirect_uri = "https://localhost/auth/callback"
        authorization_url = self.user_management.get_authorization_url(
            provider=provider, redirect_uri=redirect_uri
        )

        parsed_url = urlparse(authorization_url)
        assert parsed_url.path == "/user_management/authorize"
        assert dict(parse_qsl(str(parsed_url.query))) == {
            "provider": provider,
            "client_id": workos.client_id,
            "redirect_uri": redirect_uri,
            "response_type": RESPONSE_TYPE_CODE,
        }

    def test_authorization_url_has_expected_query_params_with_domain_hint(self):
        connection_id = "connection_123"
        redirect_uri = "https://localhost/auth/callback"
        domain_hint = "workos.com"

        authorization_url = self.user_management.get_authorization_url(
            connection_id=connection_id,
            domain_hint=domain_hint,
            redirect_uri=redirect_uri,
        )

        parsed_url = urlparse(authorization_url)
        assert parsed_url.path == "/user_management/authorize"
        assert dict(parse_qsl(str(parsed_url.query))) == {
            "domain_hint": domain_hint,
            "client_id": workos.client_id,
            "redirect_uri": redirect_uri,
            "connection_id": connection_id,
            "response_type": RESPONSE_TYPE_CODE,
        }

    def test_authorization_url_has_expected_query_params_with_login_hint(self):
        connection_id = "connection_123"
        redirect_uri = "https://localhost/auth/callback"
        login_hint = "foo@workos.com"

        authorization_url = self.user_management.get_authorization_url(
            connection_id=connection_id,
            login_hint=login_hint,
            redirect_uri=redirect_uri,
        )

        parsed_url = urlparse(authorization_url)
        assert parsed_url.path == "/user_management/authorize"
        assert dict(parse_qsl(str(parsed_url.query))) == {
            "login_hint": login_hint,
            "client_id": workos.client_id,
            "redirect_uri": redirect_uri,
            "connection_id": connection_id,
            "response_type": RESPONSE_TYPE_CODE,
        }

    def test_authorization_url_has_expected_query_params_with_state(self):
        connection_id = "connection_123"
        redirect_uri = "https://localhost/auth/callback"
        state = json.dumps({"things": "with_stuff"})

        authorization_url = self.user_management.get_authorization_url(
            connection_id=connection_id,
            state=state,
            redirect_uri=redirect_uri,
        )

        parsed_url = urlparse(authorization_url)
        assert parsed_url.path == "/user_management/authorize"
        assert dict(parse_qsl(str(parsed_url.query))) == {
            "state": state,
            "client_id": workos.client_id,
            "redirect_uri": redirect_uri,
            "connection_id": connection_id,
            "response_type": RESPONSE_TYPE_CODE,
        }

    def test_authorization_url_has_expected_query_params_with_code_challenge(self):
        connection_id = "connection_123"
        redirect_uri = "https://localhost/auth/callback"
        code_challenge = json.dumps({"code_challenge": "code_challenge_for_pkce"})

        authorization_url = self.user_management.get_authorization_url(
            connection_id=connection_id,
            code_challenge=code_challenge,
            redirect_uri=redirect_uri,
        )

        parsed_url = urlparse(authorization_url)
        assert parsed_url.path == "/user_management/authorize"
        assert dict(parse_qsl(str(parsed_url.query))) == {
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "client_id": workos.client_id,
            "redirect_uri": redirect_uri,
            "connection_id": connection_id,
            "response_type": RESPONSE_TYPE_CODE,
        }

    def test_authenticate_with_password(
        self,
        capture_and_mock_http_client_request,
        mock_auth_response,
        base_authentication_params,
    ):
        params = {
            "email": "marcelina@foo-corp.com",
            "password": "test123",
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "ip_address": "192.0.0.1",
        }
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_auth_response, 200
        )

        response = self.user_management.authenticate_with_password(**params)

        assert request_kwargs["url"].endswith("user_management/authenticate")
        assert response.user.id == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        assert response.organization_id == "org_12345"
        assert response.access_token == "access_token_12345"
        assert response.refresh_token == "refresh_token_12345"
        assert request_kwargs["json"] == {
            **params,
            **base_authentication_params,
            "grant_type": "password",
        }

    def test_authenticate_with_code(
        self,
        capture_and_mock_http_client_request,
        mock_auth_response,
        base_authentication_params,
    ):
        params = {
            "code": "test_code",
            "code_verifier": "test_code_verifier",
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "ip_address": "192.0.0.1",
        }
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_auth_response, 200
        )

        response = self.user_management.authenticate_with_code(**params)

        assert request_kwargs["url"].endswith("user_management/authenticate")
        assert response.user.id == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        assert response.organization_id == "org_12345"
        assert response.access_token == "access_token_12345"
        assert response.refresh_token == "refresh_token_12345"
        assert request_kwargs["json"] == {
            **params,
            **base_authentication_params,
            "grant_type": "authorization_code",
        }

    def test_authenticate_impersonator_with_code(
        self,
        capture_and_mock_http_client_request,
        mock_auth_response_with_impersonator,
        base_authentication_params,
    ):
        params = {"code": "test_code"}

        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_auth_response_with_impersonator, 200
        )

        response = self.user_management.authenticate_with_code(**params)

        assert request_kwargs["url"].endswith("user_management/authenticate")
        assert response.user.id == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        assert response.impersonator is not None
        assert response.impersonator.dict() == {
            "email": "admin@foocorp.com",
            "reason": "Debugging an account issue.",
        }
        assert request_kwargs["json"] == {
            **params,
            **base_authentication_params,
            "code_verifier": None,
            "ip_address": None,
            "user_agent": None,
            "grant_type": "authorization_code",
        }

    def test_authenticate_with_magic_auth(
        self,
        capture_and_mock_http_client_request,
        mock_auth_response,
        base_authentication_params,
    ):
        params = {
            "code": "test_auth",
            "email": "marcelina@foo-corp.com",
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "ip_address": "192.0.0.1",
        }

        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_auth_response, 200
        )

        response = self.user_management.authenticate_with_magic_auth(**params)

        assert request_kwargs["url"].endswith("user_management/authenticate")
        assert response.user.id == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        assert response.organization_id == "org_12345"
        assert response.access_token == "access_token_12345"
        assert response.refresh_token == "refresh_token_12345"
        assert request_kwargs["json"] == {
            **params,
            **base_authentication_params,
            "grant_type": "urn:workos:oauth:grant-type:magic-auth:code",
            "link_authorization_code": None,
        }

    def test_authenticate_with_email_verification(
        self,
        capture_and_mock_http_client_request,
        mock_auth_response,
        base_authentication_params,
    ):
        params = {
            "code": "test_auth",
            "pending_authentication_token": "ql1AJgNoLN1tb9llaQ8jyC2dn",
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "ip_address": "192.0.0.1",
        }

        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_auth_response, 200
        )

        response = self.user_management.authenticate_with_email_verification(**params)

        assert request_kwargs["url"].endswith("user_management/authenticate")
        assert response.user.id == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        assert response.organization_id == "org_12345"
        assert response.access_token == "access_token_12345"
        assert response.refresh_token == "refresh_token_12345"
        assert request_kwargs["json"] == {
            **params,
            **base_authentication_params,
            "grant_type": "urn:workos:oauth:grant-type:email-verification:code",
        }

    def test_authenticate_with_totp(
        self,
        capture_and_mock_http_client_request,
        mock_auth_response,
        base_authentication_params,
    ):
        params = {
            "code": "test_auth",
            "authentication_challenge_id": "auth_challenge_01FVYZWQTZQ5VB6BC5MPG2EYC5",
            "pending_authentication_token": "ql1AJgNoLN1tb9llaQ8jyC2dn",
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "ip_address": "192.0.0.1",
        }
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_auth_response, 200
        )

        response = self.user_management.authenticate_with_totp(**params)

        assert request_kwargs["url"].endswith("user_management/authenticate")
        assert response.user.id == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        assert response.organization_id == "org_12345"
        assert response.access_token == "access_token_12345"
        assert response.refresh_token == "refresh_token_12345"
        assert request_kwargs["json"] == {
            **params,
            **base_authentication_params,
            "grant_type": "urn:workos:oauth:grant-type:mfa-totp",
        }

    def test_authenticate_with_organization_selection(
        self,
        capture_and_mock_http_client_request,
        mock_auth_response,
        base_authentication_params,
    ):
        params = {
            "organization_id": "org_12345",
            "pending_authentication_token": "ql1AJgNoLN1tb9llaQ8jyC2dn",
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "ip_address": "192.0.0.1",
        }
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_auth_response, 200
        )

        response = self.user_management.authenticate_with_organization_selection(
            **params
        )

        assert request_kwargs["url"].endswith("user_management/authenticate")
        assert response.user.id == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        assert response.organization_id == "org_12345"
        assert response.access_token == "access_token_12345"
        assert response.refresh_token == "refresh_token_12345"
        assert request_kwargs["json"] == {
            **params,
            **base_authentication_params,
            "grant_type": "urn:workos:oauth:grant-type:organization-selection",
        }

    def test_authenticate_with_refresh_token(
        self,
        capture_and_mock_http_client_request,
        mock_auth_refresh_token_response,
        base_authentication_params,
    ):
        params = {
            "refresh_token": "refresh_token_98765",
            "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "ip_address": "192.0.0.1",
        }
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_auth_refresh_token_response, 200
        )

        response = self.user_management.authenticate_with_refresh_token(**params)

        assert request_kwargs["url"].endswith("user_management/authenticate")
        assert response.access_token == "access_token_12345"
        assert response.refresh_token == "refresh_token_12345"
        assert request_kwargs["json"] == {
            **params,
            **base_authentication_params,
            "organization_id": None,
            "grant_type": "refresh_token",
        }

    def test_get_jwks_url(self):
        expected = "%ssso/jwks/%s" % (workos.base_api_url, workos.client_id)
        result = self.user_management.get_jwks_url()

        assert expected == result

    def test_get_logout_url(self):
        expected = "%suser_management/sessions/logout?session_id=%s" % (
            workos.base_api_url,
            "session_123",
        )
        result = self.user_management.get_logout_url("session_123")

        assert expected == result

    def test_get_password_reset(
        self, mock_password_reset, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_password_reset, 200
        )

        password_reset = self.user_management.get_password_reset("password_reset_ABCDE")

        assert request_kwargs["url"].endswith(
            "user_management/password_reset/password_reset_ABCDE"
        )
        assert password_reset.id == "password_reset_ABCDE"

    def test_create_password_reset(
        self, capture_and_mock_http_client_request, mock_password_reset
    ):
        email = "marcelina@foo-corp.com"
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_password_reset, 201
        )

        password_reset = self.user_management.create_password_reset(email=email)

        assert request_kwargs["url"].endswith("user_management/password_reset")
        assert password_reset.email == email

    def test_reset_password(self, capture_and_mock_http_client_request, mock_user):
        params = {
            "token": "token123",
            "new_password": "pass123",
        }
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, {"user": mock_user}, 200
        )

        response = self.user_management.reset_password(**params)

        assert request_kwargs["url"].endswith("user_management/password_reset/confirm")
        assert response.id == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        assert request_kwargs["json"] == params

    def test_get_email_verification(
        self, mock_email_verification, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_email_verification, 200
        )

        email_verification = self.user_management.get_email_verification(
            "email_verification_ABCDE"
        )

        assert request_kwargs["url"].endswith(
            "user_management/email_verification/email_verification_ABCDE"
        )
        assert email_verification.id == "email_verification_ABCDE"

    def test_send_verification_email(
        self, capture_and_mock_http_client_request, mock_user
    ):
        user_id = "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"

        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, {"user": mock_user}, 200
        )

        response = self.user_management.send_verification_email(user_id=user_id)

        assert request_kwargs["url"].endswith(
            "user_management/users/user_01H7ZGXFP5C6BBQY6Z7277ZCT0/email_verification/send"
        )
        assert response.id == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"

    def test_verify_email(self, capture_and_mock_http_client_request, mock_user):
        user_id = "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        code = "code_123"

        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, {"user": mock_user}, 200
        )

        response = self.user_management.verify_email(user_id=user_id, code=code)

        assert request_kwargs["url"].endswith(
            "user_management/users/user_01H7ZGXFP5C6BBQY6Z7277ZCT0/email_verification/confirm"
        )
        assert request_kwargs["json"]["code"] == code
        assert response.id == "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"

    def test_get_magic_auth(
        self, mock_magic_auth, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_magic_auth, 200
        )

        magic_auth = self.user_management.get_magic_auth("magic_auth_ABCDE")

        assert request_kwargs["url"].endswith(
            "user_management/magic_auth/magic_auth_ABCDE"
        )
        assert magic_auth.id == "magic_auth_ABCDE"

    def test_create_magic_auth(
        self, capture_and_mock_http_client_request, mock_magic_auth
    ):
        email = "marcelina@foo-corp.com"
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_magic_auth, 201
        )

        magic_auth = self.user_management.create_magic_auth(email=email)

        assert request_kwargs["url"].endswith("user_management/magic_auth")
        assert magic_auth.email == email

    def test_enroll_auth_factor(
        self, mock_enroll_auth_factor_response, mock_http_client_with_response
    ):
        user_id = "user_01H7ZGXFP5C6BBQY6Z7277ZCT0"
        type = "totp"
        totp_issuer = "WorkOS"
        totp_user = "marcelina@foo-corp.com"
        totp_secret = "secret-test"

        mock_http_client_with_response(
            self.http_client, mock_enroll_auth_factor_response, 200
        )

        enroll_auth_factor = self.user_management.enroll_auth_factor(
            user_id=user_id,
            type=type,
            totp_issuer=totp_issuer,
            totp_user=totp_user,
            totp_secret=totp_secret,
        )

        assert enroll_auth_factor.dict() == mock_enroll_auth_factor_response

    def test_list_auth_factors_auto_pagination(
        self, mock_auth_factors_multiple_pages, test_sync_auto_pagination
    ):
        test_sync_auto_pagination(
            http_client=self.http_client,
            list_function=self.user_management.list_auth_factors,
            list_function_params={"user_id": "user_12345"},
            expected_all_page_data=mock_auth_factors_multiple_pages["data"],
        )

    def test_get_invitation(
        self, mock_invitation, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_invitation, 200
        )

        invitation = self.user_management.get_invitation("invitation_ABCDE")

        assert request_kwargs["url"].endswith(
            "user_management/invitations/invitation_ABCDE"
        )
        assert invitation.id == "invitation_ABCDE"

    def test_find_invitation_by_token(
        self, mock_invitation, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_invitation, 200
        )

        invitation = self.user_management.find_invitation_by_token(
            "Z1uX3RbwcIl5fIGJJJCXXisdI"
        )

        assert request_kwargs["url"].endswith(
            "user_management/invitations/by_token/Z1uX3RbwcIl5fIGJJJCXXisdI"
        )
        assert invitation.token == "Z1uX3RbwcIl5fIGJJJCXXisdI"

    def test_list_invitations_auto_pagination(
        self, mock_invitations_multiple_pages, test_sync_auto_pagination
    ):
        test_sync_auto_pagination(
            http_client=self.http_client,
            list_function=self.user_management.list_invitations,
            list_function_params={"organization_id": "org_12345"},
            expected_all_page_data=mock_invitations_multiple_pages["data"],
        )

    def test_send_invitation(
        self, capture_and_mock_http_client_request, mock_invitation
    ):
        email = "marcelina@foo-corp.com"
        organization_id = "org_12345"
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_invitation, 201
        )

        invitation = self.user_management.send_invitation(
            email=email, organization_id=organization_id
        )

        assert request_kwargs["url"].endswith("user_management/invitations")
        assert invitation.email == email
        assert invitation.organization_id == organization_id

    def test_revoke_invitation(
        self, capture_and_mock_http_client_request, mock_invitation
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_invitation, 200
        )

        self.user_management.revoke_invitation("invitation_ABCDE")

        assert request_kwargs["url"].endswith(
            "user_management/invitations/invitation_ABCDE/revoke"
        )
