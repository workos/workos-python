import platform
from typing import (
    Any,
    Mapping,
    Sequence,
    cast,
    Dict,
    Generic,
    Optional,
    TypeVar,
    Union,
)
from typing_extensions import NotRequired, TypedDict

import httpx
from httpx._types import QueryParamTypes

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


ParamsType = Optional[Mapping[str, Any]]
HeadersType = Optional[Dict[str, str]]
JsonType = Optional[Union[Mapping[str, Any], Sequence[Any]]]
ResponseJson = Mapping[Any, Any]


class PreparedRequest(TypedDict):
    method: str
    url: str
    headers: httpx.Headers
    params: NotRequired[Optional[QueryParamTypes]]
    json: NotRequired[JsonType]
    timeout: int


class BaseHTTPClient(Generic[_HttpxClientT]):
    _client: _HttpxClientT

    _api_key: str
    _client_id: str
    _base_url: str
    _version: str
    _timeout: int

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        client_id: str,
        version: str,
        timeout: Optional[int] = DEFAULT_REQUEST_TIMEOUT,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._client_id = client_id
        self._version = version
        self._timeout = DEFAULT_REQUEST_TIMEOUT if timeout is None else timeout

    def _generate_api_url(self, path: str) -> str:
        return f"{self._base_url}{path}"

    def _build_headers(
        self,
        *,
        custom_headers: Union[HeadersType, None],
        exclude_default_auth_headers: bool = False,
    ) -> httpx.Headers:
        if custom_headers is None:
            custom_headers = {}

        default_headers = {
            **self.default_headers,
            **({} if exclude_default_auth_headers else self.auth_headers),
        }

        # httpx.Headers is case-insensitive while dictionaries are not.
        return httpx.Headers({**default_headers, **custom_headers})

    def _maybe_raise_error_by_status_code(
        self, response: httpx.Response, response_json: Union[ResponseJson, None]
    ) -> None:
        status_code = response.status_code
        if status_code >= 400 and status_code < 500:
            if status_code == 401:
                raise AuthenticationException(response, response_json)
            elif status_code == 403:
                raise AuthorizationException(response, response_json)
            elif status_code == 404:
                raise NotFoundException(response, response_json)

            raise BadRequestException(response, response_json)
        elif status_code >= 500 and status_code < 600:
            raise ServerException(response, response_json)

    def _prepare_request(
        self,
        path: str,
        method: Optional[str] = REQUEST_METHOD_GET,
        params: ParamsType = None,
        json: JsonType = None,
        headers: HeadersType = None,
        exclude_default_auth_headers: bool = False,
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
        parsed_headers = self._build_headers(
            custom_headers=headers,
            exclude_default_auth_headers=exclude_default_auth_headers,
        )
        parsed_method = REQUEST_METHOD_GET if method is None else method
        bodyless_http_method = parsed_method.lower() in [
            REQUEST_METHOD_DELETE,
            REQUEST_METHOD_GET,
        ]

        if bodyless_http_method and json is not None:
            raise ValueError(f"Cannot send a body with a {parsed_method} request")

        # Remove any parameters that are None
        if params is not None:
            params = {k: v for k, v in params.items() if v is not None}

        # Remove any body values that are None
        if json is not None and isinstance(json, Mapping):
            json = {k: v for k, v in json.items() if v is not None}

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
                "params": params,
                "json": json,
                "timeout": self.timeout,
            }

    def _handle_response(self, response: httpx.Response) -> ResponseJson:
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
                raise ServerException(response, None)

        self._maybe_raise_error_by_status_code(response, response_json)

        return cast(ResponseJson, response_json)

    def build_request_url(
        self,
        url: str,
        method: Optional[str] = REQUEST_METHOD_GET,
        params: Optional[QueryParamTypes] = None,
    ) -> str:
        return self._client.build_request(
            method=method or REQUEST_METHOD_GET, url=url, params=params
        ).url.__str__()

    @property
    def api_key(self) -> str:
        return self._api_key

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def client_id(self) -> str:
        return self._client_id

    @property
    def auth_headers(self) -> Mapping[str, str]:
        return self.auth_header_from_token(self._api_key)

    def auth_header_from_token(self, token: str) -> Mapping[str, str]:
        return {
            "Authorization": f"Bearer {token}",
        }

    @property
    def default_headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": self.user_agent,
        }

    @property
    def user_agent(self) -> str:
        # TODO: Include sync/async in user agent
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
