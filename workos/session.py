
from typing import Protocol, Union

from workos.types.user_management.session import AuthenticateWithSessionCookieSuccessResponse, AuthenticateWithSessionCookieErrorResponse

class SessionModule(Protocol):

    def authenticate(self) -> Union[AuthenticateWithSessionCookieSuccessResponse, AuthenticateWithSessionCookieErrorResponse]:
        ...