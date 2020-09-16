import workos
from workos.utils.request import RequestHelper, REQUEST_METHOD_POST
from workos.utils.validation import PASSWORDLESS_MODULE, validate_settings


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
        """Create an Passwordless Session.

        Args:
            session_options (dict) - An session options object
                session_options[email] (str): The email of the user to authenticate.
                session_options[state] (str): Optional parameter that the redirect
                    URI received from WorkOS will contain. The state parameter
                    can be used to encode arbitrary information to help
                    restore application state between redirects.
                session_options[type] (str): The type of Passwordless Session to
                    create. Currently, the only supported value is 'MagicLink'.

        Returns:
            dict: Passwordless Session
        """

        return self.request_helper.request(
            "passwordless/sessions",
            method=REQUEST_METHOD_POST,
            params=session_options,
            token=workos.api_key,
        )

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
