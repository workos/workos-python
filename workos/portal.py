import workos
from workos.utils.request import RequestHelper, REQUEST_METHOD_GET, REQUEST_METHOD_POST
from workos.utils.validation import PORTAL_MODULE, validate_settings

ORGANIZATIONS_PATH = "organizations"
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
