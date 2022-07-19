import json
from requests import Response

import pytest

import workos
from workos.directory_sync import DirectorySync
from workos.utils.request import RESPONSE_TYPE_CODE


class TestDirectorySync(object):
    @pytest.fixture(autouse=True)
    def setup(self, set_api_key):
        self.directory_sync = DirectorySync()

    @pytest.fixture
    def mock_users(self):
        return {
            "list_metadata": {"before": None, "after": None},
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
            "list_metadata": {
                "before": "directory_grp_id",
                "after": "directory_grp_id",
            },
        }

    @pytest.fixture
    def mock_user(self):
        return {
            "id": "directory_user_01E1JG7J09H96KYP8HM9B0G5SJ",
            "idp_id": "2836",
            "directory_id": "directory_01ECAZ4NV9QMV47GW873HDCX74",
            "organization_id": "org_01EZTR6WYX1A0DSE2CYMGXQ24Y",
            "first_name": "Marcelina",
            "last_name": "Davis",
            "emails": [
                {"primary": "true", "type": "work", "value": "marcelina@foo-corp.com"}
            ],
            "username": "marcelina@foo-corp.com",
            "groups": [
                {
                    "id": "directory_group_01E64QTDNS0EGJ0FMCVY9BWGZT",
                    "name": "Engineering",
                    "created_at": "2021-06-25T19:07:33.155Z",
                    "updated_at": "2021-06-25T19:07:33.155Z",
                    "raw_attributes": {...},
                }
            ],
            "state": "active",
            "created_at": "2021-06-25T19:07:33.155Z",
            "updated_at": "2021-06-25T19:07:33.155Z",
            "custom_attributes": {"department": "Engineering"},
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
        }

    @pytest.fixture
    def mock_group(self):
        return {
            "id": "directory_group_01FHGRYAQ6ERZXXXXXX1E01QFE",
            "idp_id": "Sales",
            "directory_id": "directory_01FHGRXQEXDXXXXXXXCM2290ZR",
            "name": "Sales",
            "created_at": "2021-10-08T20:19:13.381Z",
            "updated_at": "2021-10-15T07:49:43.448Z",
            "raw_attributes": {},
        }

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
                    "organization_id": "organization_id",
                    "domain": "crashlandingonyou.com",
                }
            ],
            "list_metadata": {"before": None, "after": None},
        }

    @pytest.fixture
    def mock_directory(self):
        return {
            "object": "directory",
            "id": "directory_01ECAZ4NV9QMV47GW873HDCX74",
            "domain": "foo-corp.com",
            "name": "Foo Corp",
            "organization_id": "org_01EHZNVPK3SFK441A1RGBFSHRT",
            "state": "unlinked",
            "type": "gsuite directory",
            "created_at": "2021-06-25T19:07:33.155Z",
            "updated_at": "2021-06-25T19:07:33.155Z",
        }

    def test_list_users_with_directory(self, mock_users, mock_request_method):
        mock_request_method("get", mock_users, 200)

        users = self.directory_sync.list_users(directory="directory_id")

        assert users == mock_users

    def test_list_users_with_group(self, mock_users, mock_request_method):
        mock_request_method("get", mock_users, 200)

        users = self.directory_sync.list_users(group="directory_grp_id")

        assert users == mock_users

    def test_list_groups_with_directory(self, mock_groups, mock_request_method):
        mock_request_method("get", mock_groups, 200)

        groups = self.directory_sync.list_groups(directory="directory_id")

        assert groups == mock_groups

    def test_list_groups_with_user(self, mock_groups, mock_request_method):
        mock_request_method("get", mock_groups, 200)

        groups = self.directory_sync.list_groups(user="directory_usr_id")

        assert groups == mock_groups

    def test_get_user(self, mock_user, mock_request_method):
        mock_request_method("get", mock_user, 200)

        user = self.directory_sync.get_user(user="directory_usr_id")

        assert user == mock_user

    def test_get_group(self, mock_group, mock_request_method):
        mock_request_method("get", mock_group, 200)

        group = self.directory_sync.get_group(group="directory_grp_id")

        assert group == mock_group

    def test_list_directories(self, mock_directories, mock_request_method):
        mock_request_method("get", mock_directories, 200)

        directories = self.directory_sync.list_directories()

        assert directories == mock_directories

    def test_get_directory(self, mock_directory, mock_request_method):
        mock_request_method("get", mock_directory, 200)

        directory = self.directory_sync.get_directory(directory="directory_id")

        assert directory == mock_directory

    def test_delete_directory(self, mock_directories, mock_raw_request_method):
        mock_raw_request_method(
            "delete",
            "Accepted",
            202,
            headers={"content-type": "text/plain; charset=utf-8"},
        )

        response = self.directory_sync.delete_directory(directory="directory_id")

        assert response is None
