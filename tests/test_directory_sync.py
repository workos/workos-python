import json
from requests import Response

import pytest

import workos
from workos.directory_sync import DirectorySync
from workos.utils.request import RESPONSE_TYPE_CODE


class TestSSO(object):
    @pytest.fixture(autouse=True)
    def setup(self, set_api_key):
        self.directory_sync = DirectorySync()

    @pytest.fixture
    def mock_directory_users(self):
        return {
            "listMetadata": {"before": None, "after": None},
            "data": [
                {
                    "username": "yoon@seri.com",
                    "last_name": "Seri",
                    "first_name": "Yoon",
                    "emails": [
                        {"primary": True, "type": "work", "value": "yoon@seri.com"}
                    ],
                    "raw_attributes": {
                        "schemas": ["urn:scim:schemas:core:1.0"],
                        "name": {"familyName": "Seri", "givenName": "Yoon"},
                        "externalId": "external-id",
                        "locale": "en_US",
                        "userName": "yoon@seri.com",
                        "id": "directory_usr_id",
                        "displayName": "Yoon Seri",
                        "active": True,
                        "groups": [],
                        "meta": {
                            "created": "2020-02-21T00:32:14.443Z",
                            "version": "7ff066f75718e21a521c269ae7eafce474ae07c1",
                            "lastModified": "2020-02-21T00:36:44.638Z",
                        },
                        "emails": [
                            {"value": "yoon@seri.com", "type": "work", "primary": True}
                        ],
                    },
                    "id": "directory_usr_id",
                }
            ],
        }

    @pytest.fixture
    def mock_directory_groups(self):
        return {
            "data": [{"name": "Developers", "id": "directory_grp_id"}],
            "listMetadata": {
                "before": "directory_grp_id",
                "after": "directory_grp_id",
            },
        }

    @pytest.fixture
    def mock_directory_user(self):
        return {
            "username": "yoon@seri.com",
            "last_name": "Seri",
            "first_name": "Yoon",
            "emails": [{"primary": True, "type": "work", "value": "yoon@seri.com"}],
            "raw_attributes": {
                "schemas": ["urn:scim:schemas:core:1.0"],
                "name": {"familyName": "Seri", "givenName": "Yoon"},
                "externalId": "external-id",
                "locale": "en_US",
                "userName": "yoon@seri.com",
                "id": "directory_usr_id",
                "displayName": "Yoon Seri",
                "active": True,
                "groups": [],
                "meta": {
                    "created": "2020-02-21T00:32:14.443Z",
                    "version": "7ff066f75718e21a521c269ae7eafce474ae07c1",
                    "lastModified": "2020-02-21T00:36:44.638Z",
                },
                "emails": [{"value": "yoon@seri.com", "type": "work", "primary": True}],
            },
            "id": "directory_usr_id",
        }

    def test_get_directory_users(self, mock_directory_users, mock_request_method):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.response_dict = mock_directory_users
        mock_request_method("get", mock_response, 200)
        response = self.directory_sync.get_directory_users(
            directory_endpoint_id="directory_edp_id"
        )
        assert response.status_code == 200
        assert response.response_dict == mock_directory_users

    def test_get_directory_groups(self, mock_directory_groups, mock_request_method):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.response_dict = mock_directory_groups
        mock_request_method("get", mock_response, 200)
        response = self.directory_sync.get_directory_groups(
            directory_endpoint_id="directory_edp_id"
        )
        assert response.status_code == 200
        assert response.response_dict == mock_directory_groups

    def test_get_directory_user(self, mock_directory_user, mock_request_method):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.response_dict = mock_directory_user
        mock_request_method("get", mock_response, 200)
        response = self.directory_sync.get_directory_user(
            directory_endpoint_id="directory_edp_id",
            directory_user_id="directory_usr_id",
        )
        assert response.status_code == 200
        assert response.response_dict == mock_directory_user

    def test_get_directory_user_groups(
        self, mock_directory_groups, mock_request_method
    ):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.response_dict = mock_directory_groups
        mock_request_method("get", mock_response, 200)
        response = self.directory_sync.get_directory_user_groups(
            directory_endpoint_id="directory_edp_id",
            directory_user_id="directory_usr_id",
        )
        assert response.status_code == 200
        assert response.response_dict == mock_directory_groups
