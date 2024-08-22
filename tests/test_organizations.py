import datetime
import pytest
from tests.types.test_auto_pagination_function import TestAutoPaginationFunction
from tests.utils.fixtures.mock_organization import MockOrganization
from tests.utils.list_resource import list_data_to_dicts, list_response_of
from workos.organizations import AsyncOrganizations, Organizations


class OrganizationFixtures:
    @pytest.fixture
    def mock_organization(self):
        return MockOrganization("org_01EHT88Z8J8795GZNQ4ZP1J81T").dict()

    @pytest.fixture
    def mock_organization_updated(self):
        return {
            "name": "Example Organization",
            "object": "organization",
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat(),
            "id": "org_01EHT88Z8J8795GZNQ4ZP1J81T",
            "allow_profiles_outside_organization": True,
            "domains": [
                {
                    "domain": "example.io",
                    "object": "organization_domain",
                    "id": "org_domain_01EHT88Z8WZEFWYPM6EC9BX2R8",
                    "state": "verified",
                    "organization_id": "org_01EHT88Z8J8795GZNQ4ZP1J81T",
                    "verification_strategy": "dns",
                    "verification_token": "token",
                }
            ],
        }

    @pytest.fixture
    def mock_organizations(self):
        organization_list = [MockOrganization(id=str(i)).dict() for i in range(10)]

        return {
            "data": organization_list,
            "list_metadata": {"before": None, "after": None},
            "object": "list",
        }

    @pytest.fixture
    def mock_organizations_single_page_response(self):
        organization_list = [MockOrganization(id=str(i)).dict() for i in range(10)]
        return {
            "data": organization_list,
            "list_metadata": {"before": None, "after": None},
            "object": "list",
        }

    @pytest.fixture
    def mock_organizations_multiple_data_pages(self):
        organizations_list = [
            MockOrganization(id=str(f"org_{i+1}")).dict() for i in range(40)
        ]
        return list_response_of(data=organizations_list)


