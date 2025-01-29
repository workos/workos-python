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

    def test_generate_link_sso(
        self, mock_portal_link, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_portal_link, 201
        )

        response = self.portal.generate_link(
            intent="sso",
            organization_id="org_01EHQMYV6MBK39QC5PZXHY59C3",
            intent_options={"sso": {"bookmark_slug": "my_app"}},
        )

        assert request_kwargs["url"].endswith("/portal/generate_link")
        assert request_kwargs["method"] == "post"
        assert request_kwargs["json"] == {
            "intent": "sso",
            "organization": "org_01EHQMYV6MBK39QC5PZXHY59C3",
            "intent_options": {"sso": {"bookmark_slug": "my_app"}},
        }
        assert response.link == "https://id.workos.com/portal/launch?secret=secret"

    def test_generate_link_domain_verification(
        self, mock_portal_link, mock_http_client_with_response
    ):
        mock_http_client_with_response(self.http_client, mock_portal_link, 201)

        response = self.portal.generate_link(
            intent="domain_verification",
            organization_id="org_01EHQMYV6MBK39QC5PZXHY59C3",
        )

        assert response.link == "https://id.workos.com/portal/launch?secret=secret"

    def test_generate_link_dsync(
        self, mock_portal_link, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_portal_link, 201
        )

        response = self.portal.generate_link(
            intent="dsync", organization_id="org_01EHQMYV6MBK39QC5PZXHY59C3"
        )

        assert request_kwargs["url"].endswith("/portal/generate_link")
        assert request_kwargs["method"] == "post"
        assert request_kwargs["json"] == {
            "intent": "dsync",
            "organization": "org_01EHQMYV6MBK39QC5PZXHY59C3",
        }
        assert response.link == "https://id.workos.com/portal/launch?secret=secret"

    def test_generate_link_audit_logs(
        self, mock_portal_link, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_portal_link, 201
        )

        response = self.portal.generate_link(
            intent="audit_logs", organization_id="org_01EHQMYV6MBK39QC5PZXHY59C3"
        )

        assert request_kwargs["url"].endswith("/portal/generate_link")
        assert request_kwargs["method"] == "post"
        assert request_kwargs["json"] == {
            "intent": "audit_logs",
            "organization": "org_01EHQMYV6MBK39QC5PZXHY59C3",
        }
        assert response.link == "https://id.workos.com/portal/launch?secret=secret"

    def test_generate_link_log_streams(
        self, mock_portal_link, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_portal_link, 201
        )

        response = self.portal.generate_link(
            intent="log_streams", organization_id="org_01EHQMYV6MBK39QC5PZXHY59C3"
        )

        assert request_kwargs["url"].endswith("/portal/generate_link")
        assert request_kwargs["method"] == "post"
        assert request_kwargs["json"] == {
            "intent": "log_streams",
            "organization": "org_01EHQMYV6MBK39QC5PZXHY59C3",
        }
        assert response.link == "https://id.workos.com/portal/launch?secret=secret"

    def test_generate_link_certificate_renewal(
        self, mock_portal_link, mock_http_client_with_response
    ):
        mock_http_client_with_response(self.http_client, mock_portal_link, 201)

        response = self.portal.generate_link(
            intent="certificate_renewal",
            organization_id="org_01EHQMYV6MBK39QC5PZXHY59C3",
        )

        assert response.link == "https://id.workos.com/portal/launch?secret=secret"
