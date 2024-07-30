import datetime

import pytest

from tests.utils.list_resource import list_data_to_dicts, list_response_of
from workos.organizations import Organizations
from tests.utils.fixtures.mock_organization import MockOrganization
from workos.utils.http_client import SyncHTTPClient


class TestOrganizations(object):
    @pytest.fixture(autouse=True)
    def setup(self, set_api_key):
        self.http_client = SyncHTTPClient(
            base_url="https://api.workos.test", version="test"
        )
        self.organizations = Organizations(http_client=self.http_client)

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

    def test_list_organizations(
        self, mock_organizations, mock_http_client_with_response
    ):
        mock_http_client_with_response(self.http_client, mock_organizations, 200)

        organizations_response = self.organizations.list_organizations()

        def to_dict(x):
            return x.dict()

        assert (
            list(map(to_dict, organizations_response.data))
            == mock_organizations["data"]
        )

    def test_get_organization(self, mock_organization, mock_http_client_with_response):
        mock_http_client_with_response(self.http_client, mock_organization, 200)

        organization = self.organizations.get_organization(
            organization_id="organization_id"
        )

        assert organization.dict() == mock_organization

    def test_get_organization_by_lookup_key(
        self, mock_organization, mock_http_client_with_response
    ):
        mock_http_client_with_response(self.http_client, mock_organization, 200)

        organization = self.organizations.get_organization_by_lookup_key(
            lookup_key="test"
        )

        assert organization.dict() == mock_organization

    def test_create_organization_with_domain_data(
        self, mock_organization, mock_http_client_with_response
    ):
        mock_http_client_with_response(self.http_client, mock_organization, 201)

        payload = {
            "domain_data": [{"domain": "example.com", "state": "verified"}],
            "name": "Test Organization",
        }
        organization = self.organizations.create_organization(**payload)

        assert organization.id == "org_01EHT88Z8J8795GZNQ4ZP1J81T"
        assert organization.name == "Foo Corporation"

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
        self, mock_organization_updated, mock_http_client_with_response
    ):
        mock_http_client_with_response(self.http_client, mock_organization_updated, 201)

        updated_organization = self.organizations.update_organization(
            organization_id="org_01EHT88Z8J8795GZNQ4ZP1J81T",
            name="Example Organization",
            domain_data=[{"domain": "example.io", "state": "verified"}],
        )

        assert updated_organization.id == "org_01EHT88Z8J8795GZNQ4ZP1J81T"
        assert updated_organization.name == "Example Organization"
        assert updated_organization.domains == [
            {
                "domain": "example.io",
                "object": "organization_domain",
                "id": "org_domain_01EHT88Z8WZEFWYPM6EC9BX2R8",
            }
        ]

    def test_delete_organization(self, setup, mock_http_client_with_response):
        mock_http_client_with_response(
            self.http_client,
            202,
            headers={"content-type": "text/plain; charset=utf-8"},
        )

        response = self.organizations.delete_organization(
            organization_id="connection_id"
        )

        assert response is None

    def test_list_organizations_auto_pagination_for_single_page(
        self,
        mock_organizations_single_page_response,
        mock_organizations,
        mock_http_client_with_response,
    ):
        mock_http_client_with_response(
            self.http_client, mock_organizations_single_page_response, 200
        )

        all_organizations = []
        organizations = self.organizations.list_organizations()

        for org in organizations.auto_paging_iter():
            all_organizations.append(org)

        assert len(list(all_organizations)) == 10

        organization_data = mock_organizations_single_page_response["data"]
        assert (list_data_to_dicts(all_organizations)) == organization_data

    def test_list_organizations_auto_pagination_for_multiple_pages(
        self,
        mock_organizations_multiple_data_pages,
        test_sync_auto_pagination,
    ):
        test_sync_auto_pagination(
            http_client=self.http_client,
            list_function=self.organizations.list_organizations,
            expected_all_page_data=mock_organizations_multiple_data_pages["data"],
        )
