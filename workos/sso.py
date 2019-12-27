from requests import Request

from .constants import RESPONSE_TYPE_CODE
from .utils.requests import request_helper, REQUEST_METHOD_POST
from .utils.settings import get_setting, API_KEY_SETTING_KEY, PROJECT_ID_SETTING_KEY

AUTHORIZATION_PATH = 'sso/authorize'
TOKEN_PATH = 'sso/token'

OAUTH_GRANT_TYPE = 'authorization_code'

class SSO(object):
    @property
    def api_key(self):
        return get_setting(API_KEY_SETTING_KEY)

    @property
    def project_id(self):
        return get_setting(PROJECT_ID_SETTING_KEY)

    def get_authorization_url(self, domain, redirect_uri, state=None):
        params = {
            'domain': domain,
            'client_id': self.project_id,
            'redirect_uri': redirect_uri,
            'response_type': RESPONSE_TYPE_CODE,
        }
        if state is not None:
            params['state'] = state

        prepared_request = Request(
            'GET',
            request_helper.generate_api_url(AUTHORIZATION_PATH),
            params=params
        ).prepare()

        return prepared_request.url

    def get_profile(self, code, redirect_uri):
        params = {
            'client_id': self.project_id,
            'client_secret': self.api_key,
            'code': code,
            'redirect_uri': redirect_uri,
            'grant_type': OAUTH_GRANT_TYPE
        }

        response = request_helper.request(TOKEN_PATH, method=REQUEST_METHOD_POST, params=params)
        return response['profile']