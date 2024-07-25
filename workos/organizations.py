from typing import List, Optional, Protocol
import workos
from workos.utils.pagination_order import PaginationOrder
from workos.utils.request import (
    DEFAULT_LIST_RESPONSE_LIMIT,
    RequestHelper,
    REQUEST_METHOD_DELETE,
    REQUEST_METHOD_GET,
    REQUEST_METHOD_POST,
    REQUEST_METHOD_PUT,
)
from workos.utils.validation import ORGANIZATIONS_MODULE, validate_settings
from workos.resources.organizations import (
    Organization,
    DomainDataInput,
)
from workos.resources.list import ListPage, WorkOsListResource, ListArgs

ORGANIZATIONS_PATH = "organizations"


class OrganizationListFilters(ListArgs, total=False):
    domains: Optional[List[str]]


class OrganizationsModule(Protocol):
    def list_organizations(
        self,
        domains: Optional[List[str]] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> WorkOsListResource[Organization, OrganizationListFilters]:
        ...

    def get_organization(self, organization: str) -> Organization:
        ...

    def get_organization_by_lookup_key(self, lookup_key: str) -> Organization:
        ...

    def create_organization(
        self,
        name: str,
        domain_data: Optional[List[DomainDataInput]] = None,
        idempotency_key: Optional[str] = None,
    ) -> Organization:
        ...

    def update_organization(
        self,
        organization: str,
        name: str,
        domain_data: Optional[List[DomainDataInput]] = None,
    ) -> Organization:
        ...

    def delete_organization(self, organization: str) -> None:
        ...


class Organizations(OrganizationsModule):
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
        domains: Optional[List[str]] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> WorkOsListResource[Organization, OrganizationListFilters]:
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

        list_params: OrganizationListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
            "domains": domains,
        }

        response = self.request_helper.request(
            ORGANIZATIONS_PATH,
            method=REQUEST_METHOD_GET,
            params=list_params,
            token=workos.api_key,
        )

        return WorkOsListResource[Organization, OrganizationListFilters](
            list_method=self.list_organizations,
            list_args=list_params,
            **ListPage[Organization](**response).model_dump()
        )

    def get_organization(self, organization: str) -> Organization:
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

        return Organization.model_validate(response)

    def get_organization_by_lookup_key(self, lookup_key: str) -> Organization:
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

        return Organization.model_validate(response)

    def create_organization(
        self,
        name: str,
        domain_data: Optional[List[DomainDataInput]] = None,
        idempotency_key: Optional[str] = None,
    ) -> Organization:
        """Create an organization"""
        headers = {}
        if idempotency_key:
            headers["idempotency-key"] = idempotency_key

        params = {
            "name": name,
            "domain_data": domain_data,
            "idempotency_key": idempotency_key,
        }

        response = self.request_helper.request(
            ORGANIZATIONS_PATH,
            method=REQUEST_METHOD_POST,
            params=params,
            headers=headers,
            token=workos.api_key,
        )

        return Organization.model_validate(response)

    def update_organization(
        self,
        organization: str,
        name: str,
        domain_data: Optional[List[DomainDataInput]] = None,
    ):
        params = {
            "name": name,
            "domain_data": domain_data,
        }

        response = self.request_helper.request(
            "organizations/{organization}".format(organization=organization),
            method=REQUEST_METHOD_PUT,
            params=params,
            token=workos.api_key,
        )

        return Organization.model_validate(response)

    def delete_organization(self, organization: str):
        """Deletes a single Organization

        Args:
            organization (str): Organization unique identifier
        """
        return self.request_helper.request(
            "organizations/{organization}".format(organization=organization),
            method=REQUEST_METHOD_DELETE,
            token=workos.api_key,
        )
