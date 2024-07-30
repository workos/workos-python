from typing import Optional, Protocol

import workos
from workos.resources.portal import PortalLink, PortalLinkIntent
from workos.utils.http_client import SyncHTTPClient
from workos.utils.request_helper import REQUEST_METHOD_POST
from workos.utils.validation import PORTAL_MODULE, validate_settings


PORTAL_GENERATE_PATH = "portal/generate_link"


class PortalModule(Protocol):
    def generate_link(
        self,
        intent: PortalLinkIntent,
        organization_id: str,
        return_url: Optional[str] = None,
        success_url: Optional[str] = None,
    ) -> PortalLink: ...


class Portal(PortalModule):

    _http_client: SyncHTTPClient

    @validate_settings(PORTAL_MODULE)
    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def generate_link(
        self,
        intent: PortalLinkIntent,
        organization_id: str,
        return_url: Optional[str] = None,
        success_url: Optional[str] = None,
    ) -> PortalLink:
        """Generate a link to grant access to an organization's Admin Portal

        Args:
            intent (str): The access scope for the generated Admin Portal link. Valid values are: ["audit_logs", "dsync", "log_streams", "sso",]
            organization_id (string): The ID of the organization the Admin Portal link will be generated for

        Kwargs:
            return_url (str): The URL that the end user will be redirected to upon exiting the generated Admin Portal. If none is provided, the default redirect link set in your WorkOS Dashboard will be used. (Optional)
            success_url (str): The URL to which WorkOS will redirect users to upon successfully viewing Audit Logs, setting up Log Streams, Single Sign On or Directory Sync. (Optional)

        Returns:
            PortalLink: PortalLink object with URL to redirect a User to to access an Admin Portal session
        """
        params = {
            "intent": intent,
            "organization": organization_id,
            "return_url": return_url,
            "success_url": success_url,
        }
        response = self._http_client.request(
            PORTAL_GENERATE_PATH,
            method=REQUEST_METHOD_POST,
            params=params,
            token=workos.api_key,
        )

        return PortalLink.model_validate(response)
