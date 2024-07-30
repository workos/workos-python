import platform
from typing import (
    cast,
    Dict,
    Generic,
    Mapping,
    Optional,
    TypeVar,
    Union,
)
from typing_extensions import NotRequired, TypedDict

import httpx

from workos.exceptions import (
    ServerException,
    AuthenticationException,
    AuthorizationException,
    NotFoundException,
    BadRequestException,
)
from workos.utils.request_helper import REQUEST_METHOD_DELETE, REQUEST_METHOD_GET


_HttpxClientT = TypeVar("_HttpxClientT", bound=Union[httpx.Client, httpx.AsyncClient])


DEFAULT_REQUEST_TIMEOUT = 25


class PreparedRequest(TypedDict):
    method: str
    url: str
    headers: httpx.Headers
    params: NotRequired[Union[Mapping, None]]
    json: NotRequired[Union[Mapping, None]]
    timeout: int


class BaseHTTPClient(Generic[_HttpxClientT]):
    _client: _HttpxClientT
    _base_url: str
    _version: str
    _timeout: int

    def __init__(
        self,
        *,
        base_url: str,
        version: str,
        timeout: Optional[int] = DEFAULT_REQUEST_TIMEOUT,
    ) -> None:
        self.base_url = base_url
        self._version = version
        self._timeout = DEFAULT_REQUEST_TIMEOUT if timeout is None else timeout

    def _enforce_trailing_slash(self, url: str) -> str:
        return url if url.endswith("/") else url + "/"

    def _generate_api_url(self, path: str) -> str:
        return self._base_url.format(path)

    def _build_headers(
        self, custom_headers: Union[dict, None], token: Optional[str] = None
    ) -> httpx.Headers:
        if custom_headers is None:
            custom_headers = {}

        if token:
            custom_headers["Authorization"] = "Bearer {}".format(token)

        # httpx.Headers is case-insensitive while dictionaries are not.
        return httpx.Headers({**self.default_headers, **custom_headers})

    def _maybe_raise_error_by_status_code(
        self, response: httpx.Response, response_json: Union[dict, None]
    ) -> None:
        status_code = response.status_code
        if status_code >= 400 and status_code < 500:
            if status_code == 401:
                raise AuthenticationException(response)
            elif status_code == 403:
                raise AuthorizationException(response)
            elif status_code == 404:
                raise NotFoundException(response)

            error = (
                response_json.get("error")
                if response_json and "error" in response_json
                else "Unknown"
            )
            error_description = (
                response_json.get("error_description")
                if response_json and "error_description" in response_json
                else "Unknown"
            )
            raise BadRequestException(
                response, error=error, error_description=error_description
            )
        elif status_code >= 500 and status_code < 600:
            raise ServerException(response)

    def _prepare_request(
        self,
        path: str,
        method: Optional[str] = REQUEST_METHOD_GET,
        params: Optional[Mapping] = None,
        headers: Optional[dict] = None,
        token: Optional[str] = None,
    ) -> PreparedRequest:
        """Executes a request against the WorkOS API.

        Args:
            path (str): Path for the api request that'd be appended to the base API URL

        Kwargs:
            method Optional[str]: One of the supported methods as defined by the REQUEST_METHOD_X constants
            params Optional[dict]: Query params or body payload to be added to the request
            headers Optional[dict]: Custom headers to be added to the request
            token Optional[str]: Bearer token

        Returns:
            dict: Response from WorkOS
        """
        url = self._generate_api_url(path)
        parsed_headers = self._build_headers(headers, token)
        parsed_method = REQUEST_METHOD_GET if method is None else method
        bodyless_http_method = parsed_method.lower() in [
            REQUEST_METHOD_DELETE,
            REQUEST_METHOD_GET,
        ]

        # Remove any parameters that are None
        if params is not None:
            params = (
                {k: v for k, v in params.items() if v is not None}
                if bodyless_http_method
                else params
            )

        # We'll spread these return values onto the HTTP client request method
        if bodyless_http_method:
            return {
                "method": parsed_method,
                "url": url,
                "headers": parsed_headers,
                "params": params,
                "timeout": self.timeout,
            }
        else:
            return {
                "method": parsed_method,
                "url": url,
                "headers": parsed_headers,
                "json": params,
                "timeout": self.timeout,
            }

    def _handle_response(self, response: httpx.Response) -> dict:
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

        # type: ignore
        self._maybe_raise_error_by_status_code(response, response_json)

        return cast(Dict, response_json)

    def build_request_url(
        self,
        url: str,
        method: Optional[str] = REQUEST_METHOD_GET,
        params: Optional[Mapping] = None,
    ) -> str:
        return self._client.build_request(
            method=method or REQUEST_METHOD_GET, url=url, params=params
        ).url.__str__()

    @property
    def base_url(self) -> str:
        return self._base_url

    @base_url.setter
    def base_url(self, url: str) -> None:
        """Creates an accessible template for constructing the URL for an API request.

        Args:
            base_api_url (str): Base URL for api requests
        """
        self._base_url = "{}{{}}".format(self._enforce_trailing_slash(url))

    @property
    def default_headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": self.user_agent,
        }

    @property
    def user_agent(self) -> str:
        return "WorkOS Python/{} Python SDK/{}".format(
            platform.python_version(),
            self._version,
        )

    @property
    def timeout(self) -> int:
        return self._timeout

    @property
    def version(self) -> str:
        return self._version
