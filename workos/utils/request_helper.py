import urllib.parse


DEFAULT_LIST_RESPONSE_LIMIT = 10
RESPONSE_TYPE_CODE = "code"
REQUEST_METHOD_DELETE = "delete"
REQUEST_METHOD_GET = "get"
REQUEST_METHOD_POST = "post"
REQUEST_METHOD_PUT = "put"


class RequestHelper:

    @classmethod
    def build_parameterized_url(cls, url, **params):
        escaped_params = {k: urllib.parse.quote(str(v)) for k, v in params.items()}
        return url.format(**escaped_params)

    @classmethod
    def build_url_with_query_params(cls, base_url: str, path: str, **params):
        return base_url.format(path) + "?" + urllib.parse.urlencode(params)
