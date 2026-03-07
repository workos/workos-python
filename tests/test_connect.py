from typing import Union
import pytest
from tests.types.test_auto_pagination_function import TestAutoPaginationFunction
from tests.utils.fixtures.mock_client_secret import MockClientSecret
from tests.utils.fixtures.mock_connect_application import MockConnectApplication
from tests.utils.list_resource import list_response_of
from tests.utils.syncify import syncify
from workos.connect import AsyncConnect, Connect


@pytest.mark.sync_and_async(Connect, AsyncConnect)
class TestConnect:
    @pytest.fixture(autouse=True)
    def setup(self, module_instance: Union[Connect, AsyncConnect]):
        self.http_client = module_instance._http_client
        self.connect = module_instance

    @pytest.fixture
    def mock_application(self):
        return MockConnectApplication("app_01ABC").dict()

    @pytest.fixture
    def mock_oauth_application(self):
        return MockConnectApplication("app_01ABC", application_type="oauth").dict()

    @pytest.fixture
    def mock_applications(self):
        application_list = [MockConnectApplication(id=str(i)).dict() for i in range(10)]
        return {
            "data": application_list,
            "list_metadata": {"before": None, "after": None},
            "object": "list",
        }

    @pytest.fixture
    def mock_applications_multiple_data_pages(self):
        applications_list = [
            MockConnectApplication(id=f"app_{i + 1}").dict() for i in range(40)
        ]
        return list_response_of(data=applications_list)

    @pytest.fixture
    def mock_client_secret(self):
        return MockClientSecret("cs_01ABC", include_secret=True).dict()

    @pytest.fixture
    def mock_client_secrets(self):
        return [MockClientSecret(id=f"cs_{i}").dict() for i in range(10)]

    # --- Application Tests ---

    def test_list_applications(
        self, mock_applications, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_applications, 200
        )

        response = syncify(self.connect.list_applications())

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith("/connect/applications")
        assert list(map(lambda x: x.dict(), response.data)) == mock_applications["data"]

    def test_list_applications_with_organization_id(
        self, mock_applications, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_applications, 200
        )

        syncify(self.connect.list_applications(organization_id="org_01ABC"))

        assert request_kwargs["method"] == "get"
        assert request_kwargs["params"]["organization_id"] == "org_01ABC"

    def test_get_application(
        self, mock_application, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_application, 200
        )

        application = syncify(self.connect.get_application(application_id="app_01ABC"))

        assert application.dict() == mock_application
        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith("/connect/applications/app_01ABC")

    def test_get_oauth_application(
        self, mock_oauth_application, capture_and_mock_http_client_request
    ):
        capture_and_mock_http_client_request(
            self.http_client, mock_oauth_application, 200
        )

        application = syncify(self.connect.get_application(application_id="app_01ABC"))

        assert application.dict() == mock_oauth_application
        assert application.application_type == "oauth"
        assert application.redirect_uris is not None
        assert application.uses_pkce is True
        assert application.is_first_party is True

    def test_create_m2m_application(
        self, mock_application, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_application, 201
        )

        application = syncify(
            self.connect.create_application(
                name="Test Application",
                application_type="m2m",
                is_first_party=True,
                organization_id="org_01ABC",
                scopes=["read", "write"],
            )
        )

        assert application.id == "app_01ABC"
        assert application.name == "Test Application"
        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith("/connect/applications")
        assert request_kwargs["json"]["name"] == "Test Application"
        assert request_kwargs["json"]["application_type"] == "m2m"
        assert request_kwargs["json"]["organization_id"] == "org_01ABC"

    def test_create_oauth_application(
        self, mock_oauth_application, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_oauth_application, 201
        )

        application = syncify(
            self.connect.create_application(
                name="Test Application",
                application_type="oauth",
                is_first_party=True,
                redirect_uris=[{"uri": "https://example.com/callback", "default": True}],
                uses_pkce=True,
            )
        )

        assert application.application_type == "oauth"
        assert request_kwargs["method"] == "post"
        assert request_kwargs["json"]["application_type"] == "oauth"
        assert request_kwargs["json"]["redirect_uris"] == [
            {"uri": "https://example.com/callback", "default": True}
        ]

    def test_update_application(
        self, mock_application, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_application, 200
        )

        syncify(
            self.connect.update_application(
                application_id="app_01ABC",
                name="Updated Name",
                scopes=["read"],
            )
        )

        assert request_kwargs["method"] == "put"
        assert request_kwargs["url"].endswith("/connect/applications/app_01ABC")
        assert request_kwargs["json"]["name"] == "Updated Name"
        assert request_kwargs["json"]["scopes"] == ["read"]

    def test_delete_application(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client,
            None,
            202,
            headers={"content-type": "text/plain; charset=utf-8"},
        )

        response = syncify(self.connect.delete_application(application_id="app_01ABC"))

        assert request_kwargs["url"].endswith("/connect/applications/app_01ABC")
        assert request_kwargs["method"] == "delete"
        assert response is None

    def test_list_applications_auto_pagination_for_single_page(
        self,
        mock_applications,
        test_auto_pagination: TestAutoPaginationFunction,
    ):
        test_auto_pagination(
            http_client=self.http_client,
            list_function=self.connect.list_applications,
            expected_all_page_data=mock_applications["data"],
        )

    def test_list_applications_auto_pagination_for_multiple_pages(
        self,
        mock_applications_multiple_data_pages,
        test_auto_pagination: TestAutoPaginationFunction,
    ):
        test_auto_pagination(
            http_client=self.http_client,
            list_function=self.connect.list_applications,
            expected_all_page_data=mock_applications_multiple_data_pages["data"],
        )

    # --- Client Secret Tests ---

    def test_create_client_secret(
        self, mock_client_secret, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_client_secret, 201
        )

        secret = syncify(self.connect.create_client_secret(application_id="app_01ABC"))

        assert secret.id == "cs_01ABC"
        assert secret.secret == "sk_test_secret_value_123"
        assert secret.secret_hint == "...abcd"
        assert request_kwargs["method"] == "post"
        assert request_kwargs["url"].endswith(
            "/connect/applications/app_01ABC/client_secrets"
        )
        assert request_kwargs["json"] == {}

    def test_list_client_secrets(
        self, mock_client_secrets, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client, mock_client_secrets, 200
        )

        response = syncify(self.connect.list_client_secrets(application_id="app_01ABC"))

        assert request_kwargs["method"] == "get"
        assert request_kwargs["url"].endswith(
            "/connect/applications/app_01ABC/client_secrets"
        )
        assert [secret.dict() for secret in response] == mock_client_secrets

    def test_delete_client_secret(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(
            self.http_client,
            None,
            202,
            headers={"content-type": "text/plain; charset=utf-8"},
        )

        response = syncify(
            self.connect.delete_client_secret(client_secret_id="cs_01ABC")
        )

        assert request_kwargs["url"].endswith("/connect/client_secrets/cs_01ABC")
        assert request_kwargs["method"] == "delete"
        assert response is None
