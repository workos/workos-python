import workos
from workos.utils.request import RequestHelper, REQUEST_METHOD_POST
from workos.utils.validation import PORTAL_MODULE, validate_settings


PORTAL_GENERATE_PATH = "portal/generate_link"


class Portal(object):
    @validate_settings(PORTAL_MODULE)
    def __init__(self):
        pass

    @property
    def request_helper(self):
        if not getattr(self, "_request_helper", None):
            self._request_helper = RequestHelper()
        return self._request_helper

    def generate_link(self, intent, organization, return_url=None, success_url=None):
        """Generate a link to grant access to an organization's Admin Portal

        Args:
            intent (str): The access scope for the generated Admin Portal link. Valid values are: ["audit_logs", "dsync", "log_streams", "sso",]
            organization (string): The ID of the organization the Admin Portal link will be generated for

        Kwargs:
            return_url (str): The URL that the end user will be redirected to upon exiting the generated Admin Portal. If none is provided, the default redirect link set in your WorkOS Dashboard will be used. (Optional)
            success_url (str): The URL to which WorkOS will redirect users to upon successfully viewing Audit Logs, setting up Log Streams, Single Sign On or Directory Sync. (Optional)

        Returns:
            str:  URL to redirect a User to to access an Admin Portal session
        """
        params = {
            "intent": intent,
            "organization": organization,
            "return_url": return_url,
            "success_url": success_url,
        }
        return self.request_helper.request(
            PORTAL_GENERATE_PATH,
            method=REQUEST_METHOD_POST,
            params=params,
            token=workos.api_key,
        )
