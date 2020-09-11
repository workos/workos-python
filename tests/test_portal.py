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
        response = self.portal.list_organizations()
        assert response.status_code == 200
        assert len(response.response_dict["data"]) == 2
