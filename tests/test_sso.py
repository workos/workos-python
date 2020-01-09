import json
from urllib.parse import parse_qsl, urlparse

import pytest
import requests

import workos
from workos.sso import SSO
from workos.utils.requests import RESPONSE_TYPE_CODE

class MockResponse(object):
    def __init__(self, response_dict, status_code):
        self.response_dict = response_dict
        self.status_code = status_code

    def json(self):
        return self.response_dict

class TestSSO(object):
    @pytest.fixture(autouse=True)
    def setup(self, set_api_key_and_project_id):
        self.customer_domain = 'workos.com'
        self.redirect_uri = 'https://localhost/auth/callback'
        self.state = { 'things': 'with_stuff', }

        self.sso = SSO()

    @pytest.fixture
    def mock_profile(self):
        return {
            'id': 'prof_01DWAS7ZQWM70PV93BFV1V78QV',
            'email': 'demo@workos-okta.com',
            'first_name': 'WorkOS',
            'last_name': 'Demo',
            'connection_type': 'OktaSAML',
            'idp_id': '00u1klkowm8EGah2H357'
        }

    @pytest.fixture
    def mock_request_post_profile(self, monkeypatch, mock_profile):
        def mock_post(*args, **kwargs):
            return MockResponse({
                'profile': {
                    'object': 'profile',
                    'id': mock_profile['id'],
                    'email': mock_profile['email'],
                    'first_name': mock_profile['first_name'],
                    'connection_type': mock_profile['connection_type'],
                    'last_name': mock_profile['last_name'],
                    'idp_id': mock_profile['idp_id'],
                },
                'access_token': '01DY34ACQTM3B1CSX1YSZ8Z00D',
            }, 200)

        monkeypatch.setattr(requests, 'post', mock_post)

    def test_authorization_url_has_expected_query_params(self):
        authorization_url = self.sso.get_authorization_url(
            self.customer_domain,
            self.redirect_uri,
            state=self.state
        )

        parsed_url = urlparse(authorization_url)

        assert dict(parse_qsl(parsed_url.query)) == {
            'domain': self.customer_domain,
            'client_id': workos.project_id,
            'redirect_uri': self.redirect_uri,
            'response_type': RESPONSE_TYPE_CODE,
            'state': json.dumps(self.state),
        }


    def test_get_profile_returns_expected_workosprofile_object(
        self, mock_request_post_profile, mock_profile
    ):
        profile = self.sso.get_profile(123)

        assert profile.to_dict() == mock_profile