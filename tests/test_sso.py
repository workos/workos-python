import json
from six.moves.urllib.parse import parse_qsl, urlparse

import pytest

import workos
from workos.sso import SSO
from workos.utils.connection_types import ConnectionType
from workos.utils.request import RESPONSE_TYPE_CODE


class TestSSO(object):
    @pytest.fixture(autouse=True)
    def setup(self, set_api_key_and_project_id):
        self.provider = ConnectionType.GoogleOAuth
        self.customer_domain = "workos.com"
        self.redirect_uri = "https://localhost/auth/callback"
        self.state = {
            "things": "with_stuff",
        }

        self.sso = SSO()

    @pytest.fixture
    def mock_profile(self):
        return {
            "id": "prof_01DWAS7ZQWM70PV93BFV1V78QV",
            "email": "demo@workos-okta.com",
            "first_name": "WorkOS",
            "last_name": "Demo",
            "connection_type": "OktaSAML",
            "idp_id": "00u1klkowm8EGah2H357",
        }

    def test_authorization_url_throws_value_error_with_missing_domain_and_provider(
        self,
    ):
        with pytest.raises(ValueError, match=r"Incomplete arguments.*"):
            self.sso.get_authorization_url(
                redirect_uri=self.redirect_uri, state=self.state
            )

    def test_authorization_url_throws_value_error_with_incorrect_provider_type(self):
        with pytest.raises(
            ValueError, match="'provider' must be of type ConnectionType"
        ):
            self.sso.get_authorization_url(
                provider="foo", redirect_uri=self.redirect_uri, state=self.state
            )

    def test_authorization_url_has_expected_query_params_with_provider(self):
        authorization_url = self.sso.get_authorization_url(
            provider=self.provider, redirect_uri=self.redirect_uri, state=self.state
        )

        parsed_url = urlparse(authorization_url)

        assert dict(parse_qsl(parsed_url.query)) == {
            "provider": str(self.provider),
            "client_id": workos.project_id,
            "redirect_uri": self.redirect_uri,
            "response_type": RESPONSE_TYPE_CODE,
            "state": json.dumps(self.state),
        }

    def test_authorization_url_has_expected_query_params_with_domain(self):
        authorization_url = self.sso.get_authorization_url(
            domain=self.customer_domain,
            redirect_uri=self.redirect_uri,
            state=self.state,
        )

        parsed_url = urlparse(authorization_url)

        assert dict(parse_qsl(parsed_url.query)) == {
            "domain": self.customer_domain,
            "client_id": workos.project_id,
            "redirect_uri": self.redirect_uri,
            "response_type": RESPONSE_TYPE_CODE,
            "state": json.dumps(self.state),
        }

    def test_authorization_url_has_expected_query_params_with_domain_and_provider(self):
        authorization_url = self.sso.get_authorization_url(
            domain=self.customer_domain,
            provider=self.provider,
            redirect_uri=self.redirect_uri,
            state=self.state,
        )

        parsed_url = urlparse(authorization_url)

        assert dict(parse_qsl(parsed_url.query)) == {
            "domain": self.customer_domain,
            "provider": str(self.provider),
            "client_id": workos.project_id,
            "redirect_uri": self.redirect_uri,
            "response_type": RESPONSE_TYPE_CODE,
            "state": json.dumps(self.state),
        }

    def test_get_profile_returns_expected_workosprofile_object(
        self, mock_profile, mock_request_method
    ):
        response_dict = {
            "profile": {
                "object": "profile",
                "id": mock_profile["id"],
                "email": mock_profile["email"],
                "first_name": mock_profile["first_name"],
                "connection_type": mock_profile["connection_type"],
                "last_name": mock_profile["last_name"],
                "idp_id": mock_profile["idp_id"],
            },
            "access_token": "01DY34ACQTM3B1CSX1YSZ8Z00D",
        }

        mock_request_method("post", response_dict, 200)

        profile = self.sso.get_profile(123)

        assert profile.to_dict() == mock_profile
