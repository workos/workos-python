import pytest
from workos.directory_sync import DirectorySync
from workos.utils.request import RESPONSE_TYPE_CODE
from workos.resources.directory_sync import WorkOSDirectoryUser
from workos.resources.list import WorkOSListResource
from tests.utils.fixtures.mock_directory import MockDirectory
from tests.utils.fixtures.mock_directory_user import MockDirectoryUser
from tests.utils.fixtures.mock_directory_group import MockDirectoryGroup
from workos.utils.pagination_order import Type


class TestDirectorySync(object):
    @pytest.fixture(autouse=True)
    def setup(self, set_api_key):
        self.directory_sync = DirectorySync()

    @pytest.fixture
    def mock_users(self):

        user_list = [MockDirectoryUser(f"id{i}").to_dict() for i in range(5000)]

        return {
            "data": user_list,
            "list_metadata": {"before": None, "after": None},
        }

    @pytest.fixture
    def mock_groups(self):

        group_list = [MockDirectoryGroup(f"id{i}").to_dict() for i in range(5000)]

        return {
            "data": group_list,
            "list_metadata": {"before": None, "after": None},
        }

    @pytest.fixture
    def mock_user_primary_email(self):
        return {"primary": "true", "type": "work", "value": "marcelina@foo-corp.com"}

    @pytest.fixture
    def mock_user(self):
        return MockDirectoryUser("directory_user_01E1JG7J09H96KYP8HM9B0G5SJ").to_dict()

    @pytest.fixture
    def mock_user_no_email(self):
        return {
            "id": "directory_user_01E1JG7J09H96KYP8HM9B0GZZZ",
            "idp_id": "2836",
            "directory_id": "directory_01ECAZ4NV9QMV47GW873HDCX74",
            "organization_id": "org_01EZTR6WYX1A0DSE2CYMGXQ24Y",
            "first_name": "Marcelina",
            "last_name": "Davis",
            "job_title": "Software Engineer",
            "emails": [],
            "username": "marcelina@foo-corp.com",
            "groups": [
                {
                    "id": "directory_group_01E64QTDNS0EGJ0FMCVY9BWGZT",
                    "name": "Engineering",
                    "created_at": "2021-06-25T19:07:33.155Z",
                    "updated_at": "2021-06-25T19:07:33.155Z",
                    "raw_attributes": {"work_email": "124@gmail.com"},
                }
            ],
            "state": "active",
            "created_at": "2021-06-25T19:07:33.155Z",
            "updated_at": "2021-06-25T19:07:33.155Z",
            "custom_attributes": {"department": "Engineering"},
            "raw_attributes": {},
        }

    @pytest.fixture
    def mock_group(self):
        return MockDirectoryGroup(
            f"directory_group_01FHGRYAQ6ERZXXXXXX1E01QFE"
        ).to_dict()

    @pytest.fixture
    def mock_user_groups(self):
        return [{"name": "Developers", "id": "directory_grp_id"}]

    @pytest.fixture
    def mock_directories(self):

        directory_list = [MockDirectory(f"id{i}").to_dict() for i in range(5000)]

        return {
            "data": directory_list,
            "list_metadata": {"before": None, "after": None},
        }

    @pytest.fixture
    def mock_directory(self):
        return MockDirectory("directory_id").to_dict()

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

        group = self.directory_sync.get_group(
            group="directory_group_01FHGRYAQ6ERZXXXXXX1E01QFE"
        )

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

    def test_primary_email(
        self, mock_user, mock_user_primary_email, mock_request_method
    ):
        mock_request_method("get", mock_user, 200)
        mock_user_instance = self.directory_sync.get_user(
            "directory_user_01E1JG7J09H96KYP8HM9B0G5SJ"
        )
        primary_email = WorkOSDirectoryUser.construct_from_response(
            mock_user_instance
        ).primary_email()

        assert primary_email == mock_user_primary_email

    def test_primary_email_none(self, mock_user_no_email, mock_request_method):
        mock_request_method("get", mock_user_no_email, 200)
        mock_user_instance = self.directory_sync.get_user(
            "directory_user_01E1JG7J09H96KYP8HM9B0G5SJ"
        )
        primary_email = WorkOSDirectoryUser.construct_from_response(mock_user_instance)
        me = primary_email.primary_email()

        assert me == None

    def test_directories_auto_pagination(self, mock_directories, mock_request_method):
        mock_request_method("get", mock_directories, 200)
        directories = self.directory_sync.list_directories()

        all_directories = WorkOSListResource.construct_from_response(
            directories
        ).auto_paginate(Type.Directories)

        assert len(all_directories) == len(mock_directories["data"])

    def test_directory_users_auto_pagination(self, mock_users, mock_request_method):
        mock_request_method("get", mock_users, 200)
        users = self.directory_sync.list_users()

        all_users = WorkOSListResource.construct_from_response(users).auto_paginate(
            Type.DirectoryUsers
        )

        assert len(all_users) == len(mock_users["data"])

    def test_directory_user_groups_auto_pagination(
        self, mock_groups, mock_request_method
    ):
        mock_request_method("get", mock_groups, 200)
        groups = self.directory_sync.list_groups(directory="directory_grp_id")

        all_groups = WorkOSListResource.construct_from_response(groups).auto_paginate(
            Type.DirectoryGroups
        )

        assert len(all_groups) == len(mock_groups["data"])
