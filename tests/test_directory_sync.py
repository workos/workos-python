import pytest
import requests
from tests.conftest import MockResponse, mock_pagination_request
from tests.utils.list_resource import list_data_to_dicts, list_response_of
from workos.directory_sync import DirectorySync
from workos.resources.directory_sync import DirectoryUser
from tests.utils.fixtures.mock_directory import MockDirectory
from tests.utils.fixtures.mock_directory_user import MockDirectoryUser
from tests.utils.fixtures.mock_directory_group import MockDirectoryGroup
from workos.resources.list import WorkOsListResource


class TestDirectorySync(object):
    @pytest.fixture(autouse=True)
    def setup(self, set_api_key, set_client_id):
        self.directory_sync = DirectorySync()

    @pytest.fixture
    def mock_users(self):
        user_list = [MockDirectoryUser(id=str(i)).to_dict() for i in range(100)]

        return {
            "data": user_list,
            "list_metadata": {"before": None, "after": None},
            "object": "list",
        }

    @pytest.fixture
    def mock_users_pagination_response(self):
        user_list = [MockDirectoryUser(id=str(i)).to_dict() for i in range(40)]

        return list_response_of(data=user_list)

    @pytest.fixture
    def mock_groups(self):
        group_list = [MockDirectoryGroup(id=str(i)).to_dict() for i in range(20)]
        return list_response_of(data=group_list, after="xxx")

    @pytest.fixture
    def mock_default_limit_groups(self):
        group_list = [MockDirectoryGroup(id=str(i)).to_dict() for i in range(10)]

        return {
            "data": group_list,
            "list_metadata": {"before": None, "after": "xxx"},
            "metadata": {
                "params": {
                    "domain": None,
                    "organization_id": None,
                    "search": None,
                    "limit": 10,
                    "before": None,
                    "after": None,
                    "order": None,
                    "default_limit": True,
                },
                "method": DirectorySync.list_groups,
            },
        }

    @pytest.fixture
    def mock_groups_pagination_response(self):
        group_list = [MockDirectoryGroup(id=str(i)).to_dict() for i in range(40)]
        return list_response_of(data=group_list)

    @pytest.fixture
    def mock_user_primary_email(self):
        return {"primary": True, "type": "work", "value": "marcelina@foo-corp.com"}

    @pytest.fixture
    def mock_user(self):
        return MockDirectoryUser("directory_user_01E1JG7J09H96KYP8HM9B0G5SJ").to_dict()

    @pytest.fixture
    def mock_user_no_email(self):
        return {
            "id": "directory_user_01E1JG7J09H96KYP8HM9B0GZZZ",
            "object": "directory_user",
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
                    "directory_id": "directory_01ECAZ4NV9QMV47GW873HDCX74",
                    "organization_id": "org_01EZTR6WYX1A0DSE2CYMGXQ24Y",
                    "object": "directory_group",
                    "idp_id": "2836",
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
            "directory_group_01FHGRYAQ6ERZXXXXXX1E01QFE"
        ).to_dict()

    @pytest.fixture
    def mock_directories(self):
        directory_list = [MockDirectory(id=str(i)).to_dict() for i in range(20)]
        return list_response_of(data=directory_list)

    @pytest.fixture
    def mock_directories_with_limit(self):
        directory_list = [MockDirectory(id=str(i)).to_dict() for i in range(4)]

        return {
            "data": directory_list,
            "list_metadata": {"before": None, "after": None},
            "metadata": {
                "params": {
                    "domain": None,
                    "organization_id": None,
                    "search": None,
                    "limit": 4,
                    "before": None,
                    "after": None,
                    "order": None,
                },
                "method": DirectorySync.list_directories,
            },
        }

    @pytest.fixture
    def mock_directories_pagination_response(self):
        directory_list = [MockDirectory(id=str(i)).to_dict() for i in range(40)]
        return list_response_of(data=directory_list)

    @pytest.fixture
    def mock_directories_multiple_data_pages(self):
        return [MockDirectory(id=str(f"dir_{i}")).to_dict() for i in range(40)]

    @pytest.fixture
    def mock_directory(self):
        return MockDirectory("directory_id").to_dict()

    def test_list_users_with_directory(self, mock_users, mock_request_method):
        mock_request_method("get", mock_users, 200)

        users = self.directory_sync.list_users(directory="directory_id")

        assert list_data_to_dicts(users.data) == mock_users["data"]

    def test_list_users_with_group(self, mock_users, mock_request_method):
        mock_request_method("get", mock_users, 200)

        users = self.directory_sync.list_users(group="directory_grp_id")

        assert list_data_to_dicts(users.data) == mock_users["data"]

    def test_list_groups_with_directory(self, mock_groups, mock_request_method):
        mock_request_method("get", mock_groups, 200)

        groups = self.directory_sync.list_groups(directory="directory_id")

        assert list_data_to_dicts(groups.data) == mock_groups["data"]

    def test_list_groups_with_user(self, mock_groups, mock_request_method):
        mock_request_method("get", mock_groups, 200)

        groups = self.directory_sync.list_groups(user="directory_usr_id")

        assert list_data_to_dicts(groups.data) == mock_groups["data"]

    def test_get_user(self, mock_user, mock_request_method):
        mock_request_method("get", mock_user, 200)

        user = self.directory_sync.get_user(user="directory_usr_id")

        assert user.dict() == mock_user

    def test_get_group(self, mock_group, mock_request_method):
        mock_request_method("get", mock_group, 200)

        group = self.directory_sync.get_group(
            group="directory_group_01FHGRYAQ6ERZXXXXXX1E01QFE"
        )

        assert group.dict() == mock_group

    def test_list_directories(self, mock_directories, mock_request_method):
        mock_request_method("get", mock_directories, 200)

        directories = self.directory_sync.list_directories()

        assert list_data_to_dicts(directories.data) == mock_directories["data"]

    def test_get_directory(self, mock_directory, mock_request_method):
        mock_request_method("get", mock_directory, 200)

        directory = self.directory_sync.get_directory(directory="directory_id")

        assert directory.dict() == mock_directory

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
        primary_email = mock_user_instance.primary_email()
        assert primary_email
        assert primary_email.dict() == mock_user_primary_email

    def test_primary_email_none(self, mock_user_no_email, mock_request_method):
        mock_request_method("get", mock_user_no_email, 200)
        mock_user_instance = self.directory_sync.get_user(
            "directory_user_01E1JG7J09H96KYP8HM9B0G5SJ"
        )

        me = mock_user_instance.primary_email()

        assert me == None

    def test_list_directories_auto_pagination(
        self,
        mock_directories_pagination_response,
        mock_directories,
        mock_request_method,
    ):
        mock_request_method("get", mock_directories_pagination_response, 200)

        directories = self.directory_sync.list_directories()
        all_directories = []
        # TODO: this is the same approach the the organizations test takes, but it's wrong.
        # this doesn't actually test that the iterator makes multiple requests for consecutive pages
        # of data. This test needs to be reworked to return multiple responses to properly test the
        # auto_paging_iter.
        for directory in directories.auto_paging_iter():
            all_directories.append(directory)

        assert len(list(all_directories)) == 40

        for i, dir in enumerate(all_directories):
            assert dir.id == str(i)

    def test_directory_users_auto_pagination(
        self,
        mock_users,
        mock_users_pagination_response,
        mock_request_method,
    ):
        mock_request_method("get", mock_users_pagination_response, 200)

        users = self.directory_sync.list_users()
        all_users = []
        # TODO: this is the same approach the the organizations test takes, but it's wrong.
        # this doesn't actually test that the iterator makes multiple requests for consecutive pages
        # of data. This test needs to be reworked to return multiple responses to properly test the
        # auto_paging_iter.
        for user in users.auto_paging_iter():
            all_users.append(user)

        assert len(list(all_users)) == 40

        for i, user in enumerate(all_users):
            assert user.id == str(i)

    def test_directory_user_groups_auto_pagination(
        self,
        mock_groups,
        mock_default_limit_groups,
        mock_groups_pagination_response,
        mock_request_method,
    ):
        mock_request_method("get", mock_groups_pagination_response, 200)

        groups = self.directory_sync.list_groups()
        all_groups = []
        # TODO: this is the same approach the the organizations test takes, but it's wrong.
        # this doesn't actually test that the iterator makes multiple requests for consecutive pages
        # of data. This test needs to be reworked to return multiple responses to properly test the
        # auto_paging_iter.
        for group in groups.auto_paging_iter():
            all_groups.append(group)

        assert len(list(all_groups)) == 40

        for i, group in enumerate(all_groups):
            assert group.id == str(i)

    def test_auto_pagination_honors_limit(
        self,
        mock_directories_multiple_data_pages,
        mock_pagination_request,
    ):
        mock_pagination_request("get", mock_directories_multiple_data_pages, 200)

        directories = self.directory_sync.list_directories()
        all_directories = []

        for directory in directories.auto_paging_iter():
            all_directories.append(directory)

        assert len(list(all_directories)) == len(mock_directories_multiple_data_pages)
        assert (
            list_data_to_dicts(all_directories)
        ) == mock_directories_multiple_data_pages
