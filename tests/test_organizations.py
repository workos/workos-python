import datetime
from typing import Union
import pytest
from tests.types.test_auto_pagination_function import TestAutoPaginationFunction
from tests.utils.fixtures.mock_feature_flag import MockFeatureFlag
from tests.utils.fixtures.mock_organization import MockOrganization
from tests.utils.fixtures.mock_role import MockRole
from tests.utils.list_resource import list_response_of
from tests.utils.syncify import syncify
from workos.organizations import AsyncOrganizations, Organizations


@pytest.mark.sync_and_async(Organizations, AsyncOrganizations)
class TestOrganizations:
    @pytest.fixture(autouse=True)
    def setup(self, module_instance: Union[Organizations, AsyncOrganizations]):
        self.http_client = module_instance._http_client
        self.organizations = module_instance

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
                    "created_at": datetime.datetime.now().isoformat(),
                    "updated_at": datetime.datetime.now().isoformat(),
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
            MockOrganization(id=str(f"org_{i + 1}")).dict() for i in range(40)
        ]
        return list_response_of(data=organizations_list)

    @pytest.fixture
    def mock_organization_roles(self):
        return {
            "data": [MockRole(id=str(i)).dict() for i in range(10)],
            "object": "list",
        }

    @pytest.fixture
    def mock_feature_flags(self):
        return {
            "data": [MockFeatureFlag(id=f"flag_{str(i)}").dict() for i in range(2)],
            "object": "list",
            "list_metadata": {"before": None, "after": None},
        }

    def test_list_organizations(
        self, mock_organizations, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_organizations, 200
        )

        organizations_response = syncify(self.organizations.list_organizations())

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

        organization = syncify(
            self.organizations.get_organization(organization_id="organization_id")
        )

        assert organization.dict() == mock_organization
        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith("/organizations/organization_id")

    def test_get_organization_by_external_id(
        self, mock_organization, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_organization, 200
        )

        organization = syncify(
            self.organizations.get_organization_by_external_id(external_id="test")
        )

        assert organization.dict() == mock_organization
        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith("/organizations/external_id/test")

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
        organization = syncify(self.organizations.create_organization(**payload))

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

        response = syncify(
            self.organizations.create_organization(
                **payload, idempotency_key=idempotency_key
            )
        )

        assert request_kwargs["headers"]["idempotency-key"] == idempotency_key
        assert response.name == "Foo Corporation"

    def test_update_organization_with_domain_data(
        self, mock_organization_updated, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_organization_updated, 201
        )

        updated_organization = syncify(
            self.organizations.update_organization(
                organization_id="org_01EHT88Z8J8795GZNQ4ZP1J81T",
                domain_data=[{"domain": "example.io", "state": "verified"}],
            )
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
        domain = updated_organization.domains[0]
        assert domain.domain == "example.io"
        assert domain.object == "organization_domain"
        assert domain.id == "org_domain_01EHT88Z8WZEFWYPM6EC9BX2R8"
        assert domain.state == "verified"
        assert domain.organization_id == "org_01EHT88Z8J8795GZNQ4ZP1J81T"
        assert domain.verification_strategy == "dns"
        assert domain.verification_token == "token"
        assert domain.verification_prefix is None
        assert isinstance(domain.created_at, str)
        assert isinstance(domain.updated_at, str)

    def test_delete_organization(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client,
            202,
            headers={"content-type": "text/plain; charset=utf-8"},
        )

        response = syncify(
            self.organizations.delete_organization(organization_id="organization_id")
        )

        assert request_kwargs["url"].endswith("/organizations/organization_id")
        assert request_kwargs["method"] == "delete"
        assert response is None

    def test_list_organizations_auto_pagination_for_single_page(
        self,
        mock_organizations_single_page_response,
        test_auto_pagination: TestAutoPaginationFunction,
    ):
        test_auto_pagination(
            http_client=self.http_client,
            list_function=self.organizations.list_organizations,
            expected_all_page_data=mock_organizations_single_page_response["data"],
        )

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

    def test_list_organization_roles(
        self, mock_organization_roles, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_organization_roles, 200
        )

        organization_roles_response = syncify(
            self.organizations.list_organization_roles(
                organization_id="org_01EHT88Z8J8795GZNQ4ZP1J81T"
            )
        )

        def to_dict(x):
            return x.dict()

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith(
            "/organizations/org_01EHT88Z8J8795GZNQ4ZP1J81T/roles"
        )
        assert (
            list(map(to_dict, organization_roles_response.data))
            == mock_organization_roles["data"]
        )

    def test_list_feature_flags(
        self, mock_feature_flags, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_feature_flags, 200
        )

        feature_flags_response = syncify(
            self.organizations.list_feature_flags(
                organization_id="org_01EHT88Z8J8795GZNQ4ZP1J81T"
            )
        )

        def to_dict(x):
            return x.dict()

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith(
            "/organizations/org_01EHT88Z8J8795GZNQ4ZP1J81T/feature-flags"
        )
        assert (
            list(map(to_dict, feature_flags_response.data))
            == mock_feature_flags["data"]
        )
