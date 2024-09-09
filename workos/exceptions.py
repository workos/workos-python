from typing import Any, Mapping, Optional

import httpx


# Request related exceptions
class BaseRequestException(Exception):
    def __init__(
        self,
        response: httpx.Response,
        response_json: Optional[Mapping[str, Any]],
    ) -> None:
        super(BaseRequestException, self).__init__(response_json)

        self.response = response
        self.response_json = response_json

        self.message = self.extractFromJson("message", "No message")
        self.error = self.extractFromJson("error", None)
        self.errors = self.extractFromJson("errors", None)
        self.code = self.extractFromJson("code", None)
        self.error_description = self.extractFromJson("error_description", None)

        self.request_id = response.headers.get("X-Request-ID")

    def extractFromJson(self, key: str, alt: Optional[str] = None) -> Optional[str]:
        if self.response_json is None:
            return alt

        return self.response_json.get(key, alt)

    def __str__(self) -> str:
        exception = "(message=%s" % self.message
        exception += ", request_id=%s" % self.request_id

        if self.response_json is not None:
            for key, value in self.response_json.items():
                if key != "message":
                    exception += ", %s=%s" % (key, value)

        return exception + ")"


class AuthorizationException(BaseRequestException):
    pass


class AuthenticationException(BaseRequestException):
    pass


class BadRequestException(BaseRequestException):
    pass


class NotFoundException(BaseRequestException):
    pass


class ServerException(BaseRequestException):
    pass
