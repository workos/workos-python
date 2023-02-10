import pytest
from workos.organizations import Organizations
from workos.resources.organizations import WorkOSOrganizationList


class TestOrganizations(object):
    @pytest.fixture(autouse=True)
    def setup(self, set_api_key):
        self.organizations = Organizations()

    @pytest.fixture
    def mock_organization(self):
        return {
            "id": "org_01EHT88Z8J8795GZNQ4ZP1J81T",
            "object": "organization",
            "name": "Foo Corporation",
            "allow_profiles_outside_organization": "false",
            "created_at": "2021-06-25T19:07:33.155Z",
            "updated_at": "2021-06-25T19:07:33.155Z",
            "domains": [
                {
                    "domain": "foo-corp.com",
                    "id": "org_domain_01EHZNVPK2QXHMVWCEDQEKY69A",
                    "object": "organization_domain",
                },
                {
                    "domain": "another-foo-corp-domain.com",
                    "id": "org_domain_01EHZNS0H9W90A90FV79GAB6AB",
                    "object": "organization_domain",
                },
            ],
        }

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
        return {
            "object": "list",
            "data": [
                {
                    "object": "organization",
                    "id": "org_01EHQMYV6MBK39QC5PZXHY59C3",
                    "name": "example.com",
                    "created_at": "2021-06-25T19:07:33.155Z",
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
                    "created_at": "2021-05-25T19:07:33.155Z",
                    "domains": [
                        {
                            "object": "organization_domain",
                            "id": "org_domain_01EHQMVDTZVA27PK614ME4YK7V",
                            "domain": "example2.com",
                        }
                    ],
                },
                {
                    "object": "organization",
                    "id": "org_01EHQMVDTC2GRAHFCCRNTSKH36",
                    "name": "example2.com",
                    "created_at": "2021-04-25T19:07:33.155Z",
                    "domains": [
                        {
                            "object": "organization_domain",
                            "id": "org_domain_01EHQMVDTZVA27PK614ME4YK7V",
                            "domain": "example2.com",
                        }
                    ],
                },
                {
                    "object": "organization",
                    "id": "org_01EHQMVDTC2GRAHFC6RNTSKH46",
                    "name": "example2.com",
                    "created_at": "2021-03-25T19:07:33.155Z",
                    "domains": [
                        {
                            "object": "organization_domain",
                            "id": "org_domain_01EHQMVDTZVA27PK614ME4YK7V",
                            "domain": "example2.com",
                        }
                    ],
                },
            ],
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
        organizations = self.organizations.list_organizations(limit=2)

        all_organizations = WorkOSOrganizationList.construct_from_response(
            organizations
        ).auto_paging_iter()

        assert len(all_organizations) == len(mock_organizations["data"])
