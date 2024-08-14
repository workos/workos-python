from typing import Literal, Optional, Protocol

from workos.types.passwordless.passwordless_session_type import PasswordlessSessionType
from workos.utils.http_client import SyncHTTPClient
from workos.utils.request_helper import REQUEST_METHOD_POST
from workos.types.passwordless.passwordless_session import PasswordlessSession


class PasswordlessModule(Protocol):
    """Offers methods through the WorkOS Passwordless service."""

    def create_session(
        self,
        *,
        email: str,
        type: PasswordlessSessionType,
        redirect_uri: Optional[str] = None,
        state: Optional[str] = None,
        expires_in: Optional[int] = None,
    ) -> PasswordlessSession:
        """Create a Passwordless Session.

        Kwargs:
            email (str): The email of the user to authenticate.
            type (PasswordlessSessionType): The type of Passwordless Session to
                create. Currently, the only supported value is 'MagicLink'.
            redirect_uri (str): Optional parameter to
                specify the redirect endpoint which will handle the callback
                from WorkOS. Defaults to the default Redirect URI in the
                WorkOS dashboard. (Optional)
            state (str): Optional parameter that the redirect
                URI received from WorkOS will contain. The state parameter
                can be used to encode arbitrary information to help
                restore application state between redirects. (Optional)
            expires_in (int): The number of seconds the Passwordless Session should live before expiring.
                This value must be between 900 (15 minutes) and 86400 (24 hours), inclusive. (Optional)

        Returns:
            PasswordlessSession: A passwordless session object.
        """
        ...

    def send_session(self, session_id: str) -> Literal[True]:
        """Send a Passwordless Session via email.

        Args:
            session_id (str): The unique identifier of the Passwordless
                Session to send an email for.

        Returns:
            boolean: Returns True
        """
        ...


class Passwordless(PasswordlessModule):
    _http_client: SyncHTTPClient

    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def create_session(
        self,
        *,
        email: str,
        type: PasswordlessSessionType,
        redirect_uri: Optional[str] = None,
        state: Optional[str] = None,
        expires_in: Optional[int] = None,
    ) -> PasswordlessSession:
        json = {
            "email": email,
            "type": type,
            "expires_in": expires_in,
            "redirect_uri": redirect_uri,
            "state": state,
        }

        response = self._http_client.request(
            "passwordless/sessions", method=REQUEST_METHOD_POST, json=json
        )

        return PasswordlessSession.model_validate(response)

    def send_session(self, session_id: str) -> Literal[True]:
        self._http_client.request(
            "passwordless/sessions/{session_id}/send".format(session_id=session_id),
            method=REQUEST_METHOD_POST,
        )

        return True
