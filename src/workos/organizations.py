from typing import Optional, Protocol, Sequence

from workos.types.feature_flags import FeatureFlag
from workos.types.feature_flags.list_filters import FeatureFlagListFilters
from workos.types.metadata import Metadata
from workos.types.organizations.domain_data_input import DomainDataInput
from workos.types.organizations.list_filters import OrganizationListFilters
from workos.types.roles.role import RoleList
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

FeatureFlagsListResource = WorkOSListResource[
    FeatureFlag, FeatureFlagListFilters, ListMetadata
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

    def get_organization_by_external_id(
        self, external_id: str
    ) -> SyncOrAsync[Organization]:
        """Gets details for a single Organization by external id

        Args:
            external_id (str): Organization's external id

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
        external_id: Optional[str] = None,
        metadata: Optional[Metadata] = None,
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
        external_id: Optional[str] = None,
        metadata: Optional[Metadata] = None,
    ) -> SyncOrAsync[Organization]:
        """Update an organization

        Kwargs:
            organization (str): Organization's unique identifier.
            name (str): A descriptive name for the organization. (Optional)
            domain_data (Sequence[DomainDataInput]): List of domains that belong to the organization. (Optional)
            stripe_customer_id (str): The ID of the Stripe customer associated with the organization. (Optional)

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

    def list_feature_flags(
        self,
        organization_id: str,
        *,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> SyncOrAsync[FeatureFlagsListResource]:
        """Retrieve a list of feature flags for an organization

        Args:
            organization_id (str): Organization's unique identifier
            limit (int): Maximum number of records to return. (Optional)
            before (str): Pagination cursor to receive records before a provided Feature Flag ID. (Optional)
            after (str): Pagination cursor to receive records after a provided Feature Flag ID. (Optional)
            order (Literal["asc","desc"]): Sort records in either ascending or descending (default) order by created_at timestamp. (Optional)

        Returns:
            FeatureFlagsListResource: Feature flags list response from WorkOS.
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

    def get_organization_by_external_id(self, external_id: str) -> Organization:
        response = self._http_client.request(
            "organizations/external_id/{external_id}".format(external_id=external_id),
            method=REQUEST_METHOD_GET,
        )

        return Organization.model_validate(response)

    def create_organization(
        self,
        *,
        name: str,
        domain_data: Optional[Sequence[DomainDataInput]] = None,
        idempotency_key: Optional[str] = None,
        external_id: Optional[str] = None,
        metadata: Optional[Metadata] = None,
    ) -> Organization:
        headers = {}
        if idempotency_key:
            headers["idempotency-key"] = idempotency_key

        json = {
            "name": name,
            "domain_data": domain_data,
            "idempotency_key": idempotency_key,
            "external_id": external_id,
            "metadata": metadata,
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
        stripe_customer_id: Optional[str] = None,
        external_id: Optional[str] = None,
        metadata: Optional[Metadata] = None,
    ) -> Organization:
        json = {
            "name": name,
            "domain_data": domain_data,
            "stripe_customer_id": stripe_customer_id,
            "external_id": external_id,
            "metadata": metadata,
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

    def list_organization_roles(self, organization_id: str) -> RoleList:
        response = self._http_client.request(
            f"organizations/{organization_id}/roles",
            method=REQUEST_METHOD_GET,
        )

        return RoleList.model_validate(response)

    def list_feature_flags(
        self,
        organization_id: str,
        *,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> FeatureFlagsListResource:
        list_params: FeatureFlagListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        response = self._http_client.request(
            f"organizations/{organization_id}/feature-flags",
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        return WorkOSListResource[FeatureFlag, FeatureFlagListFilters, ListMetadata](
            list_method=self.list_feature_flags,
            list_args=list_params,
            **ListPage[FeatureFlag](**response).model_dump(),
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

    async def get_organization_by_external_id(self, external_id: str) -> Organization:
        response = await self._http_client.request(
            "organizations/external_id/{external_id}".format(external_id=external_id),
            method=REQUEST_METHOD_GET,
        )

        return Organization.model_validate(response)

    async def create_organization(
        self,
        *,
        name: str,
        domain_data: Optional[Sequence[DomainDataInput]] = None,
        idempotency_key: Optional[str] = None,
        external_id: Optional[str] = None,
        metadata: Optional[Metadata] = None,
    ) -> Organization:
        headers = {}
        if idempotency_key:
            headers["idempotency-key"] = idempotency_key

        json = {
            "name": name,
            "domain_data": domain_data,
            "idempotency_key": idempotency_key,
            "external_id": external_id,
            "metadata": metadata,
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
        stripe_customer_id: Optional[str] = None,
        external_id: Optional[str] = None,
        metadata: Optional[Metadata] = None,
    ) -> Organization:
        json = {
            "name": name,
            "domain_data": domain_data,
            "stripe_customer_id": stripe_customer_id,
            "external_id": external_id,
            "metadata": metadata,
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

    async def list_organization_roles(self, organization_id: str) -> RoleList:
        response = await self._http_client.request(
            f"organizations/{organization_id}/roles",
            method=REQUEST_METHOD_GET,
        )

        return RoleList.model_validate(response)

    async def list_feature_flags(
        self,
        organization_id: str,
        *,
        limit: int = DEFAULT_LIST_RESPONSE_LIMIT,
        before: Optional[str] = None,
        after: Optional[str] = None,
        order: PaginationOrder = "desc",
    ) -> FeatureFlagsListResource:
        list_params: FeatureFlagListFilters = {
            "limit": limit,
            "before": before,
            "after": after,
            "order": order,
        }

        response = await self._http_client.request(
            f"organizations/{organization_id}/feature-flags",
            method=REQUEST_METHOD_GET,
            params=list_params,
        )

        return WorkOSListResource[FeatureFlag, FeatureFlagListFilters, ListMetadata](
            list_method=self.list_feature_flags,
            list_args=list_params,
            **ListPage[FeatureFlag](**response).model_dump(),
        )
