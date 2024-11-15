import pytest

from workos.widgets import Widgets


class TestWidgets(object):
    @pytest.fixture(autouse=True)
    def setup(self, sync_http_client_for_test):
        self.http_client = sync_http_client_for_test
        self.widgets = Widgets(http_client=self.http_client)

    @pytest.fixture
    def mock_widget_token(self):
        return {"token": "abc123456"}

    def test_get_token(self, mock_widget_token, mock_http_client_with_response):
        mock_http_client_with_response(self.http_client, mock_widget_token, 201)

        response = self.widgets.get_token(
            organization_id="org_01EHQMYV6MBK39QC5PZXHY59C3",
            user_id="user_01EHQMYV6MBK39QC5PZXHY59C3",
            scopes=["widgets:users-table:manage"],
        )

        assert response.token == "abc123456"
