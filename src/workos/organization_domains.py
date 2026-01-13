from typing import Protocol
from workos._client_configuration import ClientConfiguration
from workos.types.organization_domains import OrganizationDomain
from workos.typing.sync_or_async import SyncOrAsync
from workos.utils.http_client import AsyncHTTPClient, SyncHTTPClient
from workos.utils.request_helper import (
    REQUEST_METHOD_DELETE,
    REQUEST_METHOD_GET,
    REQUEST_METHOD_POST,
)


class OrganizationDomainsModule(Protocol):
    """Offers methods for managing organization domains."""

    _client_configuration: ClientConfiguration

    def get_organization_domain(
        self, organization_domain_id: str
    ) -> SyncOrAsync[OrganizationDomain]:
        """Gets a single Organization Domain

        Args:
            organization_domain_id (str): Organization Domain unique identifier

        Returns:
            OrganizationDomain: Organization Domain response from WorkOS
        """
        ...

    def create_organization_domain(
        self,
        organization_id: str,
        domain: str,
    ) -> SyncOrAsync[OrganizationDomain]:
        """Creates an Organization Domain

        Args:
            organization_id (str): Organization unique identifier
            domain (str): Domain to be added to the organization

        Returns:
            OrganizationDomain: Organization Domain response from WorkOS
        """
        ...

    def verify_organization_domain(
        self, organization_domain_id: str
    ) -> SyncOrAsync[OrganizationDomain]:
        """Verifies an Organization Domain

        Args:
            organization_domain_id (str): Organization Domain unique identifier

        Returns:
            OrganizationDomain: Organization Domain response from WorkOS
        """
        ...

    def delete_organization_domain(
        self, organization_domain_id: str
    ) -> SyncOrAsync[None]:
        """Deletes a single Organization Domain

        Args:
            organization_domain_id (str): Organization Domain unique identifier

        Returns:
            None
        """
        ...


class OrganizationDomains:
    """Offers methods for managing organization domains."""

    _http_client: SyncHTTPClient
    _client_configuration: ClientConfiguration

    def __init__(
        self,
        http_client: SyncHTTPClient,
        client_configuration: ClientConfiguration,
    ):
        self._http_client = http_client
        self._client_configuration = client_configuration

    def get_organization_domain(
        self, organization_domain_id: str
    ) -> OrganizationDomain:
        response = self._http_client.request(
            f"organization_domains/{organization_domain_id}",
            method=REQUEST_METHOD_GET,
        )

        return OrganizationDomain.model_validate(response)

    def create_organization_domain(
        self,
        organization_id: str,
        domain: str,
    ) -> OrganizationDomain:
        response = self._http_client.request(
            "organization_domains",
            method=REQUEST_METHOD_POST,
            json={"organization_id": organization_id, "domain": domain},
        )

        return OrganizationDomain.model_validate(response)

    def verify_organization_domain(
        self, organization_domain_id: str
    ) -> OrganizationDomain:
        response = self._http_client.request(
            f"organization_domains/{organization_domain_id}/verify",
            method=REQUEST_METHOD_POST,
        )

        return OrganizationDomain.model_validate(response)

    def delete_organization_domain(self, organization_domain_id: str) -> None:
        self._http_client.request(
            f"organization_domains/{organization_domain_id}",
            method=REQUEST_METHOD_DELETE,
        )


class AsyncOrganizationDomains:
    """Offers async methods for managing organization domains."""

    _http_client: AsyncHTTPClient
    _client_configuration: ClientConfiguration

    def __init__(
        self,
        http_client: AsyncHTTPClient,
        client_configuration: ClientConfiguration,
    ):
        self._http_client = http_client
        self._client_configuration = client_configuration

    async def get_organization_domain(
        self, organization_domain_id: str
    ) -> OrganizationDomain:
        response = await self._http_client.request(
            f"organization_domains/{organization_domain_id}",
            method=REQUEST_METHOD_GET,
        )

        return OrganizationDomain.model_validate(response)

    async def create_organization_domain(
        self,
        organization_id: str,
        domain: str,
    ) -> OrganizationDomain:
        response = await self._http_client.request(
            "organization_domains",
            method=REQUEST_METHOD_POST,
            json={"organization_id": organization_id, "domain": domain},
        )

        return OrganizationDomain.model_validate(response)

    async def verify_organization_domain(
        self, organization_domain_id: str
    ) -> OrganizationDomain:
        response = await self._http_client.request(
            f"organization_domains/{organization_domain_id}/verify",
            method=REQUEST_METHOD_POST,
        )

        return OrganizationDomain.model_validate(response)

    async def delete_organization_domain(self, organization_domain_id: str) -> None:
        await self._http_client.request(
            f"organization_domains/{organization_domain_id}",
            method=REQUEST_METHOD_DELETE,
        )
