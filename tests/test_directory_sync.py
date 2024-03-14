import pytest
from workos.directory_sync import DirectorySync
from workos.resources.directory_sync import WorkOSDirectoryUser
from tests.utils.fixtures.mock_directory import MockDirectory
from tests.utils.fixtures.mock_directory_user import MockDirectoryUser
from tests.utils.fixtures.mock_directory_group import MockDirectoryGroup


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
                "method": DirectorySync.list_users,
            },
        }

    @pytest.fixture
    def mock_default_limit_users(self):
        user_list = [MockDirectoryUser(id=str(i)).to_dict() for i in range(10)]

        return {
            "data": user_list,
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
                "method": DirectorySync.list_users,
            },
        }

    @pytest.fixture
    def mock_default_limit_users_v2(self):
        user_list = [MockDirectoryUser(id=str(i)).to_dict() for i in range(10)]

        dict_response = {
            "data": user_list,
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
                "method": DirectorySync.list_users,
            },
        }

        return self.directory_sync.construct_from_response(dict_response)

    @pytest.fixture
    def mock_users_pagination_response(self):
        user_list = [MockDirectoryUser(id=str(i)).to_dict() for i in range(90)]

        return {
            "data": user_list,
            "list_metadata": {"before": None, "after": None},
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
                "method": DirectorySync.list_users,
            },
        }

    @pytest.fixture
    def mock_groups(self):
        group_list = [MockDirectoryGroup(id=str(i)).to_dict() for i in range(5000)]

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
    def mock_default_limit_groups_v2(self):
        group_list = [MockDirectoryGroup(id=str(i)).to_dict() for i in range(10)]

        dict_response = {
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

        return self.directory_sync.construct_from_response(dict_response)

    @pytest.fixture
    def mock_groups_pagination_reponse(self):
        group_list = [MockDirectoryGroup(id=str(i)).to_dict() for i in range(4990)]

        return {
            "data": group_list,
            "list_metadata": {"before": None, "after": None},
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
            "directory_group_01FHGRYAQ6ERZXXXXXX1E01QFE"
        ).to_dict()

    @pytest.fixture
    def mock_directories(self):
        directory_list = [MockDirectory(id=str(i)).to_dict() for i in range(5000)]

        return {
            "data": directory_list,
            "list_metadata": {"before": None, "after": None},
            "metadata": {
                "params": {
                    "domain": None,
                    "organization_id": None,
                    "search": None,
                    "limit": None,
                    "before": None,
                    "after": None,
                    "order": None,
                    "default_limit": True,
                },
                "method": DirectorySync.list_directories,
            },
        }

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
    def mock_directories_with_limit_v2(self):
        directory_list = [MockDirectory(id=str(i)).to_dict() for i in range(4)]

        dict_response = {
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

        return self.directory_sync.construct_from_response(dict_response)

    @pytest.fixture
    def mock_default_limit_directories(self):
        directory_list = [MockDirectory(id=str(i)).to_dict() for i in range(10)]

        return {
            "data": directory_list,
            "list_metadata": {"before": None, "after": "directory_id_xx"},
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
                "method": DirectorySync.list_directories,
            },
        }

    @pytest.fixture
    def mock_default_limit_directories_v2(self):
        directory_list = [MockDirectory(id=str(i)).to_dict() for i in range(10)]

        dict_response = {
            "data": directory_list,
            "list_metadata": {"before": None, "after": "directory_id_xx"},
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
                "method": DirectorySync.list_directories,
            },
        }

        return self.directory_sync.construct_from_response(dict_response)

    @pytest.fixture
    def mock_directories_pagination_response(self):
        directory_list = [MockDirectory(id=str(i)).to_dict() for i in range(4990)]

        return {
            "data": directory_list,
            "list_metadata": {"before": None, "after": None},
            "metadata": {
                "params": {
                    "domain": None,
                    "organization_id": None,
                    "search": None,
                    "limit": None,
                    "before": None,
                    "after": None,
                    "order": None,
                    "default_limit": True,
                },
                "method": DirectorySync.list_directories,
            },
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

    def test_directories_auto_pagination(
        self,
        mock_default_limit_directories,
        mock_directories_pagination_response,
        mock_directories,
        mock_request_method,
    ):
        mock_request_method("get", mock_directories_pagination_response, 200)

        directories = mock_default_limit_directories

        all_directories = DirectorySync.construct_from_response(
            directories
        ).auto_paging_iter()

        assert len(*list(all_directories)) == len(mock_directories["data"])

    def test_list_directories_auto_pagination_v2(
        self,
        mock_default_limit_directories_v2,
        mock_directories_pagination_response,
        mock_directories,
        mock_request_method,
    ):
        directories = mock_default_limit_directories_v2
        mock_request_method("get", mock_directories_pagination_response, 200)
        all_directories = directories.auto_paging_iter()

        assert len(*list(all_directories)) == len(mock_directories["data"])

    def test_directory_users_auto_pagination(
        self,
        mock_users,
        mock_default_limit_users,
        mock_users_pagination_response,
        mock_request_method,
    ):
        mock_request_method("get", mock_users_pagination_response, 200)
        users = mock_default_limit_users

        all_users = DirectorySync.construct_from_response(users).auto_paging_iter()

        assert len(*list(all_users)) == len(mock_users["data"])

    def test_directory_users_auto_pagination_v2(
        self,
        mock_users,
        mock_default_limit_users_v2,
        mock_users_pagination_response,
        mock_request_method,
    ):
        mock_request_method("get", mock_users_pagination_response, 200)
        users = mock_default_limit_users_v2

        all_users = users.auto_paging_iter()

        assert len(*list(all_users)) == len(mock_users["data"])

    def test_directory_user_groups_auto_pagination(
        self,
        mock_groups,
        mock_default_limit_groups,
        mock_groups_pagination_reponse,
        mock_request_method,
    ):
        mock_request_method("get", mock_groups_pagination_reponse, 200)

        groups = mock_default_limit_groups
        all_groups = DirectorySync.construct_from_response(groups).auto_paging_iter()

        assert len(*list(all_groups)) == len(mock_groups["data"])

    def test_directory_user_groups_auto_pagination_v2(
        self,
        mock_groups,
        mock_default_limit_groups_v2,
        mock_groups_pagination_reponse,
        mock_request_method,
    ):
        mock_request_method("get", mock_groups_pagination_reponse, 200)

        groups = mock_default_limit_groups_v2
        all_groups = groups.auto_paging_iter()

        assert len(*list(all_groups)) == len(mock_groups["data"])

    def test_auto_pagination_honors_limit(
        self,
        mock_directories_with_limit,
        mock_directories_pagination_response,
        mock_request_method,
    ):
        mock_request_method("get", mock_directories_pagination_response, 200)

        directories = mock_directories_with_limit

        all_directories = DirectorySync.construct_from_response(
            directories
        ).auto_paging_iter()

        assert len(*list(all_directories)) == len(mock_directories_with_limit["data"])

    def test_auto_pagination_honors_limit_v2(
        self,
        mock_directories_with_limit_v2,
        mock_directories_pagination_response,
        mock_request_method,
    ):
        mock_request_method("get", mock_directories_pagination_response, 200)

        directories = mock_directories_with_limit_v2
        dict_directories = mock_directories_with_limit_v2.to_dict()
        all_directories = directories.auto_paging_iter()

        assert len(*list(all_directories)) == len(dict_directories["data"])

    def test_list_directories_returns_metadata(
        self,
        mock_directories,
        mock_request_method,
    ):
        mock_request_method("get", mock_directories, 200)
        directories = self.directory_sync.list_directories(
            organization="Planet Express"
        )

        assert directories["metadata"]["params"]["organization_id"] == "Planet Express"

    def test_list_directories_returns_metadata_v2(
        self,
        mock_directories,
        mock_request_method,
    ):
        mock_request_method("get", mock_directories, 200)
        directories = self.directory_sync.list_directories_v2(
            organization="Planet Express"
        )
        dict_directories = directories.to_dict()

        assert (
            dict_directories["metadata"]["params"]["organization_id"]
            == "Planet Express"
        )
