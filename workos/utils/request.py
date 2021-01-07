import requests

import workos
from workos.exceptions import (
    AuthorizationException,
    AuthenticationException,
    BadRequestException,
    ServerException,
)

BASE_HEADERS = {
    "User-Agent": "WorkOS Python/{}".format(workos.__version__),
}

RESPONSE_TYPE_CODE = "code"

REQUEST_METHOD_GET = "get"
REQUEST_METHOD_POST = "post"


class RequestHelper(object):
    def __init__(self):
        self.set_base_api_url(workos.base_api_url)

    def set_base_api_url(self, base_api_url):
        """Creates an accessible template for constructing the URL for an API request.

        Args:
            base_api_url (str): Base URL for api requests (Should end with a /)
        """
        self.base_api_url = "{}{{}}".format(base_api_url)

    def generate_api_url(self, path):
        return self.base_api_url.format(path)

    def request(
        self, path, method=REQUEST_METHOD_GET, params=None, headers=None, token=None,
    ):
        """Executes a request against the WorkOS API.

        Args:
            path (str): Path for the api request that'd be appended to the base API URL

        Kwargs:
            method (str): One of the supported methods as defined by the REQUEST_METHOD_X constants
            params (dict): Query params to be added to the request
            token (str): Bearer token

        Returns:
            dict: Response from WorkOS
        """
        if headers is None:
            headers = {}

        if token:
            headers["Authorization"] = "Bearer {}".format(token)

        headers.update(BASE_HEADERS)
        url = self.generate_api_url(path)

        request_fn = getattr(requests, method)
        if method == REQUEST_METHOD_GET:
            response = request_fn(url, headers=headers, params=params)
        else:
            response = request_fn(url, headers=headers, json=params)

        status_code = response.status_code
        if status_code >= 400 and status_code < 500:
            if status_code == 401:
                raise AuthenticationException(response)
            elif status_code == 403:
                raise AuthorizationException(response)
            raise BadRequestException(response)
        elif status_code >= 500 and status_code < 600:
            raise ServerException(response)

        try:
            return response.json()
        except ValueError:
            raise ServerException(response)