class TestOrganizations(OrganizationFixtures):
    @pytest.fixture(autouse=True)
    def setup(self, sync_http_client_for_test):
        self.http_client = sync_http_client_for_test
        self.organizations = Organizations(http_client=self.http_client)

    def test_list_organizations(
        self, mock_organizations, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_organizations, 200
        )

        organizations_response = self.organizations.list_organizations()

        def to_dict(x):
            return x.dict()

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith("/organizations")
        assert (
            list(map(to_dict, organizations_response.data))
            == mock_organizations["data"]
        )

    def test_get_organization(
        self, mock_organization, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_organization, 200
        )

        organization = self.organizations.get_organization(
            organization_id="organization_id"
        )

        assert organization.dict() == mock_organization
        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith("/organizations/organization_id")

    def test_get_organization_by_lookup_key(
        self, mock_organization, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_organization, 200
        )

        organization = self.organizations.get_organization_by_lookup_key(
            lookup_key="test"
        )

        assert organization.dict() == mock_organization
        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith("/organizations/by_lookup_key/test")

    def test_create_organization_with_domain_data(
        self, mock_organization, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_organization, 201
        )

        payload = {
            "domain_data": [{"domain": "example.com", "state": "verified"}],
            "name": "Test Organization",
        }
        organization = self.organizations.create_organization(**payload)

        assert organization.id == "org_01EHT88Z8J8795GZNQ4ZP1J81T"
        assert organization.name == "Foo Corporation"
        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith("/organizations")
        assert request_kwargs["json"] == payload

    def test_sends_idempotency_key(
        self, mock_organization, capture_and_mock_http_client_request
    ):
        idempotency_key = "test_123456789"

        payload = {
            "domain_data": [{"domain": "example.com", "state": "verified"}],
            "name": "Foo Corporation",
        }

        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_organization, 200
        )

        response = self.organizations.create_organization(
            **payload, idempotency_key=idempotency_key
        )

        assert request_kwargs["headers"]["idempotency-key"] == idempotency_key
        assert response.name == "Foo Corporation"

    def test_update_organization_with_domain_data(
        self, mock_organization_updated, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_organization_updated, 201
        )

        updated_organization = self.organizations.update_organization(
            organization_id="org_01EHT88Z8J8795GZNQ4ZP1J81T",
            domain_data=[{"domain": "example.io", "state": "verified"}],
        )

        assert request_kwargs["url"].endswith(
            "/organizations/org_01EHT88Z8J8795GZNQ4ZP1J81T"
        )
        assert request_kwargs["method"] == "put"
        assert request_kwargs["json"] == {
            "domain_data": [{"domain": "example.io", "state": "verified"}]
        }
        assert updated_organization.id == "org_01EHT88Z8J8795GZNQ4ZP1J81T"
        assert updated_organization.name == "Example Organization"
        assert updated_organization.domains[0].dict() == {
            "domain": "example.io",
            "object": "organization_domain",
            "id": "org_domain_01EHT88Z8WZEFWYPM6EC9BX2R8",
            "state": "verified",
            "organization_id": "org_01EHT88Z8J8795GZNQ4ZP1J81T",
            "verification_strategy": "dns",
            "verification_token": "token",
        }

    def test_delete_organization(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client,
            202,
            headers={"content-type": "text/plain; charset=utf-8"},
        )

        response = self.organizations.delete_organization(
            organization_id="organization_id"
        )

        assert request_kwargs["url"].endswith("/organizations/organization_id")
        assert request_kwargs["method"] == "delete"
        assert response is None

    def test_list_organizations_auto_pagination_for_single_page(
        self,
        mock_organizations_single_page_response,
        capture_and_mock_pagination_request_for_http_client,
    ):
        request_kwargs = capture_and_mock_pagination_request_for_http_client(
            self.http_client, mock_organizations_single_page_response["data"], 200
        )

        all_organizations = []
        organizations = self.organizations.list_organizations()

        for org in organizations:
            all_organizations.append(org)

        assert len(list(all_organizations)) == 10

        organization_data = mock_organizations_single_page_response["data"]
        assert (list_data_to_dicts(all_organizations)) == organization_data
        assert request_kwargs["url"].endswith("/organizations")
        assert request_kwargs["method"] == "get"
        assert request_kwargs["params"] == {
            "after": "9",
            "limit": 10,
            "order": "desc",
        }

    def test_list_organizations_auto_pagination_for_multiple_pages(
        self,
        mock_organizations_multiple_data_pages,
        test_auto_pagination: TestAutoPaginationFunction,
    ):
        test_auto_pagination(
            http_client=self.http_client,
            list_function=self.organizations.list_organizations,
            expected_all_page_data=mock_organizations_multiple_data_pages["data"],
        )


