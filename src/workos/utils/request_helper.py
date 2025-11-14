from typing import Dict, Union
import urllib.parse


DEFAULT_LIST_RESPONSE_LIMIT = 10
RESPONSE_TYPE_CODE = "code"
REQUEST_METHOD_DELETE = "delete"
REQUEST_METHOD_GET = "get"
REQUEST_METHOD_POST = "post"
REQUEST_METHOD_PUT = "put"

QueryParameterValue = Union[str, int, bool, None]
QueryParameters = Dict[str, QueryParameterValue]


class RequestHelper:

    @classmethod
    def build_parameterized_url(cls, url: str, **params: QueryParameterValue) -> str:
        escaped_params = {k: urllib.parse.quote(str(v)) for k, v in params.items()}
        return url.format(**escaped_params)

    @classmethod
    def build_url_with_query_params(
        cls, base_url: str, path: str, **params: QueryParameterValue
    ) -> str:
        return base_url + path + "?" + urllib.parse.urlencode(params)
