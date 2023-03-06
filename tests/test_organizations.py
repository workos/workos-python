import pytest
from workos.organizations import Organizations
from workos.resources.list import WorkOSListResource
from tests.utils.fixtures.mock_organization import MockOrganization
from workos.utils.list_types import Type


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

        organization_list = [MockOrganization(id=str(i)).to_dict() for i in range(5000)]

        return {
            "data": organization_list,
            "list_metadata": {"before": None, "after": None},
        }

    def test_list_organizations(self, mock_organizations, mock_request_method):
        mock_request_method("get", {"data": mock_organizations}, 200)

        organizations_response = self.organizations.list_organizations()

        assert organizations_response["data"] == mock_organizations

    def test_get_organization(self, mock_organization, mock_request_method):
        mock_request_method("get", mock_organization, 200)

        organization = self.organizations.get_organization(
            organization="organization_id"
        )

        assert organization == mock_organization

    def test_create_organization(self, mock_organization, mock_request_method):
        mock_request_method("post", mock_organization, 201)

        payload = {"domains": ["example.com"], "name": "Test Organization"}
        organization = self.organizations.create_organization(payload)

        assert organization["id"] == "org_01EHT88Z8J8795GZNQ4ZP1J81T"
        assert organization["name"] == "Foo Corporation"

    def test_sends_idempotency_key(self, capture_and_mock_request):
        idempotency_key = "test_123456789"
        payload = {"domains": ["example.com"], "name": "Foo Corporation"}

        _, request_kwargs = capture_and_mock_request("post", payload, 200)

        response = self.organizations.create_organization(
            payload, idempotency_key=idempotency_key
        )

        assert request_kwargs["headers"]["idempotency-key"] == idempotency_key
        assert response["name"] == "Foo Corporation"

    def test_update_organization(self, mock_organization_updated, mock_request_method):
        mock_request_method("put", mock_organization_updated, 201)

        updated_organization = self.organizations.update_organization(
            organization="org_01EHT88Z8J8795GZNQ4ZP1J81T",
            name="Example Organization",
            domains=["example.io"],
            allow_profiles_outside_organization=True,
        )

        assert updated_organization["id"] == "org_01EHT88Z8J8795GZNQ4ZP1J81T"
        assert updated_organization["name"] == "Example Organization"
        assert updated_organization["domains"] == [
            {
                "domain": "example.io",
                "object": "organization_domain",
                "id": "org_domain_01EHT88Z8WZEFWYPM6EC9BX2R8",
            }
        ]
        assert updated_organization["allow_profiles_outside_organization"]

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
        self, mock_organizations, mock_request_method
    ):
        mock_request_method("get", mock_organizations, 200)
        organizations = self.organizations.list_organizations()

        all_organizations = WorkOSListResource.construct_from_response(
            organizations
        ).auto_paginate(Type.Organizations)

        assert len(all_organizations) == len(mock_organizations["data"])
