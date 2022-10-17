import json
from six.moves.urllib.parse import parse_qsl, urlparse
import pytest
import workos
from workos.sso import SSO
from workos.utils.connection_types import ConnectionType
from workos.utils.request import RESPONSE_TYPE_CODE
from workos.resources.sso import WorkOSProfile, WorkOSProfileAndToken, WorkOSConnection


class TestSSO(object):
    @pytest.fixture
    def setup_with_client_id(self, set_api_key_and_client_id):
        self.provider = ConnectionType.GoogleOAuth
        self.customer_domain = "workos.com"
        self.login_hint = "foo@workos.com"
        self.redirect_uri = "https://localhost/auth/callback"
        self.state = json.dumps({"things": "with_stuff"})
        self.connection = "connection_123"
        self.organization = "organization_123"

        self.sso = SSO()

    @pytest.fixture
    def mock_profile(self):
        return {
            "id": "prof_01DWAS7ZQWM70PV93BFV1V78QV",
            "email": "demo@workos-okta.com",
            "first_name": "WorkOS",
            "last_name": "Demo",
            "organization_id": "org_01FG53X8636WSNW2WEKB2C31ZB",
            "connection_id": "conn_01EMH8WAK20T42N2NBMNBCYHAG",
            "connection_type": "OktaSAML",
            "idp_id": "00u1klkowm8EGah2H357",
            "raw_attributes": {
                "email": "demo@workos-okta.com",
                "first_name": "WorkOS",
                "last_name": "Demo",
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
            "raw_attributes": {},
        }

    @pytest.fixture
    def mock_connection(self):
        return {
            "object": "connection",
            "id": "conn_01E4ZCR3C56J083X43JQXF3JK5",
            "organization_id": "org_01EHWNCE74X7JSDV0X3SZ3KJNY",
            "connection_type": "GoogleOAuth",
            "name": "Foo Corp",
            "state": "active",
            "status": "none",
            "created_at": "2021-06-25T19:07:33.155Z",
            "updated_at": "2021-06-25T19:07:33.155Z",
            "domains": [
                {
                    "id": "conn_domain_01EHWNFTAFCF3CQAE5A9Q0P1YB",
                    "object": "connection_domain",
                    "domain": "foo-corp.com",
                }
            ],
        }

    @pytest.fixture
    def mock_connections(self):
        return {
            "data": [
                {
                    "object": "connection",
                    "id": "conn_01E4ZCR3C56J083X43JQXF3JK5",
                    "organization_id": "org_01EHWNCE74X7JSDV0X3SZ3KJNY",
                    "connection_type": "GoogleOAuth",
                    "name": "Foo Corp",
                    "state": "active",
                    "created_at": "2021-06-25T19:07:33.155Z",
                    "updated_at": "2021-06-25T19:07:33.155Z",
                    "domains": [
                        {
                            "id": "conn_domain_01EHWNFTAFCF3CQAE5A9Q0P1YB",
                            "object": "connection_domain",
                            "domain": "foo-corp.com",
                        }
                    ],
                }
            ],
            "list_metadata": {"before": None, "after": None},
        }

    def test_authorization_url_throws_value_error_with_missing_connection_domain_and_provider(
        self, setup_with_client_id
    ):
        with pytest.raises(ValueError, match=r"Incomplete arguments.*"):
            self.sso.get_authorization_url(
                redirect_uri=self.redirect_uri, state=self.state
            )

    def test_authorization_url_throws_value_error_with_incorrect_provider_type(
        self, setup_with_client_id
    ):
        with pytest.raises(
            ValueError, match="'provider' must be of type ConnectionType"
        ):
            self.sso.get_authorization_url(
                provider="foo", redirect_uri=self.redirect_uri, state=self.state
            )

    def test_authorization_url_throws_value_error_wihout_redirect_uri(
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
                "organization_id": mock_profile["organization_id"],
                "connection_id": mock_profile["connection_id"],
                "connection_type": mock_profile["connection_type"],
                "last_name": mock_profile["last_name"],
                "idp_id": mock_profile["idp_id"],
                "raw_attributes": {
                    "email": mock_profile["raw_attributes"]["email"],
                    "first_name": mock_profile["raw_attributes"]["first_name"],
                    "last_name": mock_profile["raw_attributes"]["last_name"],
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
