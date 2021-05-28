import json
from requests import Response

import pytest

import workos
from workos.organizations import Organizations


class TestOrganizations(object):
    @pytest.fixture(autouse=True)
    def setup(self, set_api_key):
        self.organizations = Organizations()

    @pytest.fixture
    def mock_organization(self):
        return {
            "name": "Test Organization",
            "object": "organization",
            "id": "org_01EHT88Z8J8795GZNQ4ZP1J81T",
            "domains": [
                {
                    "domain": "example.com",
                    "object": "organization_domain",
                    "id": "org_domain_01EHT88Z8WZEFWYPM6EC9BX2R8",
                }
            ],
        }

    @pytest.fixture
    def mock_organization_updated(self):
        return {
            "name": "Example Organization",
            "object": "organization",
            "id": "org_01EHT88Z8J8795GZNQ4ZP1J81T",
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
        return {
            "object": "list",
            "data": [
                {
                    "object": "organization",
                    "id": "org_01EHQMYV6MBK39QC5PZXHY59C3",
                    "name": "example.com",
                    "domains": [
                        {
                            "object": "organization_domain",
                            "id": "org_domain_01EHQMYV71XT8H31WE5HF8YK4A",
                            "domain": "example.com",
                        }
                    ],
                },
                {
                    "object": "organization",
                    "id": "org_01EHQMVDTC2GRAHFCCRNTSKH46",
                    "name": "example2.com",
                    "domains": [
                        {
                            "object": "organization_domain",
                            "id": "org_domain_01EHQMVDTZVA27PK614ME4YK7V",
                            "domain": "example2.com",
                        }
                    ],
                },
            ],
            "listMetadata": {"before": "before-id", "after": None},
        }

    def test_list_organizations(self, mock_organizations, mock_request_method):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.response_dict = mock_organizations
        mock_request_method("get", mock_response, 200)
        response = self.organizations.list_organizations()
        assert response.status_code == 200
        assert len(response.response_dict["data"]) == 2

    def test_get_organization(self, mock_organization, mock_request_method):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.response_dict = mock_organization
        mock_request_method("get", mock_response, 200)
        response = self.organizations.get_organization(organization="organization_id")
        assert response.status_code == 200
        assert response.response_dict == mock_organization

    def test_create_organization(self, mock_organization, mock_request_method):
        organization = {"domains": ["example.com"], "name": "Test Organization"}
        mock_response = Response()
        mock_response.status_code = 201
        mock_response.response_dict = mock_organization
        mock_request_method("post", mock_response, 201)

        result = self.organizations.create_organization(organization)
        subject = result.response_dict

        assert subject["id"] == "org_01EHT88Z8J8795GZNQ4ZP1J81T"
        assert subject["name"] == "Test Organization"

    def test_update_organization(self, mock_organization_updated, mock_request_method):
        mock_response = Response()
        mock_response.status_code = 201
        mock_response.response_dict = mock_organization_updated
        mock_request_method("put", mock_response, 201)

        result = self.organizations.update_organization(
            organization="org_01EHT88Z8J8795GZNQ4ZP1J81T",
            name="Example Organization",
            domains=["example.io"],
        )
        subject = result.response_dict

        assert subject["id"] == "org_01EHT88Z8J8795GZNQ4ZP1J81T"
        assert subject["name"] == "Example Organization"
        assert subject["domains"] == [
            {
                "domain": "example.io",
                "object": "organization_domain",
                "id": "org_domain_01EHT88Z8WZEFWYPM6EC9BX2R8",
            }
        ]

    def test_delete_organization(self, setup, mock_request_method):
        mock_response = Response()
        mock_response.status_code = 204
        mock_request_method("delete", mock_response, 204)
        response = self.organizations.delete_organization(organization="connection_id")
        assert response.status_code == 204
