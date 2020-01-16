class ConfigurationException(Exception):
    pass


# Request related exceptions
class BaseRequestException(Exception):
    def __init__(self, response, message=None):
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


class AuthorizationException(BaseRequestException):
    pass


class AuthenticationException(BaseRequestException):
    pass


class BadRequestException(BaseRequestException):
    pass


class ServerException(BaseRequestException):
    pass
