import json
from six.moves.urllib.parse import parse_qsl, urlparse
import pytest
import workos
from workos.sso import SSO
from workos.utils.connection_types import ConnectionType
from workos.utils.sso_provider_types import SsoProviderType
from workos.utils.request import RESPONSE_TYPE_CODE
from tests.utils.fixtures.mock_connection import MockConnection


class TestSSO(object):
    @pytest.fixture
    def setup_with_client_id(self, set_api_key_and_client_id):
        self.sso = SSO()
        self.provider = SsoProviderType.GoogleOAuth
        self.customer_domain = "workos.com"
        self.login_hint = "foo@workos.com"
        self.redirect_uri = "https://localhost/auth/callback"
        self.state = json.dumps({"things": "with_stuff"})
        self.connection = "connection_123"
        self.organization = "organization_123"
        self.setup_completed = True

    @pytest.fixture
    def mock_profile(self):
        return {
            "id": "prof_01DWAS7ZQWM70PV93BFV1V78QV",
            "email": "demo@workos-okta.com",
            "first_name": "WorkOS",
            "last_name": "Demo",
            "groups": ["Admins", "Developers"],
            "organization_id": "org_01FG53X8636WSNW2WEKB2C31ZB",
            "connection_id": "conn_01EMH8WAK20T42N2NBMNBCYHAG",
            "connection_type": "OktaSAML",
            "idp_id": "00u1klkowm8EGah2H357",
            "raw_attributes": {
                "email": "demo@workos-okta.com",
                "first_name": "WorkOS",
                "last_name": "Demo",
                "groups": ["Admins", "Developers"],
            },
        }

    @pytest.fixture
    def mock_magic_link_profile(self):
        return {
            "id": "prof_01DWAS7ZQWM70PV93BFV1V78QV",
            "email": "demo@workos-magic-link.com",
            "organization_id": None,
            "connection_id": "conn_01EMH8WAK20T42N2NBMNBCYHAG",
            "connection_type": "MagicLink",
            "idp_id": "",
            "first_name": None,
            "last_name": None,
            "groups": None,
            "raw_attributes": {},
        }

    @pytest.fixture
    def mock_connection(self):
        return MockConnection("conn_01E4ZCR3C56J083X43JQXF3JK5").to_dict()

    @pytest.fixture
    def mock_connections(self):
        connection_list = [MockConnection(id=str(i)).to_dict() for i in range(5000)]

        return {
            "data": connection_list,
            "list_metadata": {"before": None, "after": None},
            "metadata": {
                "params": {
                    "domains": None,
                    "limit": 4,
                    "before": None,
                    "after": None,
                    "order": None,
                    "default_limit": True,
                },
                "method": SSO.list_connections,
            },
        }

    @pytest.fixture
    def mock_connections_with_limit(self):
        connection_list = [MockConnection(id=str(i)).to_dict() for i in range(4)]

        return {
            "data": connection_list,
            "list_metadata": {"before": None, "after": None},
            "metadata": {
                "params": {
                    "connection_type": None,
                    "domain": None,
                    "organization_id": None,
                    "limit": 4,
                    "before": None,
                    "after": None,
                    "order": None,
                },
                "method": SSO.list_connections,
            },
        }

    @pytest.fixture
    def mock_connections_with_limit_v2(self, set_api_key_and_client_id):
        connection_list = [MockConnection(id=str(i)).to_dict() for i in range(4)]

        dict_response = {
            "data": connection_list,
            "list_metadata": {"before": None, "after": None},
            "metadata": {
                "params": {
                    "connection_type": None,
                    "domain": None,
                    "organization_id": None,
                    "limit": 4,
                    "before": None,
                    "after": None,
                    "order": None,
                },
                "method": SSO.list_connections_v2,
            },
        }
        return SSO.construct_from_response(dict_response)

    @pytest.fixture
    def mock_connections_with_default_limit(self):
        connection_list = [MockConnection(id=str(i)).to_dict() for i in range(10)]

        return {
            "data": connection_list,
            "list_metadata": {"before": None, "after": "conn_xxx"},
            "metadata": {
                "params": {
                    "connection_type": None,
                    "domain": None,
                    "organization_id": None,
                    "limit": 4,
                    "before": None,
                    "after": None,
                    "order": None,
                    "default_limit": True,
                },
                "method": SSO.list_connections,
            },
        }

    @pytest.fixture
    def mock_connections_with_default_limit_v2(self, setup_with_client_id):
        connection_list = [MockConnection(id=str(i)).to_dict() for i in range(10)]

        dict_response = {
            "data": connection_list,
            "list_metadata": {"before": None, "after": "conn_xxx"},
            "metadata": {
                "params": {
                    "connection_type": None,
                    "domain": None,
                    "organization_id": None,
                    "limit": 4,
                    "before": None,
                    "after": None,
                    "order": None,
                    "default_limit": True,
                },
                "method": SSO.list_connections_v2,
            },
        }
        return self.sso.construct_from_response(dict_response)

    @pytest.fixture
    def mock_connections_pagination_response(self):
        connection_list = [MockConnection(id=str(i)).to_dict() for i in range(4990)]

        return {
            "data": connection_list,
            "list_metadata": {"before": None, "after": None},
            "metadata": {
                "params": {
                    "connection_type": None,
                    "domain": None,
                    "organization_id": None,
                    "limit": None,
                    "before": None,
                    "after": None,
                    "order": None,
                    "default_limit": True,
                },
                "method": SSO.list_connections,
            },
        }

    def test_authorization_url_throws_value_error_with_missing_connection_domain_and_provider(
        self, setup_with_client_id
    ):
        with pytest.raises(ValueError, match=r"Incomplete arguments.*"):
            self.sso.get_authorization_url(
                redirect_uri=self.redirect_uri, state=self.state
            )

    @pytest.mark.parametrize(
        "invalid_provider",
        [
            123,
            SsoProviderType,
            True,
            False,
            {"provider": "GoogleOAuth"},
            ["GoogleOAuth"],
        ],
    )
    def test_authorization_url_throws_value_error_with_incorrect_provider_type(
        self, setup_with_client_id, invalid_provider
    ):
        with pytest.raises(
            ValueError, match="'provider' must be of type SsoProviderType"
        ):
            self.sso.get_authorization_url(
                provider=invalid_provider,
                redirect_uri=self.redirect_uri,
                state=self.state,
            )

    def test_authorization_url_throws_value_error_without_redirect_uri(
        self, setup_with_client_id
    ):
        with pytest.raises(
            ValueError, match="Incomplete arguments. Need to specify a 'redirect_uri'."
        ):
            self.sso.get_authorization_url(
                connection=self.connection,
                login_hint=self.login_hint,
                state=self.state,
            )

    def test_authorization_url_has_expected_query_params_with_provider(
        self, setup_with_client_id
    ):
        authorization_url = self.sso.get_authorization_url(
            provider=self.provider, redirect_uri=self.redirect_uri, state=self.state
        )

        parsed_url = urlparse(authorization_url)

        assert dict(parse_qsl(parsed_url.query)) == {
            "provider": str(self.provider.value),
            "client_id": workos.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": RESPONSE_TYPE_CODE,
            "state": self.state,
        }

    def test_authorization_url_has_expected_query_params_with_domain(
        self, setup_with_client_id
    ):
        authorization_url = self.sso.get_authorization_url(
            domain=self.customer_domain,
            redirect_uri=self.redirect_uri,
            state=self.state,
        )

        parsed_url = urlparse(authorization_url)

        assert dict(parse_qsl(parsed_url.query)) == {
            "domain": self.customer_domain,
            "client_id": workos.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": RESPONSE_TYPE_CODE,
            "state": self.state,
        }

    def test_authorization_url_has_expected_query_params_with_domain_hint(
        self, setup_with_client_id
    ):
        authorization_url = self.sso.get_authorization_url(
            connection=self.connection,
            domain_hint=self.customer_domain,
            redirect_uri=self.redirect_uri,
            state=self.state,
        )

        parsed_url = urlparse(authorization_url)

        assert dict(parse_qsl(parsed_url.query)) == {
            "domain_hint": self.customer_domain,
            "client_id": workos.client_id,
            "redirect_uri": self.redirect_uri,
            "connection": self.connection,
            "response_type": RESPONSE_TYPE_CODE,
            "state": self.state,
        }

    def test_authorization_url_has_expected_query_params_with_login_hint(
        self, setup_with_client_id
    ):
        authorization_url = self.sso.get_authorization_url(
            connection=self.connection,
            login_hint=self.login_hint,
            redirect_uri=self.redirect_uri,
            state=self.state,
        )

        parsed_url = urlparse(authorization_url)

        assert dict(parse_qsl(parsed_url.query)) == {
            "login_hint": self.login_hint,
            "client_id": workos.client_id,
            "redirect_uri": self.redirect_uri,
            "connection": self.connection,
            "response_type": RESPONSE_TYPE_CODE,
            "state": self.state,
        }

    def test_authorization_url_has_expected_query_params_with_connection(
        self, setup_with_client_id
    ):
        authorization_url = self.sso.get_authorization_url(
            connection=self.connection,
            redirect_uri=self.redirect_uri,
            state=self.state,
        )

        parsed_url = urlparse(authorization_url)

        assert dict(parse_qsl(parsed_url.query)) == {
            "connection": self.connection,
            "client_id": workos.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": RESPONSE_TYPE_CODE,
            "state": self.state,
        }

    def test_authorization_url_with_string_provider_has_expected_query_params_with_organization(
        self, setup_with_client_id
    ):
        authorization_url = self.sso.get_authorization_url(
            provider=self.provider,
            organization=self.organization,
            redirect_uri=self.redirect_uri,
            state=self.state,
        )

        parsed_url = urlparse(authorization_url)

        assert dict(parse_qsl(parsed_url.query)) == {
            "organization": self.organization,
            "provider": self.provider.value,
            "client_id": workos.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": RESPONSE_TYPE_CODE,
            "state": self.state,
        }

    def test_authorization_url_has_expected_query_params_with_organization(
        self, setup_with_client_id
    ):
        authorization_url = self.sso.get_authorization_url(
            organization=self.organization,
            redirect_uri=self.redirect_uri,
            state=self.state,
        )

        parsed_url = urlparse(authorization_url)

        assert dict(parse_qsl(parsed_url.query)) == {
            "organization": self.organization,
            "client_id": workos.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": RESPONSE_TYPE_CODE,
            "state": self.state,
        }

    def test_authorization_url_has_expected_query_params_with_domain_and_provider(
        self, setup_with_client_id
    ):
        authorization_url = self.sso.get_authorization_url(
            domain=self.customer_domain,
            provider=self.provider,
            redirect_uri=self.redirect_uri,
            state=self.state,
        )

        parsed_url = urlparse(authorization_url)

        assert dict(parse_qsl(parsed_url.query)) == {
            "domain": self.customer_domain,
            "provider": str(self.provider.value),
            "client_id": workos.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": RESPONSE_TYPE_CODE,
            "state": self.state,
        }

    def test_get_profile_and_token_returns_expected_workosprofile_object(
        self, setup_with_client_id, mock_profile, mock_request_method
    ):
        response_dict = {
            "profile": {
                "object": "profile",
                "id": mock_profile["id"],
                "email": mock_profile["email"],
                "first_name": mock_profile["first_name"],
                "groups": mock_profile["groups"],
                "organization_id": mock_profile["organization_id"],
                "connection_id": mock_profile["connection_id"],
                "connection_type": mock_profile["connection_type"],
                "last_name": mock_profile["last_name"],
                "idp_id": mock_profile["idp_id"],
                "raw_attributes": {
                    "email": mock_profile["raw_attributes"]["email"],
                    "first_name": mock_profile["raw_attributes"]["first_name"],
                    "last_name": mock_profile["raw_attributes"]["last_name"],
                    "groups": mock_profile["raw_attributes"]["groups"],
                },
            },
            "access_token": "01DY34ACQTM3B1CSX1YSZ8Z00D",
        }

        mock_request_method("post", response_dict, 200)

        profile_and_token = self.sso.get_profile_and_token(123)

        assert profile_and_token.access_token == "01DY34ACQTM3B1CSX1YSZ8Z00D"
        assert profile_and_token.profile.to_dict() == mock_profile

    def test_get_profile_and_token_without_first_name_or_last_name_returns_expected_workosprofile_object(
        self, setup_with_client_id, mock_magic_link_profile, mock_request_method
    ):
        response_dict = {
            "profile": {
                "object": "profile",
                "id": mock_magic_link_profile["id"],
                "email": mock_magic_link_profile["email"],
                "organization_id": mock_magic_link_profile["organization_id"],
                "connection_id": mock_magic_link_profile["connection_id"],
                "connection_type": mock_magic_link_profile["connection_type"],
                "idp_id": "",
                "raw_attributes": {},
            },
            "access_token": "01DY34ACQTM3B1CSX1YSZ8Z00D",
        }

        mock_request_method("post", response_dict, 200)

        profile_and_token = self.sso.get_profile_and_token(123)

        assert profile_and_token.access_token == "01DY34ACQTM3B1CSX1YSZ8Z00D"
        assert profile_and_token.profile.to_dict() == mock_magic_link_profile

    def test_get_profile(self, setup_with_client_id, mock_profile, mock_request_method):
        mock_request_method("get", mock_profile, 200)

        profile = self.sso.get_profile(123)

        assert profile.to_dict() == mock_profile

    def test_get_connection(
        self, setup_with_client_id, mock_connection, mock_request_method
    ):
        mock_request_method("get", mock_connection, 200)

        connection = self.sso.get_connection(connection="connection_id")

        assert connection == mock_connection

    def test_list_connections(
        self, setup_with_client_id, mock_connections, mock_request_method
    ):
        mock_request_method("get", mock_connections, 200)

        connections_response = self.sso.list_connections()

        assert connections_response["data"] == mock_connections["data"]

    def test_list_connections_with_connection_type_as_invalid_string(
        self, setup_with_client_id, mock_connections, mock_request_method
    ):
        mock_request_method("get", mock_connections, 200)

        with pytest.raises(
            ValueError, match="'connection_type' must be a member of ConnectionType"
        ):
            self.sso.list_connections(connection_type="UnknownSAML")

    def test_list_connections_with_connection_type_as_string(
        self, setup_with_client_id, mock_connections, capture_and_mock_request
    ):
        request_args, request_kwargs = capture_and_mock_request(
            "get", mock_connections, 200
        )

        connections_response = self.sso.list_connections(connection_type="GenericSAML")

        request_params = request_kwargs["params"]
        assert request_params["connection_type"] == "GenericSAML"

    def test_list_connections_with_connection_type_as_enum(
        self, setup_with_client_id, mock_connections, capture_and_mock_request
    ):
        request_args, request_kwargs = capture_and_mock_request(
            "get", mock_connections, 200
        )

        connections_response = self.sso.list_connections(
            connection_type=ConnectionType.OktaSAML
        )

        request_params = request_kwargs["params"]
        assert request_params["connection_type"] == "OktaSAML"

    def test_delete_connection(self, setup_with_client_id, mock_raw_request_method):
        mock_raw_request_method(
            "delete",
            "No Content",
            204,
            headers={"content-type": "text/plain; charset=utf-8"},
        )

        response = self.sso.delete_connection(connection="connection_id")

        assert response is None

    def test_list_connections_auto_pagination(
        self,
        mock_connections_with_default_limit,
        mock_connections_pagination_response,
        mock_connections,
        mock_request_method,
        setup_with_client_id,
    ):
        mock_request_method("get", mock_connections_pagination_response, 200)
        connections = mock_connections_with_default_limit

        all_connections = SSO.construct_from_response(connections).auto_paging_iter()

        assert len(*list(all_connections)) == len(mock_connections["data"])

    def test_list_connections_auto_pagination_v2(
        self,
        mock_connections_with_default_limit_v2,
        mock_connections_pagination_response,
        mock_connections,
        mock_request_method,
        setup_with_client_id,
    ):
        connections = mock_connections_with_default_limit_v2

        mock_request_method("get", mock_connections_pagination_response, 200)
        all_connections = connections.auto_paging_iter()

        number_of_connections = len(*list(all_connections))
        assert number_of_connections == len(mock_connections["data"])

    def test_list_connections_honors_limit(
        self,
        mock_connections_with_limit,
        mock_connections_pagination_response,
        mock_request_method,
        setup_with_client_id,
    ):
        connections = mock_connections_with_limit
        mock_request_method("get", mock_connections_pagination_response, 200)
        all_connections = SSO.construct_from_response(connections).auto_paging_iter()

        assert len(*list(all_connections)) == len(mock_connections_with_limit["data"])

    def test_list_connections_honors_limit_v2(
        self,
        mock_connections_with_limit_v2,
        mock_connections_pagination_response,
        mock_request_method,
        setup_with_client_id,
    ):
        connections = mock_connections_with_limit_v2
        mock_request_method("get", mock_connections_pagination_response, 200)
        all_connections = connections.auto_paging_iter()
        dict_mock_connections_with_limit = mock_connections_with_limit_v2.to_dict()

        assert len(*list(all_connections)) == len(
            dict_mock_connections_with_limit["data"]
        )

    def test_list_connections_returns_metadata(
        self,
        mock_connections,
        mock_request_method,
        setup_with_client_id,
    ):
        mock_request_method("get", mock_connections, 200)
        connections = self.sso.list_connections(domain="planet-express.com")

        assert connections["metadata"]["params"]["domain"] == "planet-express.com"

    def test_list_connections_returns_metadata_v2(
        self,
        mock_connections,
        mock_request_method,
        setup_with_client_id,
    ):
        mock_request_method("get", mock_connections, 200)

        connections = self.sso.list_connections_v2(domain="planet-express.com")
        dict_connections = connections.to_dict()

        assert dict_connections["metadata"]["params"]["domain"] == "planet-express.com"
