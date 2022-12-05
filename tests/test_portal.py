import json
from requests import Response

import pytest

import workos
from workos.portal import Portal


class TestPortal(object):
    @pytest.fixture(autouse=True)
    def setup(self, set_api_key):
        self.portal = Portal()

    @pytest.fixture
    def mock_portal_link(self):
        return {"link": "https://id.workos.com/portal/launch?secret=secret"}

    def test_generate_link_sso(self, mock_portal_link, mock_request_method):
        mock_request_method("post", mock_portal_link, 201)

        response = self.portal.generate_link("sso", "org_01EHQMYV6MBK39QC5PZXHY59C3")

        assert response["link"] == "https://id.workos.com/portal/launch?secret=secret"

    def test_generate_link_dsync(self, mock_portal_link, mock_request_method):
        mock_request_method("post", mock_portal_link, 201)

        response = self.portal.generate_link("dsync", "org_01EHQMYV6MBK39QC5PZXHY59C3")

        assert response["link"] == "https://id.workos.com/portal/launch?secret=secret"

    def test_generate_link_audit_logs(self, mock_portal_link, mock_request_method):
        mock_request_method("post", mock_portal_link, 201)

        response = self.portal.generate_link(
            "audit_logs", "org_01EHQMYV6MBK39QC5PZXHY59C3"
        )

        assert response["link"] == "https://id.workos.com/portal/launch?secret=secret"

    def test_generate_link_log_streams(self, mock_portal_link, mock_request_method):
        mock_request_method("post", mock_portal_link, 201)

        response = self.portal.generate_link(
            "log_streams", "org_01EHQMYV6MBK39QC5PZXHY59C3"
        )

        assert response["link"] == "https://id.workos.com/portal/launch?secret=secret"
