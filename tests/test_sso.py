import json
from six.moves.urllib.parse import parse_qsl, urlparse
import pytest
from tests.utils.fixtures.mock_profile import MockProfile
from tests.utils.list_resource import list_data_to_dicts, list_response_of
from tests.utils.fixtures.mock_connection import MockConnection
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
            groups=None,
            raw_attributes={},
        ).dict()

    @pytest.fixture
    def mock_connection(self):
        return MockConnection("conn_01E4ZCR3C56J083X43JQXF3JK5").dict()

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


class TestSSO(SSOFixtures):
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
        self.state = json.dumps({"things": "with_stuff"})
        self.connection_id = "connection_123"
        self.organization_id = "organization_123"
        self.setup_completed = True

    def test_get_profile_and_token_returns_expected_profile_object(
        self, mock_profile, mock_http_client_with_response
    ):
        response_dict = {
            "profile": mock_profile,
            "access_token": "01DY34ACQTM3B1CSX1YSZ8Z00D",
        }

        mock_http_client_with_response(self.http_client, response_dict, 200)

        profile_and_token = self.sso.get_profile_and_token("123")

        assert profile_and_token.access_token == "01DY34ACQTM3B1CSX1YSZ8Z00D"
        assert profile_and_token.profile.dict() == mock_profile

    def test_get_profile_and_token_without_first_name_or_last_name_returns_expected_profile_object(
        self, mock_magic_link_profile, mock_http_client_with_response
    ):
        response_dict = {
            "profile": mock_magic_link_profile,
            "access_token": "01DY34ACQTM3B1CSX1YSZ8Z00D",
        }

        mock_http_client_with_response(self.http_client, response_dict, 200)

        profile_and_token = self.sso.get_profile_and_token("123")

        assert profile_and_token.access_token == "01DY34ACQTM3B1CSX1YSZ8Z00D"
        assert profile_and_token.profile.dict() == mock_magic_link_profile

    def test_get_profile(self, mock_profile, mock_http_client_with_response):
        mock_http_client_with_response(self.http_client, mock_profile, 200)

        profile = self.sso.get_profile("123")

        assert profile.dict() == mock_profile

    def test_get_connection(self, mock_connection, mock_http_client_with_response):
        mock_http_client_with_response(self.http_client, mock_connection, 200)

        connection = self.sso.get_connection(connection_id="connection_id")

        assert connection.dict() == mock_connection

    def test_list_connections(self, mock_connections, mock_http_client_with_response):
        mock_http_client_with_response(self.http_client, mock_connections, 200)

        connections = self.sso.list_connections()

        assert list_data_to_dicts(connections.data) == mock_connections["data"]

    def test_list_connections_with_connection_type(
        self, mock_connections, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            http_client=self.http_client,
            response_dict=mock_connections,
            status_code=200,
        )

        self.sso.list_connections(connection_type="GenericSAML")

        assert request_kwargs["params"] == {
            "connection_type": "GenericSAML",
            "limit": 10,
            "order": "desc",
        }

    def test_delete_connection(self, mock_http_client_with_response):
        mock_http_client_with_response(
            self.http_client,
            status_code=204,
            headers={"content-type": "text/plain; charset=utf-8"},
        )

        response = self.sso.delete_connection(connection_id="connection_id")

        assert response is None

    def test_list_connections_auto_pagination(
        self,
        mock_connections_multiple_data_pages,
        mock_pagination_request_for_http_client,
    ):
        mock_pagination_request_for_http_client(
            http_client=self.http_client,
            data_list=mock_connections_multiple_data_pages,
            status_code=200,
        )

        connections = self.sso.list_connections()
        all_connections = []

        for connection in connections:
            all_connections.append(connection)

        assert len(list(all_connections)) == len(mock_connections_multiple_data_pages)
        assert (
            list_data_to_dicts(all_connections)
        ) == mock_connections_multiple_data_pages


