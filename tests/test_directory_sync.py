import pytest

from tests.utils.list_resource import list_data_to_dicts, list_response_of
from workos.directory_sync import AsyncDirectorySync, DirectorySync
from workos.utils.http_client import AsyncHTTPClient, SyncHTTPClient
from tests.utils.fixtures.mock_directory import MockDirectory
from tests.utils.fixtures.mock_directory_user import MockDirectoryUser
from tests.utils.fixtures.mock_directory_group import MockDirectoryGroup


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


class DirectorySyncFixtures:
    @pytest.fixture
    def mock_users(self):
        user_list = [MockDirectoryUser(id=str(i)).to_dict() for i in range(100)]

        return {
            "data": user_list,
            "list_metadata": {"before": None, "after": None},
            "object": "list",
        }

    @pytest.fixture
    def mock_groups(self):
        group_list = [MockDirectoryGroup(id=str(i)).to_dict() for i in range(20)]
        return list_response_of(data=group_list, after="xxx")

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
        directory_list = [MockDirectory(id=str(i)).to_dict() for i in range(1)]
        return list_response_of(data=directory_list)

    @pytest.fixture
    def mock_directory_users_multiple_data_pages(self):
        return [
            MockDirectoryUser(id=str(f"directory_user_{i}")).to_dict()
            for i in range(40)
        ]

    @pytest.fixture
    def mock_directories_multiple_data_pages(self):
        return [MockDirectory(id=str(f"dir_{i}")).to_dict() for i in range(40)]

    @pytest.fixture
    def mock_directory_groups_multiple_data_pages(self):
        return [
            MockDirectoryGroup(id=str(f"directory_group_{i}")).to_dict()
            for i in range(40)
        ]

    @pytest.fixture
    def mock_directory(self):
        return MockDirectory("directory_id").to_dict()


