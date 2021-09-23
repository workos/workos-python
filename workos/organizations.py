import workos
from workos.utils.request import (
    RequestHelper,
    REQUEST_METHOD_DELETE,
    REQUEST_METHOD_GET,
    REQUEST_METHOD_POST,
    REQUEST_METHOD_PUT,
)
from workos.utils.validation import ORGANIZATIONS_MODULE, validate_settings

ORGANIZATIONS_PATH = "organizations"
RESPONSE_LIMIT = 10


class Organizations(object):
    @validate_settings(ORGANIZATIONS_MODULE)
    def __init__(self):
        pass

    @property
    def request_helper(self):
        if not getattr(self, "_request_helper", None):
            self._request_helper = RequestHelper()
        return self._request_helper

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

    def get_organization(self, organization):
        """Gets details for a single Organization
        Args:
            organization (str): Organization's unique identifier
        Returns:
            dict: Organization response from WorkOS
        """
        return self.request_helper.request(
            "organizations/{organization}".format(organization=organization),
            method=REQUEST_METHOD_GET,
            token=workos.api_key,
        )

    def create_organization(self, organization):
        """Create an organization

        Args:
            organization (dict) - An organization object
                organization[name] (str) - A unique, descriptive name for the organization
                organization[allow_profiles_outside_organization] (boolean) - Whether Connections
                    within the Organization allow profiles that are outside of the Organization's
                    configured User Email Domains. (Optional)
                organization[domains] (list) - List of domains that belong to the organization

        Returns:
            dict: Created Organization response from WorkOS.
        """
        return self.request_helper.request(
            ORGANIZATIONS_PATH,
            method=REQUEST_METHOD_POST,
            params=organization,
            token=workos.api_key,
        )

    def update_organization(self, organization, name, domains=None):
        """Update an organization

        Args:
            organization(str) - Organization's unique identifier.
            name (str) - A unique, descriptive name for the organization.
            organization[allow_profiles_outside_organization] (boolean) - Whether Connections
                    within the Organization allow profiles that are outside of the Organization's
                    configured User Email Domains. (Optional)
            domains (list) - List of domains that belong to the organization. (Optional)

        Returns:
            dict: Updated Organization response from WorkOS.
        """
        params = {
            "domains": domains,
            "name": name,
        }
        return self.request_helper.request(
            "organizations/{organization}".format(organization=organization),
            method=REQUEST_METHOD_PUT,
            params=params,
            token=workos.api_key,
        )

    def delete_organization(self, organization):
        """Deletes a single Organization

        Args:
            organization (str): Organization unique identifier
        """
        return self.request_helper.request(
            "organizations/{organization}".format(organization=organization),
            method=REQUEST_METHOD_DELETE,
            token=workos.api_key,
        )
