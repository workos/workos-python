from requests import Request

import workos
from workos.exceptions import ConfigurationException
from workos.resources.sso import SSOProfile
from workos.utils.requests import RequestHelper, RESPONSE_TYPE_CODE, REQUEST_METHOD_POST

AUTHORIZATION_PATH = 'sso/authorize'
TOKEN_PATH = 'sso/token'

OAUTH_GRANT_TYPE = 'authorization_code'

class SSO(object):
    def __init__(self):
        required_settings = ['api_key', 'project_id', ]

        missing_settings = []
        for setting in required_settings:
            if not getattr(workos, setting, None):
                missing_settings.append(setting)

        if missing_settings:
            raise ConfigurationException(
                'The following settings are missing for SSO: {}'.format(', '.join(missing_settings))
            )

    @property
    def request_helper(self):
        if not getattr(self, '_request_helper', None):
            self._request_helper = RequestHelper()
        return self._request_helper

    def get_authorization_url(self, domain, redirect_uri, state=None):
        params = {
            'domain': domain,
            'client_id': workos.project_id,
            'redirect_uri': redirect_uri,
            'response_type': RESPONSE_TYPE_CODE,
        }
        if state is not None:
            params['state'] = state

        prepared_request = Request(
            'GET',
            self.request_helper.generate_api_url(AUTHORIZATION_PATH),
            params=params
        ).prepare()

        return prepared_request.url

    def get_profile(self, code):
        params = {
            'client_id': workos.project_id,
            'client_secret': workos.api_key,
            'code': code,
            'grant_type': OAUTH_GRANT_TYPE
        }

        response = self.request_helper.request(TOKEN_PATH, method=REQUEST_METHOD_POST, params=params)
        return SSOProfile.construct_from_response(response)