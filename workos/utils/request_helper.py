from enum import Enum
from typing import Dict, Union
import urllib.parse


DEFAULT_LIST_RESPONSE_LIMIT = 10
RESPONSE_TYPE_CODE = "code"


class RequestMethod(Enum):
    DELETE = "delete"
    GET = "get"
    POST = "post"
    PUT = "put"


QueryParameterValue = Union[str, int, bool, None]
QueryParameters = Dict[str, QueryParameterValue]


class RequestHelper:

    @classmethod
    def build_parameterized_path(
        cls, *, path: str, **params: QueryParameterValue
    ) -> str:
        escaped_params = {k: urllib.parse.quote(str(v)) for k, v in params.items()}
        return path.format(**escaped_params)

    @classmethod
    def build_url_with_query_params(
        cls, *, base_url: str, path: str, **params: QueryParameterValue
    ) -> str:
        return base_url.format(path) + "?" + urllib.parse.urlencode(params)
