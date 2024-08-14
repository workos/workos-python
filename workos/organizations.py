from typing import Optional, Protocol, Sequence

from workos.types.organizations.domain_data_input import DomainDataInput
from workos.types.organizations.list_filters import OrganizationListFilters
from workos.typing.sync_or_async import SyncOrAsync
from workos.utils.http_client import AsyncHTTPClient, SyncHTTPClient
from workos.utils.pagination_order import PaginationOrder
from workos.utils.request_helper import (
    DEFAULT_LIST_RESPONSE_LIMIT,
    REQUEST_METHOD_DELETE,
    REQUEST_METHOD_GET,
    REQUEST_METHOD_POST,
    REQUEST_METHOD_PUT,
)
from workos.types.organizations import Organization
from workos.types.list_resource import ListMetadata, ListPage, WorkOSListResource

ORGANIZATIONS_PATH = "organizations"


OrganizationsListResource = WorkOSListResource[
    Organization, OrganizationListFilters, ListMetadata
]


class OrganizationsModule(Protocol):
    """Offers methods through the WorkOS Organizations service."""

    def list_organizations(
        self,
        *,
        domains: Optional[Sequence[str]] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> SyncOrAsync[OrganizationsListResource]:
        """Retrieve a list of organizations that have connections configured within your WorkOS dashboard.

        Kwargs:
            domains (list): Filter organizations to only return those that are associated with the provided domains. (Optional)
            limit (int): Maximum number of records to return. (Optional)
            before (str): Pagination cursor to receive records before a provided Organization ID. (Optional)
            after (str): Pagination cursor to receive records after a provided Organization ID. (Optional)
            order (Literal["asc","desc"]): Sort records in either ascending or descending (default) order by created_at timestamp. (Optional)

        Returns:
            OrganizationsListResource: Organizations list response from WorkOS.
        """
        ...

    def get_organization(self, organization_id: str) -> SyncOrAsync[Organization]:
        """Gets details for a single Organization

        Args:
            organization_id (str): Organization's unique identifier
        Returns:
            Organization: Organization response from WorkOS
        """
        ...

    def get_organization_by_lookup_key(
        self, lookup_key: str
    ) -> SyncOrAsync[Organization]:
        """Gets details for a single Organization by lookup key

        Args:
            lookup_key (str): Organization's lookup key

        Returns:
            Organization: Organization response from WorkOS
        """
        ...

    def create_organization(
        self,
        *,
        name: str,
        domain_data: Optional[Sequence[DomainDataInput]] = None,
        idempotency_key: Optional[str] = None,
    ) -> SyncOrAsync[Organization]:
        """Create an organization

        Kwargs:
            name (str): A descriptive name for the organization. (Optional)
            domain_data (Sequence[DomainDataInput]): List of domains that belong to the organization. (Optional)
            idempotency_key (str): Key to guarantee idempotency across requests. (Optional)

        Returns:
            Organization: Updated Organization response from WorkOS.
        """
        ...

    def update_organization(
        self,
        *,
        organization_id: str,
        name: Optional[str] = None,
        domain_data: Optional[Sequence[DomainDataInput]] = None,
    ) -> SyncOrAsync[Organization]:
        """Update an organization

        Kwargs:
            organization (str): Organization's unique identifier.
            name (str): A descriptive name for the organization. (Optional)
            domain_data (Sequence[DomainDataInput]): List of domains that belong to the organization. (Optional)

        Returns:
            Organization: Updated Organization response from WorkOS.
        """
        ...

    def delete_organization(self, organization_id: str) -> SyncOrAsync[None]:
        """Deletes a single Organization

        Args:
            organization_id (str): Organization unique identifier

        Returns:
            None
        """
        ...


class Organizations(OrganizationsModule):

    _http_client: SyncHTTPClient

    def __init__(self, http_client: SyncHTTPClient):
        self._http_client = http_client

    def list_organizations(
        self,
        *,
        domains: Optional[Sequence[str]] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> OrganizationsListResource:
        list_params: OrganizationListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
            "domains": domains,
        }

        response = self._http_client.request(
            ORGANIZATIONS_PATH,
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        return WorkOSListResource[Organization, OrganizationListFilters, ListMetadata](
            list_method=self.list_organizations,
            list_args=list_params,
            **ListPage[Organization](**response).model_dump(),
        )

    def get_organization(self, organization_id: str) -> Organization:
        response = self._http_client.request(
            f"organizations/{organization_id}", method=REQUEST_METHOD_GET
        )

        return Organization.model_validate(response)

    def get_organization_by_lookup_key(self, lookup_key: str) -> Organization:
        response = self._http_client.request(
            "organizations/by_lookup_key/{lookup_key}".format(lookup_key=lookup_key),
            method=REQUEST_METHOD_GET,
        )

        return Organization.model_validate(response)

    def create_organization(
        self,
        *,
        name: str,
        domain_data: Optional[Sequence[DomainDataInput]] = None,
        idempotency_key: Optional[str] = None,
    ) -> Organization:
        headers = {}
        if idempotency_key:
            headers["idempotency-key"] = idempotency_key

        json = {
            "name": name,
            "domain_data": domain_data,
            "idempotency_key": idempotency_key,
        }

        response = self._http_client.request(
            ORGANIZATIONS_PATH,
            method=REQUEST_METHOD_POST,
            json=json,
            headers=headers,
        )

        return Organization.model_validate(response)

    def update_organization(
        self,
        *,
        organization_id: str,
        name: Optional[str] = None,
        domain_data: Optional[Sequence[DomainDataInput]] = None,
    ) -> Organization:
        json = {
            "name": name,
            "domain_data": domain_data,
        }

        response = self._http_client.request(
            f"organizations/{organization_id}", method=REQUEST_METHOD_PUT, json=json
        )

        return Organization.model_validate(response)

    def delete_organization(self, organization_id: str) -> None:
        self._http_client.request(
            f"organizations/{organization_id}",
            method=REQUEST_METHOD_DELETE,
        )


class AsyncOrganizations(OrganizationsModule):

    _http_client: AsyncHTTPClient

    def __init__(self, http_client: AsyncHTTPClient):
        self._http_client = http_client

    async def list_organizations(
        self,
        *,
        domains: Optional[Sequence[str]] = None,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> OrganizationsListResource:
        list_params: OrganizationListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
            "domains": domains,
        }

        response = await self._http_client.request(
            ORGANIZATIONS_PATH,
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        return WorkOSListResource[Organization, OrganizationListFilters, ListMetadata](
            list_method=self.list_organizations,
            list_args=list_params,
            **ListPage[Organization](**response).model_dump(),
        )

    async def get_organization(self, organization_id: str) -> Organization:
        response = await self._http_client.request(
            f"organizations/{organization_id}", method=REQUEST_METHOD_GET
        )

        return Organization.model_validate(response)

    async def get_organization_by_lookup_key(self, lookup_key: str) -> Organization:
        response = await self._http_client.request(
            "organizations/by_lookup_key/{lookup_key}".format(lookup_key=lookup_key),
            method=REQUEST_METHOD_GET,
        )

        return Organization.model_validate(response)

    async def create_organization(
        self,
        *,
        name: str,
        domain_data: Optional[Sequence[DomainDataInput]] = None,
        idempotency_key: Optional[str] = None,
    ) -> Organization:
        headers = {}
        if idempotency_key:
            headers["idempotency-key"] = idempotency_key

        json = {
            "name": name,
            "domain_data": domain_data,
            "idempotency_key": idempotency_key,
        }

        response = await self._http_client.request(
            ORGANIZATIONS_PATH,
            method=REQUEST_METHOD_POST,
            json=json,
            headers=headers,
        )

        return Organization.model_validate(response)

    async def update_organization(
        self,
        *,
        organization_id: str,
        name: Optional[str] = None,
        domain_data: Optional[Sequence[DomainDataInput]] = None,
    ) -> Organization:
        json = {
            "name": name,
            "domain_data": domain_data,
        }

        response = await self._http_client.request(
            f"organizations/{organization_id}", method=REQUEST_METHOD_PUT, json=json
        )

        return Organization.model_validate(response)

    async def delete_organization(self, organization_id: str) -> None:
        await self._http_client.request(
            f"organizations/{organization_id}",
            method=REQUEST_METHOD_DELETE,
        )
