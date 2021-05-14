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
        mock_response = Response()
        mock_response.status_code = 201
        mock_response.response_dict = mock_portal_link
        mock_request_method("post", mock_response, 201)

        result = self.portal.generate_link("sso", "org_01EHQMYV6MBK39QC5PZXHY59C3")
        subject = result.response_dict

        assert subject["link"] == "https://id.workos.com/portal/launch?secret=secret"

    def test_generate_link_dsync(self, mock_portal_link, mock_request_method):
        mock_response = Response()
        mock_response.status_code = 201
        mock_response.response_dict = mock_portal_link
        mock_request_method("post", mock_response, 201)

        result = self.portal.generate_link("dsync", "org_01EHQMYV6MBK39QC5PZXHY59C3")
        subject = result.response_dict

        assert subject["link"] == "https://id.workos.com/portal/launch?secret=secret"

    def test_get_connection(self, mock_organization, mock_request_method):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.response_dict = mock_organization
        mock_request_method("get", mock_response, 200)
        response = self.portal.get_organization(organization="organization_id")
        assert response.status_code == 200
        assert response.response_dict == mock_organization
