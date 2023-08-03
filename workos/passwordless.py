import workos
from workos.utils.request import RequestHelper, REQUEST_METHOD_POST
from workos.utils.validation import PASSWORDLESS_MODULE, validate_settings
from workos.resources.passwordless import WorkOSPasswordlessSession


class Passwordless(object):
    """Offers methods through the WorkOS Passwordless service."""

    @validate_settings(PASSWORDLESS_MODULE)
    def __init__(self):
        pass

    @property
    def request_helper(self):
        if not getattr(self, "_request_helper", None):
            self._request_helper = RequestHelper()
        return self._request_helper

    def create_session(self, session_options):
        """Create a Passwordless Session.

        Args:
            session_options (dict) - An session options object
                session_options[email] (str): The email of the user to authenticate.
                session_options[redirect_uri] (str): Optional parameter to
                    specify the redirect endpoint which will handle the callback
                    from WorkOS. Defaults to the default Redirect URI in the
                    WorkOS dashboard.
                session_options[state] (str): Optional parameter that the redirect
                    URI received from WorkOS will contain. The state parameter
                    can be used to encode arbitrary information to help
                    restore application state between redirects.
                session_options[type] (str): The type of Passwordless Session to
                    create. Currently, the only supported value is 'MagicLink'.
                session_options[expires_in] (int): The number of seconds the Passwordless Session should live before expiring.
                    This value must be between 900 (15 minutes) and 86400 (24 hours), inclusive.

        Returns:
            dict: Passwordless Session
        """

        response = self.request_helper.request(
            "passwordless/sessions",
            method=REQUEST_METHOD_POST,
            params=session_options,
            token=workos.api_key,
        )

        return WorkOSPasswordlessSession.construct_from_response(response).to_dict()

    def send_session(self, session_id):
        """Send a Passwordless Session via email.

        Args:
            session_id (str): The unique identifier of the Passwordless
                Session to send an email for.

        Returns:
            boolean: Returns True
        """
        self.request_helper.request(
            "passwordless/sessions/{session_id}/send".format(session_id=session_id),
            method=REQUEST_METHOD_POST,
            token=workos.api_key,
        )

        return True
