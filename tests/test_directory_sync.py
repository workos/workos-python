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
    def mock_users(self):
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
    def mock_groups(self):
        return {
            "data": [{"name": "Developers", "id": "directory_grp_id"}],
            "listMetadata": {
                "before": "directory_grp_id",
                "after": "directory_grp_id",
            },
        }

    @pytest.fixture
    def mock_user(self):
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

    @pytest.fixture
    def mock_group(self):
        return {"name": "Developers", "id": "directory_grp_id"}

    @pytest.fixture
    def mock_user_groups(self):
        return [{"name": "Developers", "id": "directory_grp_id"}]

    @pytest.fixture
    def mock_directories(self):
        return {
            "data": [
                {
                    "id": "directory_id",
                    "external_key": "fried-chicken",
                    "state": "linked",
                    "type": "gsuite directory",
                    "name": "Ri Jeong Hyeok",
                    "bearer_token": None,
                    "project_id": "project_id",
                    "domain": "crashlandingonyou.com",
                }
            ],
            "listMetadata": {"before": None, "after": None},
        }

    def test_list_users_with_directory(self, mock_users, mock_request_method):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.response_dict = mock_users
        mock_request_method("get", mock_response, 200)
        response = self.directory_sync.list_users(directory="directory_id")
        assert response.status_code == 200
        assert response.response_dict == mock_users

    def test_list_users_with_group(self, mock_users, mock_request_method):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.response_dict = mock_users
        mock_request_method("get", mock_response, 200)
        response = self.directory_sync.list_users(group="directory_grp_id")
        assert response.status_code == 200
        assert response.response_dict == mock_users

    def test_list_groups_with_directory(self, mock_groups, mock_request_method):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.response_dict = mock_groups
        mock_request_method("get", mock_response, 200)
        response = self.directory_sync.list_groups(directory="directory_id")
        assert response.status_code == 200
        assert response.response_dict == mock_groups

    def test_list_groups_with_user(self, mock_groups, mock_request_method):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.response_dict = mock_groups
        mock_request_method("get", mock_response, 200)
        response = self.directory_sync.list_groups(user="directory_usr_id")
        assert response.status_code == 200
        assert response.response_dict == mock_groups

    def test_get_user(self, mock_user, mock_request_method):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.response_dict = mock_user
        mock_request_method("get", mock_response, 200)
        response = self.directory_sync.get_user(user="directory_usr_id")
        assert response.status_code == 200
        assert response.response_dict == mock_user

    def test_get_group(self, mock_group, mock_request_method):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.response_dict = mock_group
        mock_request_method("get", mock_response, 200)
        response = self.directory_sync.get_group(group="directory_grp_id")
        assert response.status_code == 200
        assert response.response_dict == mock_group

    def test_list_directories(self, mock_directories, mock_request_method):
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.response_dict = mock_directories
        mock_request_method("get", mock_response, 200)
        response = self.directory_sync.list_directories()
        assert response.status_code == 200
        assert response.response_dict == mock_directories
