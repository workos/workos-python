import json

from requests import Request

import workos
from workos.exceptions import ConfigurationException
from workos.resources.sso import WorkOSProfile
from workos.utils.request import RequestHelper, RESPONSE_TYPE_CODE, REQUEST_METHOD_POST

AUTHORIZATION_PATH = 'sso/authorize'
TOKEN_PATH = 'sso/token'

OAUTH_GRANT_TYPE = 'authorization_code'

class SSO(object):
    '''Offers methods to assist in authenticating through the WorkOS SSO service.'''

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
        '''Generate an OAuth 2.0 authorization URL.

        The URL generated will redirect a User to the Identity Provider configured through
        WorkOS.

        Args:
            domain (str) - The domain a user is associated with, as configured on WorkOS
            redirect_uri (str) - A valid redirect URI, as specified on WorkOS
            state (dict) - A dict passed to WorkOS, that'd be preserved through the authentication workflow, passed
            back as a query parameter

        Returns:
            str: URL to redirect a User to to begin the OAuth workflow with WorkOS
        '''
        params = {
            'domain': domain,
            'client_id': workos.project_id,
            'redirect_uri': redirect_uri,
            'response_type': RESPONSE_TYPE_CODE,
        }
        if state is not None:
            params['state'] = json.dumps(state)

        prepared_request = Request(
            'GET',
            self.request_helper.generate_api_url(AUTHORIZATION_PATH),
            params=params
        ).prepare()

        return prepared_request.url

    def get_profile(self, code):
        '''Get the profile of an authenticated User

        Once authenticated, using the code returned having followed the authorization URL,
        get the WorkOS profile of the User.

        Args:
            code (str): Code returned by WorkOS on completion of OAuth 2.0 workflow

        Returns:
            WorkOSProfile - WorkOSProfile object representing the User
        '''
        params = {
            'client_id': workos.project_id,
            'client_secret': workos.api_key,
            'code': code,
            'grant_type': OAUTH_GRANT_TYPE
        }

        response = self.request_helper.request(TOKEN_PATH, method=REQUEST_METHOD_POST, params=params)

        return WorkOSProfile.construct_from_response(response)