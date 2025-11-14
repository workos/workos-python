from typing import Union
import pytest
from tests.utils.syncify import syncify
from workos.organization_domains import AsyncOrganizationDomains, OrganizationDomains


@pytest.mark.sync_and_async(OrganizationDomains, AsyncOrganizationDomains)
class TestOrganizationDomains:
    @pytest.fixture(autouse=True)
    def setup(
        self, module_instance: Union[OrganizationDomains, AsyncOrganizationDomains]
    ):
        self.http_client = module_instance._http_client
        self.organization_domains = module_instance

    @pytest.fixture
    def mock_organization_domain(self):
        return {
            "object": "organization_domain",
            "id": "org_domain_01EHT88Z8WZEFWYPM6EC9BX2R8",
            "organization_id": "org_01EHT88Z8J8795GZNQ4ZP1J81T",
            "domain": "example.com",
            "state": "pending",
            "verification_strategy": "dns",
            "verification_token": "workos_example_verification_token_12345",
            "verification_prefix": "_workos-challenge",
            "created_at": "2023-01-01T12:00:00.000Z",
            "updated_at": "2023-01-01T12:00:00.000Z",
        }

    @pytest.fixture
    def mock_organization_domain_verified(self):
        return {
            "object": "organization_domain",
            "id": "org_domain_01EHT88Z8WZEFWYPM6EC9BX2R8",
            "organization_id": "org_01EHT88Z8J8795GZNQ4ZP1J81T",
            "domain": "example.com",
            "state": "verified",
            "verification_strategy": "dns",
            "verification_token": "workos_example_verification_token_12345",
            "verification_prefix": "_workos-challenge",
            "created_at": "2023-01-01T12:00:00.000Z",
            "updated_at": "2023-01-01T12:00:00.000Z",
        }

    def test_get_organization_domain(
        self, capture_and_mock_http_client_request, mock_organization_domain
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client,
            mock_organization_domain,
            200,
        )

        organization_domain = syncify(
            self.organization_domains.get_organization_domain(
                organization_domain_id="org_domain_01EHT88Z8WZEFWYPM6EC9BX2R8"
            )
        )

        assert request_kwargs["url"].endswith(
            "/organization_domains/org_domain_01EHT88Z8WZEFWYPM6EC9BX2R8"
        )
        assert request_kwargs["method"] == "get"
        assert organization_domain.id == "org_domain_01EHT88Z8WZEFWYPM6EC9BX2R8"
        assert organization_domain.domain == "example.com"
        assert organization_domain.state == "pending"
        assert organization_domain.verification_strategy == "dns"

    def test_create_organization_domain(
        self, capture_and_mock_http_client_request, mock_organization_domain
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client,
            mock_organization_domain,
            201,
        )

        organization_domain = syncify(
            self.organization_domains.create_organization_domain(
                organization_id="org_01EHT88Z8J8795GZNQ4ZP1J81T",
                domain="example.com",
            )
        )

        assert request_kwargs["url"].endswith("/organization_domains")
        assert request_kwargs["method"] == "post"
        assert request_kwargs["json"] == {
            "organization_id": "org_01EHT88Z8J8795GZNQ4ZP1J81T",
            "domain": "example.com",
        }
        assert organization_domain.id == "org_domain_01EHT88Z8WZEFWYPM6EC9BX2R8"
        assert organization_domain.domain == "example.com"
        assert organization_domain.organization_id == "org_01EHT88Z8J8795GZNQ4ZP1J81T"

    def test_verify_organization_domain(
        self, capture_and_mock_http_client_request, mock_organization_domain_verified
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client,
            mock_organization_domain_verified,
            200,
        )

        organization_domain = syncify(
            self.organization_domains.verify_organization_domain(
                organization_domain_id="org_domain_01EHT88Z8WZEFWYPM6EC9BX2R8"
            )
        )

        assert request_kwargs["url"].endswith(
            "/organization_domains/org_domain_01EHT88Z8WZEFWYPM6EC9BX2R8/verify"
        )
        assert request_kwargs["method"] == "post"
        assert organization_domain.id == "org_domain_01EHT88Z8WZEFWYPM6EC9BX2R8"
        assert organization_domain.state == "verified"

    def test_delete_organization_domain(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client,
            None,
            204,
            headers={"content-type": "text/plain; charset=utf-8"},
        )

        response = syncify(
            self.organization_domains.delete_organization_domain(
                organization_domain_id="org_domain_01EHT88Z8WZEFWYPM6EC9BX2R8"
            )
        )

        assert request_kwargs["url"].endswith(
            "/organization_domains/org_domain_01EHT88Z8WZEFWYPM6EC9BX2R8"
        )
        assert request_kwargs["method"] == "delete"
        assert response is None
