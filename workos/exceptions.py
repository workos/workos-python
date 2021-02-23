class ConfigurationException(Exception):
    pass


# Request related exceptions
class BaseRequestException(Exception):
    def __init__(self, response, message=None, error=None):
        super(BaseRequestException, self).__init__(message)

        self.error = error
        self.extract_and_set_response_related_data(response)

        if message is not None:
            self.message = message

    def extract_and_set_response_related_data(self, response):
        self.response = response

        try:
            response_json = response.json()
            self.message = response_json.get("message")
        except ValueError:
            self.message = None

        headers = response.headers
        self.request_id = headers.get("X-Request-ID")

    def __str__(self):
        message = self.message or "No message"
        exception = "(message=%s" % message

        if self.request_id is not None:
            exception += ", request_id=%s" % self.request_id

        if self.error is not None:
            exception += ", error=%s" % self.error

        return exception + ")"


class AuthorizationException(BaseRequestException):
    pass


class AuthenticationException(BaseRequestException):
    pass


class BadRequestException(BaseRequestException):
    pass


class ServerException(BaseRequestException):
    pass