@pytest.mark.asyncio
class TestAsyncSSO(SSOFixtures):
    provider: SsoProviderType

    @pytest.fixture(autouse=True)
    def setup(self, async_client_configuration_and_http_client_for_test):
        client_configuration, http_client = (
            async_client_configuration_and_http_client_for_test
        )
        self.http_client = http_client
        self.sso = AsyncSSO(
            http_client=self.http_client, client_configuration=client_configuration
        )
        self.provider = "GoogleOAuth"
        self.customer_domain = "workos.com"
        self.login_hint = "foo@workos.com"
        self.redirect_uri = "https://localhost/auth/callback"
        self.state = json.dumps({"things": "with_stuff"})
        self.connection_id = "connection_123"
        self.organization_id = "organization_123"
        self.setup_completed = True

    async def test_get_profile_and_token_returns_expected_profile_object(
        self, mock_profile: Profile, mock_http_client_with_response
    ):
        response_dict = {
            "profile": mock_profile,
            "access_token": "01DY34ACQTM3B1CSX1YSZ8Z00D",
        }

        mock_http_client_with_response(self.http_client, response_dict, 200)

        profile_and_token = await self.sso.get_profile_and_token("123")

        assert profile_and_token.access_token == "01DY34ACQTM3B1CSX1YSZ8Z00D"
        assert profile_and_token.profile.dict() == mock_profile

    async def test_get_profile_and_token_without_first_name_or_last_name_returns_expected_profile_object(
        self, mock_magic_link_profile, mock_http_client_with_response
    ):
        response_dict = {
            "profile": mock_magic_link_profile,
            "access_token": "01DY34ACQTM3B1CSX1YSZ8Z00D",
        }

        mock_http_client_with_response(self.http_client, response_dict, 200)

        profile_and_token = await self.sso.get_profile_and_token("123")

        assert profile_and_token.access_token == "01DY34ACQTM3B1CSX1YSZ8Z00D"
        assert profile_and_token.profile.dict() == mock_magic_link_profile

    async def test_get_profile(self, mock_profile, mock_http_client_with_response):
        mock_http_client_with_response(self.http_client, mock_profile, 200)

        profile = await self.sso.get_profile("123")

        assert profile.dict() == mock_profile

    async def test_get_connection(
        self, mock_connection, mock_http_client_with_response
    ):
        mock_http_client_with_response(self.http_client, mock_connection, 200)

        connection = await self.sso.get_connection(connection_id="connection_id")

        assert connection.dict() == mock_connection

    async def test_list_connections(
        self, mock_connections, mock_http_client_with_response
    ):
        mock_http_client_with_response(self.http_client, mock_connections, 200)

        connections = await self.sso.list_connections()

        assert list_data_to_dicts(connections.data) == mock_connections["data"]

    async def test_list_connections_with_connection_type(
        self, mock_connections, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            http_client=self.http_client,
            response_dict=mock_connections,
            status_code=200,
        )

        await self.sso.list_connections(connection_type="GenericSAML")

        assert request_kwargs["params"] == {
            "connection_type": "GenericSAML",
            "limit": 10,
            "order": "desc",
        }

    async def test_delete_connection(self, mock_http_client_with_response):
        mock_http_client_with_response(
            self.http_client,
            status_code=204,
            headers={"content-type": "text/plain; charset=utf-8"},
        )

        response = await self.sso.delete_connection(connection_id="connection_id")

        assert response is None

    async def test_list_connections_auto_pagination(
        self,
        mock_connections_multiple_data_pages,
        mock_pagination_request_for_http_client,
    ):
        mock_pagination_request_for_http_client(
            http_client=self.http_client,
            data_list=mock_connections_multiple_data_pages,
            status_code=200,
        )

        connections = await self.sso.list_connections()
        all_connections = []

        async for connection in connections:
            all_connections.append(connection)

        assert len(list(all_connections)) == len(mock_connections_multiple_data_pages)
        assert (
            list_data_to_dicts(all_connections)
        ) == mock_connections_multiple_data_pages
