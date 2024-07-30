from typing import Literal, Optional, Protocol

import workos
from workos.utils.http_client import SyncHTTPClient
from workos.utils.request_helper import REQUEST_METHOD_POST
from workos.utils.validation import PASSWORDLESS_MODULE, validate_settings
from workos.resources.passwordless import PasswordlessSession, PasswordlessSessionType


class PasswordlessModule(Protocol):
    def create_session(
        self,
        email: str,
        type: PasswordlessSessionType,
        redirect_uri: Optional[str] = None,
        state: Optional[str] = None,
        expires_in: Optional[int] = None,
    ) -> PasswordlessSession: ...

    def send_session(self, session_id: str) -> Literal[True]: ...


class Passwordless(PasswordlessModule):
    """Offers methods through the WorkOS Passwordless service."""

    _http_client: SyncHTTPClient

    @validate_settings(PASSWORDLESS_MODULE)
    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def create_session(
        self,
        email: str,
        type: PasswordlessSessionType,
        redirect_uri: Optional[str] = None,
        state: Optional[str] = None,
        expires_in: Optional[int] = None,
    ) -> PasswordlessSession:
        """Create a Passwordless Session.

        Args:
            email (str): The email of the user to authenticate.
            redirect_uri (str): Optional parameter to
                specify the redirect endpoint which will handle the callback
                from WorkOS. Defaults to the default Redirect URI in the
                WorkOS dashboard.
            state (str): Optional parameter that the redirect
                URI received from WorkOS will contain. The state parameter
                can be used to encode arbitrary information to help
                restore application state between redirects.
            type (str): The type of Passwordless Session to
                create. Currently, the only supported value is 'MagicLink'.
            expires_in (int): The number of seconds the Passwordless Session should live before expiring.
                This value must be between 900 (15 minutes) and 86400 (24 hours), inclusive.

        Returns:
            PasswordlessSession
        """

        params = {
            "email": email,
            "type": type,
            "expires_in": expires_in,
            "redirect_uri": redirect_uri,
            "state": state,
        }

        response = self._http_client.request(
            "passwordless/sessions",
            method=REQUEST_METHOD_POST,
            params=params,
            token=workos.api_key,
        )

        return PasswordlessSession.model_validate(response)

    def send_session(self, session_id: str) -> Literal[True]:
        """Send a Passwordless Session via email.

        Args:
            session_id (str): The unique identifier of the Passwordless
                Session to send an email for.

        Returns:
            boolean: Returns True
        """
        self._http_client.request(
            "passwordless/sessions/{session_id}/send".format(session_id=session_id),
            method=REQUEST_METHOD_POST,
            token=workos.api_key,
        )

        return True
