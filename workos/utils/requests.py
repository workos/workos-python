import requests

import workos
from workos.exceptions import (
    AuthorizationException, AuthenticationException, BadRequestException,
    ServerException,
)

RESPONSE_TYPE_CODE = 'code'

REQUEST_METHOD_GET = 'get'
REQUEST_METHOD_POST = 'post'

class RequestHelper(object):
    def __init__(self):
        self.set_base_api_url(workos.base_api_url)

    def set_base_api_url(self, base_api_url):
        self.base_api_url = '{}{{}}'.format(base_api_url)

    def generate_api_url(self, path):
        return self.base_api_url.format(path)

    def request(self, path, method=REQUEST_METHOD_GET, params=None):
        url = self.generate_api_url(path)
        response = getattr(requests, method)(url, params=params)

        status_code = response.status_code
        if status_code >= 400 and status_code < 500:
            if status_code == 401:
                raise AuthorizationException(response)
            elif status_code == 403:
                raise AuthenticationException(response)
            raise BadRequestException(response)
        elif status_code >= 500 and status_code < 600:
            raise ServerException(response)

        try:
            return response.json()
        except ValueError:
            raise ServerException(response)