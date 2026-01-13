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

        self.message = self.extract_from_json("message", "No message")
        self.error = self.extract_from_json("error", "Unknown")
        self.errors = self.extract_from_json("errors", None)
        self.code = self.extract_from_json("code", None)
        self.error_description = self.extract_from_json("error_description", "Unknown")

        self.request_id = response.headers.get("X-Request-ID")

    def extract_from_json(self, key: str, alt: Optional[str] = None) -> Optional[str]:
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


class EmailVerificationRequiredException(AuthorizationException):
    """Raised when email verification is required before authentication.

    This exception includes an email_verification_id field that can be used
    to retrieve the email verification object or resend the verification email.
    """

    def __init__(
        self,
        response: httpx.Response,
        response_json: Optional[Mapping[str, Any]],
    ) -> None:
        super().__init__(response, response_json)
        self.email_verification_id = self.extract_from_json(
            "email_verification_id", None
        )


class AuthenticationException(BaseRequestException):
    pass


class BadRequestException(BaseRequestException):
    pass


class ConflictException(BaseRequestException):
    pass


class NotFoundException(BaseRequestException):
    pass


class ServerException(BaseRequestException):
    pass