@pytest.mark.asyncio
class TestAsyncOrganizations(OrganizationFixtures):
    @pytest.fixture(autouse=True)
    def setup(self, async_http_client_for_test):
        self.http_client = async_http_client_for_test
        self.organizations = AsyncOrganizations(http_client=self.http_client)

    async def test_list_organizations(
        self, mock_organizations, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_organizations, 200
        )

        organizations_response = await self.organizations.list_organizations()

        def to_dict(x):
            return x.dict()

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith("/organizations")
        assert (
            list(map(to_dict, organizations_response.data))
            == mock_organizations["data"]
        )

    async def test_get_organization(
        self, mock_organization, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_organization, 200
        )

        organization = await self.organizations.get_organization(
            organization_id="organization_id"
        )

        assert organization.dict() == mock_organization
        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith("/organizations/organization_id")

    async def test_get_organization_by_lookup_key(
        self, mock_organization, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_organization, 200
        )

        organization = await self.organizations.get_organization_by_lookup_key(
            lookup_key="test"
        )

        assert organization.dict() == mock_organization
        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith("/organizations/by_lookup_key/test")

    async def test_create_organization_with_domain_data(
        self, mock_organization, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_organization, 201
        )

        payload = {
            "domain_data": [{"domain": "example.com", "state": "verified"}],
            "name": "Test Organization",
        }
        organization = await self.organizations.create_organization(**payload)

        assert organization.id == "org_01EHT88Z8J8795GZNQ4ZP1J81T"
        assert organization.name == "Foo Corporation"
        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith("/organizations")
        assert request_kwargs["json"] == payload

    async def test_sends_idempotency_key(
        self, mock_organization, capture_and_mock_http_client_request
    ):
        idempotency_key = "test_123456789"

        payload = {
            "domain_data": [{"domain": "example.com", "state": "verified"}],
            "name": "Foo Corporation",
        }

        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_organization, 200
        )

        response = await self.organizations.create_organization(
            **payload, idempotency_key=idempotency_key
        )

        assert request_kwargs["headers"]["idempotency-key"] == idempotency_key
        assert response.name == "Foo Corporation"

    async def test_update_organization_with_domain_data(
        self, mock_organization_updated, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_organization_updated, 201
        )

        updated_organization = await self.organizations.update_organization(
            organization_id="org_01EHT88Z8J8795GZNQ4ZP1J81T",
            domain_data=[{"domain": "example.io", "state": "verified"}],
        )

        assert request_kwargs["url"].endswith(
            "/organizations/org_01EHT88Z8J8795GZNQ4ZP1J81T"
        )
        assert request_kwargs["method"] == "put"
        assert request_kwargs["json"] == {
            "domain_data": [{"domain": "example.io", "state": "verified"}]
        }
        assert updated_organization.id == "org_01EHT88Z8J8795GZNQ4ZP1J81T"
        assert updated_organization.name == "Example Organization"
        assert updated_organization.domains[0].dict() == {
            "domain": "example.io",
            "object": "organization_domain",
            "id": "org_domain_01EHT88Z8WZEFWYPM6EC9BX2R8",
            "state": "verified",
            "organization_id": "org_01EHT88Z8J8795GZNQ4ZP1J81T",
            "verification_strategy": "dns",
            "verification_token": "token",
        }

    async def test_delete_organization(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client,
            202,
            headers={"content-type": "text/plain; charset=utf-8"},
        )

        response = await self.organizations.delete_organization(
            organization_id="organization_id"
        )

        assert request_kwargs["url"].endswith("/organizations/organization_id")
        assert request_kwargs["method"] == "delete"
        assert response is None

    async def test_list_organizations_auto_pagination_for_single_page(
        self,
        mock_organizations_single_page_response,
        capture_and_mock_pagination_request_for_http_client,
    ):
        request_kwargs = capture_and_mock_pagination_request_for_http_client(
            self.http_client, mock_organizations_single_page_response["data"], 200
        )

        all_organizations = []
        organizations = await self.organizations.list_organizations()

        async for org in organizations:
            all_organizations.append(org)

        assert len(list(all_organizations)) == 10

        organization_data = mock_organizations_single_page_response["data"]
        assert (list_data_to_dicts(all_organizations)) == organization_data
        assert request_kwargs["url"].endswith("/organizations")
        assert request_kwargs["method"] == "get"
        assert request_kwargs["params"] == {
            "after": "9",
            "limit": 10,
            "order": "desc",
        }

    async def test_list_organizations_auto_pagination_for_multiple_pages(
        self,
        mock_organizations_multiple_data_pages,
        capture_and_mock_pagination_request_for_http_client,
    ):
        request_kwargs = capture_and_mock_pagination_request_for_http_client(
            http_client=self.http_client,
            data_list=mock_organizations_multiple_data_pages["data"],
            status_code=200,
        )

        all_organizations = []

        async for organization in await self.organizations.list_organizations():
            all_organizations.append(organization)

        assert len(list(all_organizations)) == len(
            mock_organizations_multiple_data_pages["data"]
        )
        assert (
            list_data_to_dicts(all_organizations)
        ) == mock_organizations_multiple_data_pages["data"]
        assert request_kwargs["url"].endswith("/organizations")
        assert request_kwargs["method"] == "get"
        assert request_kwargs["params"] == {
            "after": "org_40",
            "limit": 10,
            "order": "desc",
        }
