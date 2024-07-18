import datetime

import pytest
import requests

from tests.conftest import MockResponse
from workos.organizations import Organizations
from tests.utils.fixtures.mock_organization import MockOrganization


class TestOrganizations(object):
    @pytest.fixture(autouse=True)
    def setup(self, set_api_key):
        self.organizations = Organizations()

    @pytest.fixture
    def mock_organization(self):
        return MockOrganization("org_01EHT88Z8J8795GZNQ4ZP1J81T").to_dict()

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
        organization_list = [MockOrganization(id=str(i)).to_dict() for i in range(10)]

        return {
            "data": organization_list,
            "list_metadata": {"before": None, "after": None},
            "object": "list",
        }

    @pytest.fixture
    def mock_organizations_pagination_response(self):
        organization_list = [MockOrganization(id=str(i)).to_dict() for i in range(10)]

        return {
            "data": organization_list,
            "list_metadata": {"before": None, "after": None},
            "object": "list",
        }

    @pytest.fixture
    def mock_pagination_request(self, monkeypatch):
        def inner(method, response_dict, status_code, headers=None):
            def mock(*args, **kwargs):
                params = kwargs.get("params") or {}
                if params.get("after") is None:
                    response_dict["list_metadata"]["after"] = "after"

                if params.get("after") == "after":
                    response_dict["list_metadata"]["after"] = None

                    for item in response_dict["data"]:
                        item["id"] = str(int(item["id"]) + 10)

                return MockResponse(response_dict, status_code, headers=headers)

            monkeypatch.setattr(requests, method, mock)

        return inner

    def test_list_organizations(self, mock_organizations, mock_request_method):
        mock_request_method("get", mock_organizations, 200)

        organizations_response = self.organizations.list_organizations()

        def to_dict(x):
            return x.dict()

        assert (
            list(map(to_dict, organizations_response.data))
            == mock_organizations["data"]
        )

    def test_get_organization(self, mock_organization, mock_request_method):
        mock_request_method("get", mock_organization, 200)

        organization = self.organizations.get_organization(
            organization="organization_id"
        )

        assert organization.dict() == mock_organization

    def test_get_organization_by_lookup_key(
        self, mock_organization, mock_request_method
    ):
        mock_request_method("get", mock_organization, 200)

        organization = self.organizations.get_organization_by_lookup_key(
            lookup_key="test"
        )

        assert organization.dict() == mock_organization

    def test_create_organization_with_domain_data(
        self, mock_organization, mock_request_method
    ):
        mock_request_method("post", mock_organization, 201)

        payload = {
            "domain_data": [{"domain": "example.com", "state": "verified"}],
            "name": "Test Organization",
        }
        organization = self.organizations.create_organization(**payload)

        assert organization.id == "org_01EHT88Z8J8795GZNQ4ZP1J81T"
        assert organization.name == "Foo Corporation"

    def test_sends_idempotency_key(self, mock_organization, capture_and_mock_request):
        idempotency_key = "test_123456789"

        payload = {
            "domain_data": [{"domain": "example.com", "state": "verified"}],
            "name": "Foo Corporation",
        }

        _, request_kwargs = capture_and_mock_request("post", mock_organization, 200)

        response = self.organizations.create_organization(
            **payload, idempotency_key=idempotency_key
        )

        assert request_kwargs["headers"]["idempotency-key"] == idempotency_key
        assert response.name == "Foo Corporation"

    def test_update_organization_with_domain_data(
        self, mock_organization_updated, mock_request_method
    ):
        mock_request_method("put", mock_organization_updated, 201)

        updated_organization = self.organizations.update_organization(
            organization="org_01EHT88Z8J8795GZNQ4ZP1J81T",
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

    def test_delete_organization(self, setup, mock_raw_request_method):
        mock_raw_request_method(
            "delete",
            "Accepted",
            202,
            headers={"content-type": "text/plain; charset=utf-8"},
        )

        response = self.organizations.delete_organization(organization="connection_id")

        assert response is None

    def test_list_organizations_auto_pagination(
        self,
        mock_organizations_pagination_response,
        mock_organizations,
        mock_pagination_request,
    ):
        mock_pagination_request("get", mock_organizations_pagination_response, 200)

        all_organizations = []

        organizations = self.organizations.list_organizations()

        for org in organizations.auto_paging_iter():
            all_organizations.append(org)

        assert len(list(all_organizations)) == 20

        for i, org in enumerate(all_organizations):
            assert org.id == str(i)