class TestDirectorySync(DirectorySyncFixtures):
    @pytest.fixture(autouse=True)
    def setup(self, set_api_key, set_client_id):
        self.http_client = SyncHTTPClient(
            base_url="https://api.workos.test", version="test"
        )
        self.directory_sync = DirectorySync(http_client=self.http_client)

    def test_list_users_with_directory(
        self, mock_users, mock_http_client_with_response
    ):
        mock_http_client_with_response(
            http_client=self.http_client, status_code=200, response_dict=mock_users
        )

        users = self.directory_sync.list_users(directory="directory_id")

        assert list_data_to_dicts(users.data) == mock_users["data"]

    def test_list_users_with_group(self, mock_users, mock_http_client_with_response):
        mock_http_client_with_response(
            http_client=self.http_client, status_code=200, response_dict=mock_users
        )

        users = self.directory_sync.list_users(group="directory_grp_id")

        assert list_data_to_dicts(users.data) == mock_users["data"]

    def test_list_groups_with_directory(
        self, mock_groups, mock_http_client_with_response
    ):
        mock_http_client_with_response(
            http_client=self.http_client, status_code=200, response_dict=mock_groups
        )

        groups = self.directory_sync.list_groups(directory="directory_id")

        assert list_data_to_dicts(groups.data) == mock_groups["data"]

    def test_list_groups_with_user(self, mock_groups, mock_http_client_with_response):
        mock_http_client_with_response(
            http_client=self.http_client, status_code=200, response_dict=mock_groups
        )

        groups = self.directory_sync.list_groups(user="directory_usr_id")

        assert list_data_to_dicts(groups.data) == mock_groups["data"]

    def test_get_user(self, mock_user, mock_http_client_with_response):
        mock_http_client_with_response(
            http_client=self.http_client,
            status_code=200,
            response_dict=mock_user,
        )

        user = self.directory_sync.get_user(user="directory_usr_id")

        assert user.dict() == mock_user

    def test_get_group(self, mock_group, mock_http_client_with_response):
        mock_http_client_with_response(
            http_client=self.http_client,
            status_code=200,
            response_dict=mock_group,
        )

        group = self.directory_sync.get_group(
            group="directory_group_01FHGRYAQ6ERZXXXXXX1E01QFE"
        )

        assert group.dict() == mock_group

    def test_list_directories(self, mock_directories, mock_http_client_with_response):
        mock_http_client_with_response(
            http_client=self.http_client,
            status_code=200,
            response_dict=mock_directories,
        )

        directories = self.directory_sync.list_directories()

        assert list_data_to_dicts(directories.data) == api_directories_to_sdk(
            mock_directories["data"]
        )

    def test_get_directory(self, mock_directory, mock_http_client_with_response):
        mock_http_client_with_response(
            http_client=self.http_client,
            status_code=200,
            response_dict=mock_directory,
        )

        directory = self.directory_sync.get_directory(directory="directory_id")

        assert directory.dict() == api_directory_to_sdk(mock_directory)

    def test_delete_directory(self, mock_http_client_with_response):
        mock_http_client_with_response(
            http_client=self.http_client,
            status_code=202,
            response_dict=None,
            headers={"content-type": "text/plain; charset=utf-8"},
        )

        response = self.directory_sync.delete_directory(directory="directory_id")

        assert response is None

    def test_primary_email(
        self, mock_user, mock_user_primary_email, mock_http_client_with_response
    ):
        mock_http_client_with_response(
            http_client=self.http_client,
            status_code=200,
            response_dict=mock_user,
        )
        mock_user_instance = self.directory_sync.get_user(
            "directory_user_01E1JG7J09H96KYP8HM9B0G5SJ"
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
        mock_user_instance = self.directory_sync.get_user(
            "directory_user_01E1JG7J09H96KYP8HM9B0G5SJ"
        )

        me = mock_user_instance.primary_email()

        assert me == None

    def test_list_directories_auto_pagination(
        self,
        mock_directories_multiple_data_pages,
        mock_pagination_request_for_http_client,
    ):
        mock_pagination_request_for_http_client(
            http_client=self.http_client,
            data_list=mock_directories_multiple_data_pages,
            status_code=200,
        )

        directories = self.directory_sync.list_directories()
        all_directories = []

        for directory in directories.auto_paging_iter():
            all_directories.append(directory)

        assert len(list(all_directories)) == len(mock_directories_multiple_data_pages)
        assert (list_data_to_dicts(all_directories)) == api_directories_to_sdk(
            mock_directories_multiple_data_pages
        )

    def test_directory_users_auto_pagination(
        self,
        mock_directory_users_multiple_data_pages,
        mock_pagination_request_for_http_client,
    ):
        mock_pagination_request_for_http_client(
            http_client=self.http_client,
            data_list=mock_directory_users_multiple_data_pages,
            status_code=200,
        )

        users = self.directory_sync.list_users()
        all_users = []

        for user in users.auto_paging_iter():
            all_users.append(user)

        assert len(list(all_users)) == len(mock_directory_users_multiple_data_pages)
        assert (
            list_data_to_dicts(all_users)
        ) == mock_directory_users_multiple_data_pages

    def test_directory_user_groups_auto_pagination(
        self,
        mock_directory_groups_multiple_data_pages,
        mock_pagination_request_for_http_client,
    ):
        mock_pagination_request_for_http_client(
            http_client=self.http_client,
            data_list=mock_directory_groups_multiple_data_pages,
            status_code=200,
        )

        groups = self.directory_sync.list_groups()
        all_groups = []

        for group in groups.auto_paging_iter():
            all_groups.append(group)

        assert len(list(all_groups)) == len(mock_directory_groups_multiple_data_pages)
        assert (
            list_data_to_dicts(all_groups)
        ) == mock_directory_groups_multiple_data_pages

    def test_auto_pagination_honors_limit(
        self,
        mock_directories_multiple_data_pages,
        mock_pagination_request_for_http_client,
    ):
        # TODO: This does not actually test anything about the limit.
        mock_pagination_request_for_http_client(
            http_client=self.http_client,
            data_list=mock_directories_multiple_data_pages,
            status_code=200,
        )

        directories = self.directory_sync.list_directories()
        all_directories = []

        for directory in directories.auto_paging_iter():
            all_directories.append(directory)

        assert len(list(all_directories)) == len(mock_directories_multiple_data_pages)
        assert (list_data_to_dicts(all_directories)) == api_directories_to_sdk(
            mock_directories_multiple_data_pages
        )


@pytest.mark.asyncio
class TestAsyncDirectorySync(DirectorySyncFixtures):
    @pytest.fixture(autouse=True)
    def setup(self, set_api_key, set_client_id):
        self.http_client = AsyncHTTPClient(
            base_url="https://api.workos.test",
            version="test",
        )
        self.directory_sync = AsyncDirectorySync(http_client=self.http_client)

    async def test_list_users_with_directory(
        self, mock_users, mock_http_client_with_response
    ):
        mock_http_client_with_response(
            http_client=self.http_client, status_code=200, response_dict=mock_users
        )

        users = await self.directory_sync.list_users(directory="directory_id")

        assert list_data_to_dicts(users.data) == mock_users["data"]

    async def test_list_users_with_group(
        self, mock_users, mock_http_client_with_response
    ):
        mock_http_client_with_response(
            http_client=self.http_client, status_code=200, response_dict=mock_users
        )

        users = await self.directory_sync.list_users(group="directory_grp_id")

        assert list_data_to_dicts(users.data) == mock_users["data"]

    async def test_list_groups_with_directory(
        self, mock_groups, mock_http_client_with_response
    ):
        mock_http_client_with_response(
            http_client=self.http_client, status_code=200, response_dict=mock_groups
        )

        groups = await self.directory_sync.list_groups(directory="directory_id")

        assert list_data_to_dicts(groups.data) == mock_groups["data"]

    async def test_list_groups_with_user(
        self, mock_groups, mock_http_client_with_response
    ):
        mock_http_client_with_response(
            http_client=self.http_client, status_code=200, response_dict=mock_groups
        )

        groups = await self.directory_sync.list_groups(user="directory_usr_id")

        assert list_data_to_dicts(groups.data) == mock_groups["data"]

    async def test_get_user(self, mock_user, mock_http_client_with_response):
        mock_http_client_with_response(
            http_client=self.http_client,
            status_code=200,
            response_dict=mock_user,
        )

        user = await self.directory_sync.get_user(user="directory_usr_id")

        assert user.dict() == mock_user

    async def test_get_group(self, mock_group, mock_http_client_with_response):
        mock_http_client_with_response(
            http_client=self.http_client,
            status_code=200,
            response_dict=mock_group,
        )

        group = await self.directory_sync.get_group(
            group="directory_group_01FHGRYAQ6ERZXXXXXX1E01QFE"
        )

        assert group.dict() == mock_group

    async def test_list_directories(
        self, mock_directories, mock_http_client_with_response
    ):
        mock_http_client_with_response(
            http_client=self.http_client,
            status_code=200,
            response_dict=mock_directories,
        )

        directories = await self.directory_sync.list_directories()

        assert list_data_to_dicts(directories.data) == api_directories_to_sdk(
            mock_directories["data"]
        )

    async def test_get_directory(self, mock_directory, mock_http_client_with_response):
        mock_http_client_with_response(
            http_client=self.http_client,
            status_code=200,
            response_dict=mock_directory,
        )

        directory = await self.directory_sync.get_directory(directory="directory_id")

        assert directory.dict() == api_directory_to_sdk(mock_directory)

    async def test_delete_directory(self, mock_http_client_with_response):
        mock_http_client_with_response(
            http_client=self.http_client,
            status_code=202,
            response_dict=None,
            headers={"content-type": "text/plain; charset=utf-8"},
        )

        response = await self.directory_sync.delete_directory(directory="directory_id")

        assert response is None

    async def test_primary_email(
        self, mock_user, mock_user_primary_email, mock_http_client_with_response
    ):
        mock_http_client_with_response(
            http_client=self.http_client,
            status_code=200,
            response_dict=mock_user,
        )
        mock_user_instance = await self.directory_sync.get_user(
            "directory_user_01E1JG7J09H96KYP8HM9B0G5SJ"
        )
        primary_email = mock_user_instance.primary_email()
        assert primary_email
        assert primary_email.dict() == mock_user_primary_email

    async def test_primary_email_none(
        self, mock_user_no_email, mock_http_client_with_response
    ):
        mock_http_client_with_response(
            http_client=self.http_client,
            status_code=200,
            response_dict=mock_user_no_email,
        )
        mock_user_instance = await self.directory_sync.get_user(
            "directory_user_01E1JG7J09H96KYP8HM9B0G5SJ"
        )

        me = mock_user_instance.primary_email()

        assert me == None

    async def test_list_directories_auto_pagination(
        self,
        mock_directories_multiple_data_pages,
        mock_pagination_request_for_http_client,
    ):
        mock_pagination_request_for_http_client(
            http_client=self.http_client,
            data_list=mock_directories_multiple_data_pages,
            status_code=200,
        )

        directories = await self.directory_sync.list_directories()
        all_directories = []

        async for directory in directories.auto_paging_iter():
            all_directories.append(directory)

        assert len(list(all_directories)) == len(mock_directories_multiple_data_pages)
        assert (list_data_to_dicts(all_directories)) == api_directories_to_sdk(
            mock_directories_multiple_data_pages
        )

    async def test_directory_users_auto_pagination(
        self,
        mock_directory_users_multiple_data_pages,
        mock_pagination_request_for_http_client,
    ):
        mock_pagination_request_for_http_client(
            http_client=self.http_client,
            data_list=mock_directory_users_multiple_data_pages,
            status_code=200,
        )

        users = await self.directory_sync.list_users()
        all_users = []

        async for user in users.auto_paging_iter():
            all_users.append(user)

        assert len(list(all_users)) == len(mock_directory_users_multiple_data_pages)
        assert (
            list_data_to_dicts(all_users)
        ) == mock_directory_users_multiple_data_pages

    async def test_directory_user_groups_auto_pagination(
        self,
        mock_directory_groups_multiple_data_pages,
        mock_pagination_request_for_http_client,
    ):
        mock_pagination_request_for_http_client(
            http_client=self.http_client,
            data_list=mock_directory_groups_multiple_data_pages,
            status_code=200,
        )

        groups = await self.directory_sync.list_groups()
        all_groups = []

        async for group in groups.auto_paging_iter():
            all_groups.append(group)

        assert len(list(all_groups)) == len(mock_directory_groups_multiple_data_pages)
        assert (
            list_data_to_dicts(all_groups)
        ) == mock_directory_groups_multiple_data_pages

    async def test_auto_pagination_honors_limit(
        self,
        mock_directories_multiple_data_pages,
        mock_pagination_request_for_http_client,
    ):
        # TODO: This does not actually test anything about the limit.
        mock_pagination_request_for_http_client(
            http_client=self.http_client,
            data_list=mock_directories_multiple_data_pages,
            status_code=200,
        )

        directories = await self.directory_sync.list_directories()
        all_directories = []

        async for directory in directories.auto_paging_iter():
            all_directories.append(directory)

        assert len(list(all_directories)) == len(mock_directories_multiple_data_pages)
        assert (list_data_to_dicts(all_directories)) == api_directories_to_sdk(
            mock_directories_multiple_data_pages
        )
