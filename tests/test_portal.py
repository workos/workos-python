import pytest

from workos.portal import Portal


class TestPortal(object):
    @pytest.fixture(autouse=True)
    def setup(self, sync_http_client_for_test):
        self.http_client = sync_http_client_for_test
        self.portal = Portal(http_client=self.http_client)

    @pytest.fixture
    def mock_portal_link(self):
        return {"link": "https://id.workos.com/portal/launch?secret=secret"}

    def test_generate_link_sso(self, mock_portal_link, mock_http_client_with_response):
        mock_http_client_with_response(self.http_client, mock_portal_link, 201)

        response = self.portal.generate_link(
            intent="sso", organization_id="org_01EHQMYV6MBK39QC5PZXHY59C3"
        )

        assert response.link == "https://id.workos.com/portal/launch?secret=secret"

    def test_generate_link_dsync(
        self, mock_portal_link, mock_http_client_with_response
    ):
        mock_http_client_with_response(self.http_client, mock_portal_link, 201)

        response = self.portal.generate_link(
            intent="dsync", organization_id="org_01EHQMYV6MBK39QC5PZXHY59C3"
        )

        assert response.link == "https://id.workos.com/portal/launch?secret=secret"

    def test_generate_link_audit_logs(
        self, mock_portal_link, mock_http_client_with_response
    ):
        mock_http_client_with_response(self.http_client, mock_portal_link, 201)

        response = self.portal.generate_link(
            intent="audit_logs", organization_id="org_01EHQMYV6MBK39QC5PZXHY59C3"
        )

        assert response.link == "https://id.workos.com/portal/launch?secret=secret"

    def test_generate_link_log_streams(
        self, mock_portal_link, mock_http_client_with_response
    ):
        mock_http_client_with_response(self.http_client, mock_portal_link, 201)

        response = self.portal.generate_link(
            intent="log_streams", organization_id="org_01EHQMYV6MBK39QC5PZXHY59C3"
        )

        assert response.link == "https://id.workos.com/portal/launch?secret=secret"
