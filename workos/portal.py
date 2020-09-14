import workos
from workos.utils.request import RequestHelper, REQUEST_METHOD_GET, REQUEST_METHOD_POST
from workos.utils.validation import PORTAL_MODULE, validate_settings

ORGANIZATIONS_PATH = "organizations"
PORTAL_GENERATE_PATH = "portal/generate_link"
RESPONSE_LIMIT = 10


class Portal(object):
    @validate_settings(PORTAL_MODULE)
    def __init__(self):
        pass

    @property
    def request_helper(self):
        if not getattr(self, "_request_helper", None):
            self._request_helper = RequestHelper()
        return self._request_helper

    def create_organization(self, organization):
        """Create an organization

        Args:
            organization (dict) - An organization object
                organization[domains] (list) - List of domains that belong to the organization
                organization[name] (str) - A unique, descriptive name for the organization

        Returns:
            dict: Created Organization response from WorkOS.
        """
        return self.request_helper.request(
            ORGANIZATIONS_PATH,
            method=REQUEST_METHOD_POST,
            params=organization,
            token=workos.api_key,
        )

    def generate_link(self, intent, organization, return_url=None):
        """Generate a link to grant access to an organization's Admin Portal

        Args:
            intent (str): The access scope for the generated Admin Portal link. Valid values are: ["sso"]
            organization (string): The ID of the organization the Admin Portal link will be generated for

        Kwargs:
            return_url (str): The URL that the end user will be redirected to upon exiting the generated Admin Portal. If none is provided, the default redirect link set in your WorkOS Dashboard will be used. (Optional)

        Returns:
            str:  URL to redirect a User to to access an Admin Portal session
        """
        params = {
            "intent": intent,
            "organization": organization,
            "return_url": return_url,
        }
        return self.request_helper.request(
            PORTAL_GENERATE_PATH,
            method=REQUEST_METHOD_POST,
            params=params,
            token=workos.api_key,
        )

    def list_organizations(
        self, domains=None, limit=RESPONSE_LIMIT, before=None, after=None
    ):
        """Retrieve a list of organizations that have connections configured within your WorkOS dashboard.

        Kwargs:
            domains (list): Filter organizations to only return those that are associated with the provided domains. (Optional)
            limit (int): Maximum number of records to return. (Optional)
            before (str): Pagination cursor to receive records before a provided Organization ID. (Optional)
            after (str): Pagination cursor to receive records after a provided Organization ID. (Optional)

        Returns:
            dict: Organizations response from WorkOS.
        """
        params = {
            "domains": domains,
            "limit": limit,
            "before": before,
            "after": after,
        }
        return self.request_helper.request(
            ORGANIZATIONS_PATH,
            method=REQUEST_METHOD_GET,
            params=params,
            token=workos.api_key,
        )
