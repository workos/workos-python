import platform

import requests
import urllib

import workos
from workos.exceptions import (
    AuthorizationException,
    AuthenticationException,
    BadRequestException,
    NotFoundException,
    ServerException,
)

BASE_HEADERS = {
    "User-Agent": "WorkOS Python/{} Python SDK/{}".format(
        platform.python_version(),
        workos.__version__,
    ),
}

RESPONSE_TYPE_CODE = "code"

REQUEST_METHOD_DELETE = "delete"
REQUEST_METHOD_GET = "get"
REQUEST_METHOD_POST = "post"
REQUEST_METHOD_PUT = "put"


class RequestHelper(object):
    def __init__(self):
        self.set_base_api_url(workos.base_api_url)
        self.set_request_timeout(workos.request_timeout)

    def set_request_timeout(self, request_timeout):
        self.request_timeout = request_timeout

    def set_base_api_url(self, base_api_url):
        """Creates an accessible template for constructing the URL for an API request.

        Args:
            base_api_url (str): Base URL for api requests (Should end with a /)
        """
        self.base_api_url = "{}{{}}".format(base_api_url)

    def generate_api_url(self, path):
        return self.base_api_url.format(path)

    def build_parameterized_url(self, url, **params):
        escaped_params = {k: urllib.parse.quote(str(v)) for k, v in params.items()}
        return url.format(**escaped_params)

    def request(
        self,
        path,
        method=REQUEST_METHOD_GET,
        params=None,
        headers=None,
        token=None,
    ):
        """Executes a request against the WorkOS API.

        Args:
            path (str): Path for the api request that'd be appended to the base API URL

        Kwargs:
            method (str): One of the supported methods as defined by the REQUEST_METHOD_X constants
            params (dict): Query params or body payload to be added to the request
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
            response = request_fn(
                url, headers=headers, params=params, timeout=self.request_timeout
            )
        else:
            response = request_fn(
                url, headers=headers, json=params, timeout=self.request_timeout
            )

        response_json = None
        content_type = (
            response.headers.get("content-type")
            if response.headers is not None
            else None
        )
        if content_type is not None and "application/json" in content_type:
            try:
                response_json = response.json()
            except ValueError:
                raise ServerException(response)

        status_code = response.status_code
        if status_code >= 400 and status_code < 500:
            if status_code == 401:
                raise AuthenticationException(response)
            elif status_code == 403:
                raise AuthorizationException(response)
            elif status_code == 404:
                raise NotFoundException(response)
            error = response_json.get("error")
            error_description = response_json.get("error_description")
            raise BadRequestException(
                response, error=error, error_description=error_description
            )
        elif status_code >= 500 and status_code < 600:
            raise ServerException(response)

        return response_json
