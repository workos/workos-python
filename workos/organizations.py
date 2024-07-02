from warnings import warn
import workos
from workos.utils.pagination_order import Order
from workos.utils.request import (
    RequestHelper,
    REQUEST_METHOD_DELETE,
    REQUEST_METHOD_GET,
    REQUEST_METHOD_POST,
    REQUEST_METHOD_PUT,
)
from workos.utils.validation import ORGANIZATIONS_MODULE, validate_settings
from workos.resources.organizations import WorkOSOrganization
from workos.resources.list import WorkOSListResource

ORGANIZATIONS_PATH = "organizations"
RESPONSE_LIMIT = 10


class Organizations(WorkOSListResource):
    @validate_settings(ORGANIZATIONS_MODULE)
    def __init__(self):
        pass

    @property
    def request_helper(self):
        if not getattr(self, "_request_helper", None):
            self._request_helper = RequestHelper()
        return self._request_helper

    def list_organizations(
        self,
        domains=None,
        limit=None,
        before=None,
        after=None,
        order=None,
    ):
        """Retrieve a list of organizations that have connections configured within your WorkOS dashboard.

        Kwargs:
            domains (list): Filter organizations to only return those that are associated with the provided domains. (Optional)
            limit (int): Maximum number of records to return. (Optional)
            before (str): Pagination cursor to receive records before a provided Organization ID. (Optional)
            after (str): Pagination cursor to receive records after a provided Organization ID. (Optional)
            order (Order): Sort records in either ascending or descending order by created_at timestamp.

        Returns:
            dict: Organizations response from WorkOS.
        """
        warn(
            "The 'list_organizations' method is deprecated. Please use 'list_organizations_v2' instead.",
            DeprecationWarning,
        )
        if limit is None:
            limit = RESPONSE_LIMIT
            default_limit = True

        params = {
            "domains": domains,
            "limit": limit,
            "before": before,
            "after": after,
            "order": order or "desc",
        }

        if order is not None:
            if isinstance(order, Order):
                params["order"] = str(order.value)

            elif order == "asc" or order == "desc":
                params["order"] = order
            else:
                raise ValueError("Parameter order must be of enum type Order")

        response = self.request_helper.request(
            ORGANIZATIONS_PATH,
            method=REQUEST_METHOD_GET,
            params=params,
            token=workos.api_key,
        )

        response["metadata"] = {
            "params": params,
            "method": Organizations.list_organizations,
        }

        if "default_limit" in locals():
            if "metadata" in response and "params" in response["metadata"]:
                response["metadata"]["params"]["default_limit"] = default_limit
            else:
                response["metadata"] = {"params": {"default_limit": default_limit}}

        return response

    def list_organizations_v2(
        self,
        domains=None,
        limit=None,
        before=None,
        after=None,
        order=None,
    ):
        """Retrieve a list of organizations that have connections configured within your WorkOS dashboard.

        Kwargs:
            domains (list): Filter organizations to only return those that are associated with the provided domains. (Optional)
            limit (int): Maximum number of records to return. (Optional)
            before (str): Pagination cursor to receive records before a provided Organization ID. (Optional)
            after (str): Pagination cursor to receive records after a provided Organization ID. (Optional)
            order (Order): Sort records in either ascending or descending order by created_at timestamp.

        Returns:
            dict: Organizations response from WorkOS.
        """

        if limit is None:
            limit = RESPONSE_LIMIT
            default_limit = True

        params = {
            "domains": domains,
            "limit": limit,
            "before": before,
            "after": after,
            "order": order or "desc",
        }

        if order is not None:
            if isinstance(order, Order):
                params["order"] = str(order.value)

            elif order == "asc" or order == "desc":
                params["order"] = order
            else:
                raise ValueError("Parameter order must be of enum type Order")

        response = self.request_helper.request(
            ORGANIZATIONS_PATH,
            method=REQUEST_METHOD_GET,
            params=params,
            token=workos.api_key,
        )

        response["metadata"] = {
            "params": params,
            "method": Organizations.list_organizations_v2,
        }

        if "default_limit" in locals():
            if "metadata" in response and "params" in response["metadata"]:
                response["metadata"]["params"]["default_limit"] = default_limit
            else:
                response["metadata"] = {"params": {"default_limit": default_limit}}

        return self.construct_from_response(response)

    def get_organization(self, organization):
        """Gets details for a single Organization
        Args:
            organization (str): Organization's unique identifier
        Returns:
            dict: Organization response from WorkOS
        """
        response = self.request_helper.request(
            "organizations/{organization}".format(organization=organization),
            method=REQUEST_METHOD_GET,
            token=workos.api_key,
        )

        return WorkOSOrganization.construct_from_response(response).to_dict()

    def get_organization_by_lookup_key(self, lookup_key):
        """Gets details for a single Organization by lookup key
        Args:
            lookup_key (str): Organization's lookup key
        Returns:
            dict: Organization response from WorkOS
        """
        response = self.request_helper.request(
            "organizations/by_lookup_key/{lookup_key}".format(lookup_key=lookup_key),
            method=REQUEST_METHOD_GET,
            token=workos.api_key,
        )

        return WorkOSOrganization.construct_from_response(response).to_dict()

    def create_organization(self, organization, idempotency_key=None):
        """Create an organization

        Args:
            organization (dict) - An organization object
                organization[name] (str) - A unique, descriptive name for the organization
                organization[allow_profiles_outside_organization] (boolean) - [Deprecated] Whether Connections
                    within the Organization allow profiles that are outside of the Organization's
                    configured User Email Domains. (Optional)
                organization[domains] (list[dict]) - [Deprecated] Use domain_data instead. List of domains that
                    belong to the organization. (Optional)
                organization[domain_data] (list[dict]) - List of domains that belong to the organization.
                    organization[domain_data][][domain] - The domain of the organization.
                    organization[domain_data][][state] - The state of the domain: either 'verified' or 'pending'.
            idempotency_key (str) - Idempotency key for creating an organization. (Optional)

        Returns:
            dict: Created Organization response from WorkOS.
        """
        headers = {}
        if idempotency_key:
            headers["idempotency-key"] = idempotency_key

        if "domains" in organization:
            warn(
                "The 'domains' parameter for 'create_organization' is deprecated. Please use 'domain_data' instead.",
                DeprecationWarning,
            )

        if "allow_profiles_outside_organization" in organization:
            warn(
                "The `allow_profiles_outside_organization` parameter for `create_orgnaization` is deprecated. "
                "If you need to allow sign-ins from any email domain, contact support@workos.com.",
                DeprecationWarning,
            )

        response = self.request_helper.request(
            ORGANIZATIONS_PATH,
            method=REQUEST_METHOD_POST,
            params=organization,
            headers=headers,
            token=workos.api_key,
        )

        return WorkOSOrganization.construct_from_response(response).to_dict()

    def update_organization(
        self,
        organization,
        name,
        allow_profiles_outside_organization=None,
        domains=None,
        domain_data=None,
        lookup_key=None,
    ):
        """Update an organization

        Args:
            organization(str) - Organization's unique identifier.
            name (str) - A unique, descriptive name for the organization.
            allow_profiles_outside_organization (boolean) - [Deprecated] Whether Connections
                within the Organization allow profiles that are outside of the Organization's
                configured User Email Domains. (Optional)
            domains (list) - [Deprecated] Use domain_data instead. List of domains that belong to the organization. (Optional)
            domain_data (list[dict]) - List of domains that belong to the organization. (Optional)
                domain_data[][domain] - The domain of the organization.
                domain_data[][state] - The state of the domain: either 'verified' or 'pending'.

        Returns:
            dict: Updated Organization response from WorkOS.
        """

        params = {"name": name}

        if domains is not None:
            warn(
                "The 'domains' parameter for 'update_organization' is deprecated. Please use 'domain_data' instead.",
                DeprecationWarning,
            )
            params["domains"] = domains

        if allow_profiles_outside_organization is not None:
            warn(
                "The `allow_profiles_outside_organization` parameter for `create_orgnaization` is deprecated. "
                "If you need to allow sign-ins from any email domain, contact support@workos.com.",
                DeprecationWarning,
            )
            params[
                "allow_profiles_outside_organization"
            ] = allow_profiles_outside_organization

        if domain_data is not None:
            params["domain_data"] = domain_data

        if lookup_key is not None:
            params["lookup_key"] = lookup_key

        response = self.request_helper.request(
            "organizations/{organization}".format(organization=organization),
            method=REQUEST_METHOD_PUT,
            params=params,
            token=workos.api_key,
        )

        return WorkOSOrganization.construct_from_response(response).to_dict()

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
