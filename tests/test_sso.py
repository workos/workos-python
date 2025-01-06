import json
from typing import Union
from six.moves.urllib.parse import parse_qsl, urlparse
import pytest
from tests.types.test_auto_pagination_function import TestAutoPaginationFunction
from tests.utils.fixtures.mock_profile import MockProfile
from tests.utils.list_resource import list_data_to_dicts, list_response_of
from tests.utils.fixtures.mock_connection import MockConnection
from tests.utils.syncify import syncify
from workos.sso import SSO, AsyncSSO, SsoProviderType
from workos.types.sso import Profile
from workos.utils.request_helper import RESPONSE_TYPE_CODE


class SSOFixtures:
    @pytest.fixture
    def mock_profile(self):
        return MockProfile("prof_01DWAS7ZQWM70PV93BFV1V78QV").dict()

    @pytest.fixture
    def mock_magic_link_profile(self):
        return Profile(
            object="profile",
            id="prof_01DWAS7ZQWM70PV93BFV1V78QV",
            email="demo@workos-magic-link.com",
            organization_id=None,
            connection_id="conn_01EMH8WAK20T42N2NBMNBCYHAG",
            connection_type="MagicLink",
            idp_id="",
            first_name=None,
            last_name=None,
            profile=None,
            groups=None,
            raw_attributes={},
        ).dict()

    @pytest.fixture
    def mock_connection(self):
        return MockConnection("conn_01E4ZCR3C56J083X43JQXF3JK5").dict()

    @pytest.fixture
    def mock_connection_updated(self):
        connection = MockConnection("conn_01FHT48Z8J8295GZNQ4ZP1J81T").dict()

        connection["options"] = {
            "signing_cert": "signing_cert",
        }

        return connection

    @pytest.fixture
    def mock_connections(self):
        connection_list = [MockConnection(id=str(i)).dict() for i in range(10)]

        return list_response_of(data=connection_list)

    @pytest.fixture
    def mock_connections_multiple_data_pages(self):
        return [MockConnection(id=str(i)).dict() for i in range(40)]


