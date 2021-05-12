import json
from requests import Response
from six.moves.urllib.parse import parse_qsl, urlparse

import pytest

import workos
from workos.sso import SSO
from workos.utils.connection_types import ConnectionType
from workos.utils.request import RESPONSE_TYPE_CODE


class TestSSO(object):
    @pytest.fixture
    def setup_with_client_id(self, set_api_key_and_client_id):
        self.provider = ConnectionType.GoogleOAuth
        self.customer_domain = "workos.com"
        self.redirect_uri = "https://localhost/auth/callback"
        self.state = json.dumps({"things": "with_stuff"})
        self.connection = "connection_123"

        self.sso = SSO()

    @pytest.fixture
    def setup_with_client_id(self, set_api_key_and_client_id):
        self.provider = ConnectionType.GoogleOAuth
        self.customer_domain = "workos.com"
        self.redirect_uri = "https://localhost/auth/callback"
        self.state = json.dumps({"things": "with_stuff"})

        self.sso = SSO()

    @pytest.fixture
    def mock_profile(self):
        return {
            "id": "prof_01DWAS7ZQWM70PV93BFV1V78QV",
            "email": "demo@workos-okta.com",
            "first_name": "WorkOS",
            "last_name": "Demo",
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
    def mock_connection(self):
        return {
            "object": "connection",
            "id": "conn_id",
            "status": "linked",
            "name": "Google OAuth 2.0",
            "connection_type": "GoogleOAuth",
            "oauth_uid": "oauth-uid.apps.googleusercontent.com",
            "oauth_secret": "oauth-secret",
            "oauth_redirect_uri": "https://auth.workos.com/sso/oauth/google/chicken/callback",
            "saml_entity_id": None,
            "saml_idp_url": None,
            "saml_relying_party_trust_cert": None,
            "saml_x509_certs": None,
            "domains": [
                {
                    "object": "connection_domain",
                    "id": "domain_id",
                    "domain": "terrace-house.com",
                },
            ],
        }

    @pytest.fixture
    def mock_connections(self):
        return {
            "data": [
                {
                    "object": "connection",
                    "id": "conn_id",
                    "status": "linked",
                    "name": "Google OAuth 2.0",
                    "connection_type": "GoogleOAuth",
                    "oauth_uid": "oauth-uid.apps.googleusercontent.com",
                    "oauth_secret": "oauth-secret",
                    "oauth_redirect_uri": "https://auth.workos.com/sso/oauth/google/chicken/callback",
                    "saml_entity_id": None,
                    "saml_idp_url": None,
                    "saml_relying_party_trust_cert": None,
                    "saml_x509_certs": None,
                    "domains": [
                        {
                            "object": "connection_domain",
                            "id": "domain_id",
                            "domain": "terrace-house.com",
                        },
                    ],
                }
            ],
            "listMetadata": {"before": None, "after": None},
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

    def test_get_profile_returns_expected_workosprofile_object(
        self, setup_with_client_id, mock_profile, mock_request_method
    ):
        response_dict = {
            "profile": {
                "object": "profile",
                "id": mock_profile["id"],
                "email": mock_profile["email"],
                "first_name": mock_profile["first_name"],
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

        profile = self.sso.get_profile(123)

        assert profile.to_dict() == mock_profile

    def test_create_connection(
        self, setup_with_client_id, mock_request_method, mock_connection
    ):
        response_dict = {
            "object": "connection",
            "id": mock_connection["id"],
            "name": mock_connection["name"],
            "status": mock_connection["status"],
            "connection_type": mock_connection["connection_type"],
            "oauth_uid": mock_connection["oauth_uid"],
            "oauth_secret": mock_connection["oauth_secret"],
            "oauth_redirect_uri": mock_connection["oauth_redirect_uri"],
            "saml_entity_id": mock_connection["saml_entity_id"],
            "saml_idp_url": mock_connection["saml_idp_url"],
            "saml_relying_party_trust_cert": mock_connection[
                "saml_relying_party_trust_cert"
            ],
            "saml_x509_certs": mock_connection["saml_x509_certs"],
            "domains": mock_connection["domains"],
        }
        mock_request_method("post", mock_connection, 201)

        connection = self.sso.create_connection("draft_conn_id")
        assert connection == response_dict

    def test_get_connection(
        self, setup_with_client_id, mock_connection, mock_request_method
    ):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.response_dict = mock_connection
        mock_request_method("get", mock_response, 200)
        response = self.sso.get_connection(connection="connection_id")
        assert response.status_code == 200
        assert response.response_dict == mock_connection

    def test_list_connections(
        self, setup_with_client_id, mock_connections, mock_request_method
    ):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.response_dict = mock_connections
        mock_request_method("get", mock_response, 200)
        response = self.sso.list_connections()
        assert response.status_code == 200
        assert response.response_dict == mock_connections

    def test_delete_connection(self, setup_with_client_id, mock_request_method):
        mock_response = Response()
        mock_response.status_code = 200
        mock_request_method("delete", mock_response, 200)
        response = self.sso.delete_connection(connection="connection_id")
        assert response.status_code == 200
