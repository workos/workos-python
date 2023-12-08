class ConfigurationException(Exception):
    pass


# Request related exceptions
class BaseRequestException(Exception):
    def __init__(
        self,
        response,
        message=None,
        error=None,
        errors=None,
        error_description=None,
        code=None,
        pending_authentication_token=None,
    ):
        super(BaseRequestException, self).__init__(message)

        self.message = message
        self.error = error
        self.errors = errors
        self.code = code
        self.error_description = error_description
        self.pending_authentication_token = pending_authentication_token
        self.extract_and_set_response_related_data(response)

    def extract_and_set_response_related_data(self, response):
        self.response = response

        try:
            response_json = response.json()
            self.message = response_json.get("message")
            self.error = response_json.get("error")
            self.errors = response_json.get("errors")
            self.code = response_json.get("code")
            self.error_description = response_json.get("error_description")
            self.pending_authentication_token = response_json.get(
                "pending_authentication_token"
            )
        except ValueError:
            self.message = None
            self.error = None
            self.errors = None
            self.code = None
            self.error_description = None
            self.pending_authentication_token = None

        headers = response.headers
        self.request_id = headers.get("X-Request-ID")

    def __str__(self):
        message = self.message or "No message"
        exception = "(message=%s" % message

        if self.request_id is not None:
            exception += ", request_id=%s" % self.request_id

        if self.code is not None:
            exception += ", code=%s" % self.code

        if self.error is not None:
            exception += ", error=%s" % self.error

        if self.errors is not None:
            exception += ", errors=%s" % self.errors

        if self.error_description is not None:
            exception += ", error_description=%s" % self.error_description

        if self.pending_authentication_token is not None:
            exception += (
                ", pending_authentication_token=%s" % self.pending_authentication_token
            )

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
