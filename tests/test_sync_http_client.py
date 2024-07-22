from platform import python_version

import httpx
import pytest
from unittest.mock import MagicMock

from workos.utils.http_client import SyncHTTPClient


class TestSyncHTTPClient(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"message": "Success!"})

        self.http_client = SyncHTTPClient(
            base_url="https://api.workos.test",
            version="test",
            transport=httpx.MockTransport(handler),
        )

        self.http_client._client.request = MagicMock(
            return_value=httpx.Response(200, json={"message": "Success!"}),
        )

    def test_get_request(self):
        response = self.http_client.request(
            "events", method="GET", params={"test_param": "test_value"}, token="test"
        )

        self.http_client._client.request.assert_called_with(
            method="GET",
            url="https://api.workos.test/events",
            headers=httpx.Headers(
                {
                    "accept": "application/json",
                    "content-type": "application/json",
                    "user-agent": f"WorkOS Python/{python_version()} Python SDK/test",
                    "authorization": "Bearer test",
                }
            ),
            params={"test_param": "test_value"},
            timeout=None,
        )

        assert response == {"message": "Success!"}

    def test_delete_request(self):
        response = self.http_client.request("events", method="DELETE", token="test")

        self.http_client._client.request.assert_called_with(
            method="DELETE",
            url="https://api.workos.test/events",
            headers=httpx.Headers(
                {
                    "accept": "application/json",
                    "content-type": "application/json",
                    "user-agent": f"WorkOS Python/{python_version()} Python SDK/test",
                    "authorization": "Bearer test",
                }
            ),
            params=None,
            timeout=None,
        )

        assert response == {"message": "Success!"}

    def test_post_request(self):
        response = self.http_client.request(
            "events", method="POST", params={"test_param": "test_value"}, token="test"
        )

        self.http_client._client.request.assert_called_with(
            method="POST",
            url="https://api.workos.test/events",
            headers=httpx.Headers(
                {
                    "accept": "application/json",
                    "content-type": "application/json",
                    "user-agent": f"WorkOS Python/{python_version()} Python SDK/test",
                    "authorization": "Bearer test",
                }
            ),
            json={"test_param": "test_value"},
            timeout=None,
        )

        assert response == {"message": "Success!"}

    def test_put_request(self):
        response = self.http_client.request(
            "events", method="PUT", params={"test_param": "test_value"}, token="test"
        )

        self.http_client._client.request.assert_called_with(
            method="PUT",
            url="https://api.workos.test/events",
            headers=httpx.Headers(
                {
                    "accept": "application/json",
                    "content-type": "application/json",
                    "user-agent": f"WorkOS Python/{python_version()} Python SDK/test",
                    "authorization": "Bearer test",
                }
            ),
            json={"test_param": "test_value"},
            timeout=None,
        )

        assert response == {"message": "Success!"}

    def test_patch_request(self):
        response = self.http_client.request(
            "events", method="PATCH", params={"test_param": "test_value"}, token="test"
        )

        self.http_client._client.request.assert_called_with(
            method="PATCH",
            url="https://api.workos.test/events",
            headers=httpx.Headers(
                {
                    "accept": "application/json",
                    "content-type": "application/json",
                    "user-agent": f"WorkOS Python/{python_version()} Python SDK/test",
                    "authorization": "Bearer test",
                }
            ),
            json={"test_param": "test_value"},
            timeout=None,
        )

        assert response == {"message": "Success!"}
