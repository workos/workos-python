from typing import Union

import pytest
from workos.directory_sync import AsyncDirectorySync, DirectorySync

from tests.types.test_auto_pagination_function import TestAutoPaginationFunction
from tests.utils.fixtures.mock_directory import (
    MockDirectory,
    MockDirectoryMetadata,
    MockDirectoryUsersMetadata,
)
from tests.utils.fixtures.mock_directory_group import MockDirectoryGroup
from tests.utils.fixtures.mock_directory_user import MockDirectoryUser
from tests.utils.list_resource import list_data_to_dicts, list_response_of
from tests.utils.syncify import syncify


def api_directory_to_sdk(directory):
    # The API returns an active directory as 'linked'
    # We normalize this to 'active' in the SDK. This helper function
    # does this conversion to make make assertions easier.
    if directory["state"] == "linked":
        return {**directory, "state": "active"}
    else:
        return directory


def api_directories_to_sdk(directories):
    return list(map(lambda x: api_directory_to_sdk(x), directories))


@pytest.mark.sync_and_async(DirectorySync, AsyncDirectorySync)
class TestDirectorySync:
    @pytest.fixture(autouse=True)
    def setup(self, module_instance: Union[DirectorySync, AsyncDirectorySync]):
        self.http_client = module_instance._http_client
        self.directory_sync = module_instance

    @pytest.fixture
    def mock_users(self):
        user_list = [MockDirectoryUser(id=str(i)).dict() for i in range(100)]

        return {
            "data": user_list,
            "list_metadata": {"before": None, "after": None},
            "object": "list",
        }

    @pytest.fixture
    def mock_groups(self):
        group_list = [MockDirectoryGroup(id=str(i)).dict() for i in range(20)]
        return list_response_of(data=group_list, after="xxx")

    @pytest.fixture
    def mock_user_primary_email(self):
        return {"primary": True, "type": "work", "value": "marcelina@foo-corp.com"}

    @pytest.fixture
    def mock_user(self):
        return MockDirectoryUser("directory_user_01E1JG7J09H96KYP8HM9B0G5SJ").dict()

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
            "email": None,
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
        return MockDirectoryGroup("directory_group_01FHGRYAQ6ERZXXXXXX1E01QFE").dict()

    @pytest.fixture
    def mock_directories(self):
        directory_list = [MockDirectory(id=str(i)).dict() for i in range(10)]
        return list_response_of(data=directory_list)

    @pytest.fixture
    def mock_directories_with_metadata(self):
        metadata = MockDirectoryMetadata(
            users=MockDirectoryUsersMetadata(active=1, inactive=0), groups=1
        )
        directory_list = [
            MockDirectory(id=str(i), metadata=metadata).dict() for i in range(10)
        ]
        return list_response_of(data=directory_list)

    @pytest.fixture
    def mock_directory_users_multiple_data_pages(self):
        return [
            MockDirectoryUser(id=str(f"directory_user_{i}")).dict() for i in range(40)
        ]

    @pytest.fixture
    def mock_directories_multiple_data_pages(self):
        return [MockDirectory(id=str(f"dir_{i}")).dict() for i in range(40)]

    @pytest.fixture
    def mock_directory_groups_multiple_data_pages(self):
        return [
            MockDirectoryGroup(id=str(f"directory_group_{i}")).dict() for i in range(40)
        ]

    @pytest.fixture
    def mock_directory(self):
        return MockDirectory("directory_id").dict()

    def test_list_users_with_directory(
        self, mock_users, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            http_client=self.http_client, status_code=200, response_dict=mock_users
        )

        users = syncify(self.directory_sync.list_users(directory_id="directory_id"))

        assert list_data_to_dicts(users.data) == mock_users["data"]
        assert request_kwargs["url"].endswith("/directory_users")
        assert request_kwargs["method"] == "get"
        assert request_kwargs["params"] == {
            "directory": "directory_id",
            "limit": 10,
            "order": "desc",
        }

    def test_list_users_with_group(
        self, mock_users, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            http_client=self.http_client, status_code=200, response_dict=mock_users
        )

        users = syncify(self.directory_sync.list_users(group_id="directory_grp_id"))

        assert list_data_to_dicts(users.data) == mock_users["data"]
        assert request_kwargs["url"].endswith("/directory_users")
        assert request_kwargs["method"] == "get"
        assert request_kwargs["params"] == {
            "group": "directory_grp_id",
            "limit": 10,
            "order": "desc",
        }

    def test_list_groups_with_directory(
        self, mock_groups, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            http_client=self.http_client, status_code=200, response_dict=mock_groups
        )

        groups = syncify(self.directory_sync.list_groups(directory_id="directory_id"))

        assert list_data_to_dicts(groups.data) == mock_groups["data"]
        assert request_kwargs["url"].endswith("/directory_groups")
        assert request_kwargs["method"] == "get"
        assert request_kwargs["params"] == {
            "directory": "directory_id",
            "limit": 10,
            "order": "desc",
        }

    def test_list_groups_with_user(
        self, mock_groups, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            http_client=self.http_client, status_code=200, response_dict=mock_groups
        )

        groups = syncify(self.directory_sync.list_groups(user_id="directory_user_id"))

        assert list_data_to_dicts(groups.data) == mock_groups["data"]
        assert request_kwargs["url"].endswith("/directory_groups")
        assert request_kwargs["method"] == "get"
        assert request_kwargs["params"] == {
            "user": "directory_user_id",
            "limit": 10,
            "order": "desc",
        }

    def test_get_user(self, mock_user, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            http_client=self.http_client,
            status_code=200,
            response_dict=mock_user,
        )

        user = syncify(self.directory_sync.get_user(user_id="directory_user_id"))

        assert user.dict() == mock_user
        assert request_kwargs["url"].endswith("/directory_users/directory_user_id")
        assert request_kwargs["method"] == "get"

    def test_get_group(self, mock_group, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            http_client=self.http_client,
            status_code=200,
            response_dict=mock_group,
        )

        group = syncify(
            self.directory_sync.get_group(
                group_id="directory_group_01FHGRYAQ6ERZXXXXXX1E01QFE"
            )
        )

        assert group.dict() == mock_group
        assert request_kwargs["url"].endswith(
            "/directory_groups/directory_group_01FHGRYAQ6ERZXXXXXX1E01QFE"
        )
        assert request_kwargs["method"] == "get"

    def test_list_directories(
        self, mock_directories, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            http_client=self.http_client,
            status_code=200,
            response_dict=mock_directories,
        )

        directories = syncify(self.directory_sync.list_directories())

        assert list_data_to_dicts(directories.data) == api_directories_to_sdk(
            mock_directories["data"]
        )
        assert request_kwargs["url"].endswith("/directories")
        assert request_kwargs["method"] == "get"
        assert request_kwargs["params"] == {
            "limit": 10,
            "order": "desc",
        }

    def test_list_directories_with_metadata(
        self, mock_directories_with_metadata, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            http_client=self.http_client,
            status_code=200,
            response_dict=mock_directories_with_metadata,
        )

        directories = syncify(self.directory_sync.list_directories())

        assert list_data_to_dicts(directories.data) == api_directories_to_sdk(
            mock_directories_with_metadata["data"]
        )
        assert request_kwargs["url"].endswith("/directories")
        assert request_kwargs["method"] == "get"
        assert request_kwargs["params"] == {
            "limit": 10,
            "order": "desc",
        }

    def test_get_directory(self, mock_directory, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            http_client=self.http_client,
            status_code=200,
            response_dict=mock_directory,
        )

        directory = syncify(
            self.directory_sync.get_directory(directory_id="directory_id")
        )

        assert directory.dict() == api_directory_to_sdk(mock_directory)
        assert request_kwargs["url"].endswith("/directories/directory_id")
        assert request_kwargs["method"] == "get"

    def test_delete_directory(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            http_client=self.http_client,
            status_code=202,
            headers={"content-type": "text/plain; charset=utf-8"},
        )

        response = syncify(
            self.directory_sync.delete_directory(directory_id="directory_id")
        )

        assert request_kwargs["url"].endswith("/directories/directory_id")
        assert request_kwargs["method"] == "delete"
        assert response is None

    def test_primary_email(
        self, mock_user, mock_user_primary_email, mock_http_client_with_response
    ):
        mock_http_client_with_response(
            http_client=self.http_client,
            status_code=200,
            response_dict=mock_user,
        )
        mock_user_instance = syncify(
            self.directory_sync.get_user("directory_user_01E1JG7J09H96KYP8HM9B0G5SJ")
        )
        primary_email = mock_user_instance.primary_email()
        assert primary_email
        assert primary_email.dict() == mock_user_primary_email

    def test_primary_email_none(
        self, mock_user_no_email, mock_http_client_with_response
    ):
        mock_http_client_with_response(
            http_client=self.http_client,
            status_code=200,
            response_dict=mock_user_no_email,
        )
        mock_user_instance = syncify(
            self.directory_sync.get_user("directory_user_01E1JG7J09H96KYP8HM9B0G5SJ")
        )

        me = mock_user_instance.primary_email()

        assert me == None

    def test_list_directories_auto_pagination(
        self,
        mock_directories_multiple_data_pages,
        test_auto_pagination: TestAutoPaginationFunction,
    ):
        test_auto_pagination(
            http_client=self.http_client,
            list_function=self.directory_sync.list_directories,
            expected_all_page_data=mock_directories_multiple_data_pages,
        )

    def test_directory_users_auto_pagination(
        self,
        mock_directory_users_multiple_data_pages,
        test_auto_pagination: TestAutoPaginationFunction,
    ):
        test_auto_pagination(
            http_client=self.http_client,
            list_function=self.directory_sync.list_users,
            expected_all_page_data=mock_directory_users_multiple_data_pages,
        )

    def test_directory_user_groups_auto_pagination(
        self,
        mock_directory_groups_multiple_data_pages,
        test_auto_pagination: TestAutoPaginationFunction,
    ):
        test_auto_pagination(
            http_client=self.http_client,
            list_function=self.directory_sync.list_groups,
            expected_all_page_data=mock_directory_groups_multiple_data_pages,
        )