class TestSSOBase(SSOFixtures):
    provider: SsoProviderType

    @pytest.fixture(autouse=True)
    def setup(self, sync_client_configuration_and_http_client_for_test):
        client_configuration, http_client = (
            sync_client_configuration_and_http_client_for_test
        )
        self.http_client = http_client
        self.sso = SSO(
            http_client=self.http_client, client_configuration=client_configuration
        )
        self.provider = "GoogleOAuth"
        self.customer_domain = "workos.com"
        self.login_hint = "foo@workos.com"
        self.redirect_uri = "https://localhost/auth/callback"
        self.authorization_state = json.dumps({"things": "with_stuff"})
        self.connection_id = "connection_123"
        self.organization_id = "organization_123"
        self.setup_completed = True

    def test_authorization_url_throws_value_error_with_missing_connection_organization_and_provider(
        self,
    ):
        with pytest.raises(ValueError, match=r"Incomplete arguments.*"):
            self.sso.get_authorization_url(
                redirect_uri=self.redirect_uri, state=self.authorization_state
            )

    def test_authorization_url_has_expected_query_params_with_provider(self):
        authorization_url = self.sso.get_authorization_url(
            provider=self.provider,
            redirect_uri=self.redirect_uri,
            state=self.authorization_state,
        )

        parsed_url = urlparse(authorization_url)

        assert parsed_url.path == "/sso/authorize"
        assert dict(parse_qsl(parsed_url.query)) == {
            "provider": self.provider,
            "client_id": self.http_client.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": RESPONSE_TYPE_CODE,
            "state": self.authorization_state,
        }

    def test_authorization_url_has_expected_query_params_with_domain_hint(self):
        authorization_url = self.sso.get_authorization_url(
            connection_id=self.connection_id,
            domain_hint=self.customer_domain,
            redirect_uri=self.redirect_uri,
            state=self.authorization_state,
        )

        parsed_url = urlparse(authorization_url)

        assert parsed_url.path == "/sso/authorize"
        assert dict(parse_qsl(parsed_url.query)) == {
            "domain_hint": self.customer_domain,
            "client_id": self.http_client.client_id,
            "redirect_uri": self.redirect_uri,
            "connection": self.connection_id,
            "response_type": RESPONSE_TYPE_CODE,
            "state": self.authorization_state,
        }

    def test_authorization_url_has_expected_query_params_with_login_hint(self):
        authorization_url = self.sso.get_authorization_url(
            connection_id=self.connection_id,
            login_hint=self.login_hint,
            redirect_uri=self.redirect_uri,
            state=self.authorization_state,
        )

        parsed_url = urlparse(authorization_url)

        assert parsed_url.path == "/sso/authorize"
        assert dict(parse_qsl(parsed_url.query)) == {
            "login_hint": self.login_hint,
            "client_id": self.http_client.client_id,
            "redirect_uri": self.redirect_uri,
            "connection": self.connection_id,
            "response_type": RESPONSE_TYPE_CODE,
            "state": self.authorization_state,
        }

    def test_authorization_url_has_expected_query_params_with_connection(self):
        authorization_url = self.sso.get_authorization_url(
            connection_id=self.connection_id,
            redirect_uri=self.redirect_uri,
            state=self.authorization_state,
        )

        parsed_url = urlparse(authorization_url)

        assert parsed_url.path == "/sso/authorize"
        assert dict(parse_qsl(parsed_url.query)) == {
            "connection": self.connection_id,
            "client_id": self.http_client.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": RESPONSE_TYPE_CODE,
            "state": self.authorization_state,
        }

    def test_authorization_url_with_string_provider_has_expected_query_params_with_organization(
        self,
    ):
        authorization_url = self.sso.get_authorization_url(
            provider=self.provider,
            organization_id=self.organization_id,
            redirect_uri=self.redirect_uri,
            state=self.authorization_state,
        )

        parsed_url = urlparse(authorization_url)

        assert parsed_url.path == "/sso/authorize"
        assert dict(parse_qsl(parsed_url.query)) == {
            "organization": self.organization_id,
            "provider": self.provider,
            "client_id": self.http_client.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": RESPONSE_TYPE_CODE,
            "state": self.authorization_state,
        }

    def test_authorization_url_has_expected_query_params_with_organization(self):
        authorization_url = self.sso.get_authorization_url(
            organization_id=self.organization_id,
            redirect_uri=self.redirect_uri,
            state=self.authorization_state,
        )

        parsed_url = urlparse(authorization_url)

        assert parsed_url.path == "/sso/authorize"
        assert dict(parse_qsl(parsed_url.query)) == {
            "organization": self.organization_id,
            "client_id": self.http_client.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": RESPONSE_TYPE_CODE,
            "state": self.authorization_state,
        }

    def test_authorization_url_has_expected_query_params_with_organization_and_provider(
        self,
    ):
        authorization_url = self.sso.get_authorization_url(
            organization_id=self.organization_id,
            provider=self.provider,
            redirect_uri=self.redirect_uri,
            state=self.authorization_state,
        )

        parsed_url = urlparse(authorization_url)

        assert parsed_url.path == "/sso/authorize"
        assert dict(parse_qsl(parsed_url.query)) == {
            "organization": self.organization_id,
            "provider": self.provider,
            "client_id": self.http_client.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": RESPONSE_TYPE_CODE,
            "state": self.authorization_state,
        }


