import pytest
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
            "metadata": {
                "params": {
                    "domains": None,
                    "limit": None,
                    "before": None,
                    "after": None,
                    "order": None,
                    "default_limit": True,
                },
                "method": Organizations.list_organizations,
            },
        }

    @pytest.fixture
    def mock_organizations_v2(self):
        organization_list = [MockOrganization(id=str(i)).to_dict() for i in range(5000)]

        dict_response = {
            "data": organization_list,
            "list_metadata": {"before": None, "after": None},
            "metadata": {
                "params": {
                    "domains": None,
                    "limit": None,
                    "before": None,
                    "after": None,
                    "order": None,
                    "default_limit": True,
                },
                "method": Organizations.list_organizations_v2,
            },
        }
        return dict_response

    @pytest.fixture
    def mock_organizations_with_limit(self):
        organization_list = [MockOrganization(id=str(i)).to_dict() for i in range(4)]

        return {
            "data": organization_list,
            "list_metadata": {"before": None, "after": None},
            "metadata": {
                "params": {
                    "domains": None,
                    "limit": 4,
                    "before": None,
                    "after": None,
                    "order": None,
                },
                "method": Organizations.list_organizations,
            },
        }

    @pytest.fixture
    def mock_organizations_with_limit_v2(self):
        organization_list = [MockOrganization(id=str(i)).to_dict() for i in range(4)]

        dict_response = {
            "data": organization_list,
            "list_metadata": {"before": None, "after": None},
            "metadata": {
                "params": {
                    "domains": None,
                    "limit": 4,
                    "before": None,
                    "after": None,
                    "order": None,
                },
                "method": Organizations.list_organizations_v2,
            },
        }
        return self.organizations.construct_from_response(dict_response)

    @pytest.fixture
    def mock_organizations_with_default_limit(self):
        organization_list = [MockOrganization(id=str(i)).to_dict() for i in range(10)]

        return {
            "data": organization_list,
            "list_metadata": {"before": None, "after": "org_id_xxx"},
            "metadata": {
                "params": {
                    "domains": None,
                    "limit": None,
                    "before": None,
                    "after": None,
                    "order": None,
                    "default_limit": True,
                },
                "method": Organizations.list_organizations,
            },
        }

    @pytest.fixture
    def mock_organizations_with_default_limit_v2(self):
        organization_list = [MockOrganization(id=str(i)).to_dict() for i in range(10)]

        dict_response = {
            "data": organization_list,
            "list_metadata": {"before": None, "after": "org_id_xxx"},
            "metadata": {
                "params": {
                    "domains": None,
                    "limit": None,
                    "before": None,
                    "after": None,
                    "order": None,
                    "default_limit": True,
                },
                "method": Organizations.list_organizations_v2,
            },
        }
        return self.organizations.construct_from_response(dict_response)

    @pytest.fixture
    def mock_organizations_pagination_response(self):
        organization_list = [MockOrganization(id=str(i)).to_dict() for i in range(4990)]

        return {
            "data": organization_list,
            "list_metadata": {"before": None, "after": None},
            "metadata": {
                "params": {
                    "domains": None,
                    "limit": None,
                    "before": None,
                    "after": None,
                    "order": None,
                    "default_limit": True,
                },
                "method": Organizations.list_organizations,
            },
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
        self,
        mock_organizations_with_default_limit,
        mock_organizations_pagination_response,
        mock_organizations,
        mock_request_method,
    ):
        mock_request_method("get", mock_organizations_pagination_response, 200)

        organizations = mock_organizations_with_default_limit

        all_organizations = Organizations.construct_from_response(
            organizations
        ).auto_paging_iter()

        assert len(*list(all_organizations)) == len(mock_organizations["data"])

    def test_list_organizations_auto_pagination_v2(
        self,
        mock_organizations_with_default_limit_v2,
        mock_organizations_pagination_response,
        mock_organizations,
        mock_request_method,
    ):
        mock_request_method("get", mock_organizations_pagination_response, 200)

        organizations = mock_organizations_with_default_limit_v2

        all_organizations = organizations.auto_paging_iter()

        assert len(*list(all_organizations)) == len(mock_organizations["data"])

    def test_list_organizations_honors_limit(
        self,
        mock_organizations_with_limit,
        mock_organizations_pagination_response,
        mock_request_method,
    ):
        mock_request_method("get", mock_organizations_pagination_response, 200)

        organizations = mock_organizations_with_limit

        all_organizations = Organizations.construct_from_response(
            organizations
        ).auto_paging_iter()

        assert len(*list(all_organizations)) == len(
            mock_organizations_with_limit["data"]
        )

    def test_list_organizations_honors_limit_v2(
        self,
        mock_organizations_with_limit_v2,
        mock_organizations_pagination_response,
        mock_request_method,
    ):
        mock_request_method("get", mock_organizations_pagination_response, 200)

        organizations = mock_organizations_with_limit_v2

        all_organizations = organizations.auto_paging_iter()
        dict_response = organizations.to_dict()

        assert len(*list(all_organizations)) == len(dict_response["data"])

    def test_list_organizations_returns_metadata(
        self,
        mock_organizations,
        mock_request_method,
    ):
        mock_request_method("get", mock_organizations, 200)

        organizations = self.organizations.list_organizations(
            domains=["planet-express.com"]
        )

        assert organizations["metadata"]["params"]["domains"] == ["planet-express.com"]

    def test_list_organizations_returns_metadata_v2(
        self,
        mock_organizations_v2,
        mock_request_method,
    ):
        mock_request_method("get", mock_organizations_v2, 200)

        organizations = self.organizations.list_organizations_v2(
            domains=["planet-express.com"]
        )

        dict_organizations = organizations.to_dict()

        assert dict_organizations["metadata"]["params"]["domains"] == [
            "planet-express.com"
        ]