@pytest.mark.sync_and_async(SSO, AsyncSSO)
class TestSSO(SSOFixtures):
    provider: SsoProviderType

    @pytest.fixture(autouse=True)
    def setup(self, module_instance: Union[SSO, AsyncSSO]):
        self.http_client = module_instance._http_client
        self.sso = module_instance
        self.provider = "GoogleOAuth"
        self.customer_domain = "workos.com"
        self.login_hint = "foo@workos.com"
        self.redirect_uri = "https://localhost/auth/callback"
        self.state = json.dumps({"things": "with_stuff"})
        self.connection_id = "connection_123"
        self.organization_id = "organization_123"
        self.setup_completed = True

    def test_get_profile_and_token_returns_expected_profile_object(
        self, mock_profile, capture_and_mock_http_client_request
    ):
        response_dict = {
            "profile": mock_profile,
            "access_token": "01DY34ACQTM3B1CSX1YSZ8Z00D",
        }

        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, response_dict, 200
        )

        profile_and_token = syncify(self.sso.get_profile_and_token("123"))

        assert profile_and_token.access_token == "01DY34ACQTM3B1CSX1YSZ8Z00D"
        assert profile_and_token.profile.dict() == mock_profile
        assert request_kwargs["url"].endswith("/sso/token")
        assert request_kwargs["method"] == "post"
        assert request_kwargs["json"] == {
            "client_id": "client_b27needthisforssotemxo",
            "client_secret": "sk_test",
            "code": "123",
            "grant_type": "authorization_code",
        }

    def test_get_profile_and_token_without_first_name_or_last_name_returns_expected_profile_object(
        self, mock_magic_link_profile, capture_and_mock_http_client_request
    ):
        response_dict = {
            "profile": mock_magic_link_profile,
            "access_token": "01DY34ACQTM3B1CSX1YSZ8Z00D",
        }

        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, response_dict, 200
        )

        profile_and_token = syncify(self.sso.get_profile_and_token("123"))

        assert profile_and_token.access_token == "01DY34ACQTM3B1CSX1YSZ8Z00D"
        assert profile_and_token.profile.dict() == mock_magic_link_profile
        assert request_kwargs["url"].endswith("/sso/token")
        assert request_kwargs["method"] == "post"
        assert request_kwargs["json"] == {
            "client_id": "client_b27needthisforssotemxo",
            "client_secret": "sk_test",
            "code": "123",
            "grant_type": "authorization_code",
        }

    def test_get_profile(self, mock_profile, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_profile, 200
        )

        profile = syncify(self.sso.get_profile("123"))

        assert profile.dict() == mock_profile
        assert request_kwargs["url"].endswith("/sso/profile")
        assert request_kwargs["method"] == "get"
        assert request_kwargs["headers"]["authorization"] == "Bearer 123"

    def test_get_connection(
        self, mock_connection, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_connection, 200
        )

        connection = syncify(self.sso.get_connection(connection_id="connection_id"))

        assert connection.dict() == mock_connection
        assert request_kwargs["url"].endswith("/connections/connection_id")
        assert request_kwargs["method"] == "get"

    def test_list_connections(
        self, mock_connections, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_connections, 200
        )

        connections = syncify(self.sso.list_connections())

        assert list_data_to_dicts(connections.data) == mock_connections["data"]
        assert request_kwargs["url"].endswith("/connections")
        assert request_kwargs["method"] == "get"

    def test_list_connections_with_connection_type(
        self, mock_connections, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            http_client=self.http_client,
            response_dict=mock_connections,
            status_code=200,
        )

        syncify(self.sso.list_connections(connection_type="GenericSAML"))

        assert request_kwargs["params"] == {
            "connection_type": "GenericSAML",
            "limit": 10,
            "order": "desc",
        }

    def test_update_connection(
        self, mock_connection_updated, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_connection_updated, 200
        )

        updated_connection = syncify(
            self.sso.update_connection(
                connection_id="conn_01EHT88Z8J8795GZNQ4ZP1J81T",
                saml_options_signing_key="signing_key",
                saml_options_signing_cert="signing_cert",
            )
        )

        assert request_kwargs["url"].endswith(
            "/connections/conn_01EHT88Z8J8795GZNQ4ZP1J81T"
        )

        assert request_kwargs["method"] == "put"
        assert request_kwargs["json"] == {
            "options": {"signing_key": "signing_key", "signing_cert": "signing_cert"}
        }
        assert updated_connection.id == "conn_01FHT48Z8J8295GZNQ4ZP1J81T"
        assert updated_connection.name == "Foo Corporation"
        assert updated_connection.options.signing_cert == "signing_cert"

    def test_delete_connection(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client,
            status_code=204,
            headers={"content-type": "text/plain; charset=utf-8"},
        )

        response = syncify(self.sso.delete_connection(connection_id="connection_id"))

        assert request_kwargs["url"].endswith("/connections/connection_id")
        assert request_kwargs["method"] == "delete"
        assert response is None

    def test_list_connections_auto_pagination(
        self,
        mock_connections_multiple_data_pages,
        test_auto_pagination: TestAutoPaginationFunction,
    ):
        test_auto_pagination(
            http_client=self.http_client,
            list_function=self.sso.list_connections,
            expected_all_page_data=mock_connections_multiple_data_pages,
        )
