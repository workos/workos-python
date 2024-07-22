import httpx
import pytest
from unittest.mock import AsyncMock

from workos.utils.http_client import AsyncHTTPClient


class TestAsyncHTTPClient(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"message": "Success!"})

        self.http_client = AsyncHTTPClient(
            base_url="https://api.workos.test",
            version="test",
            transport=httpx.MockTransport(handler),
        )

        self.http_client._client.request = AsyncMock(
            return_value=httpx.Response(200, json={"message": "Success!"}),
        )

    @pytest.mark.asyncio
    async def test_get_request(self):
        response = await self.http_client.request(
            "events", method="GET", params={"test_param": "test_value"}, token="test"
        )

        self.http_client._client.request.assert_called_with(
            method="GET",
            url="https://api.workos.test/events",
            headers=httpx.Headers(
                {
                    "accept": "application/json",
                    "content-type": "application/json",
                    "user-agent": "WorkOS Python/3.8.18 Python SDK/test",
                    "authorization": "Bearer test",
                }
            ),
            params={"test_param": "test_value"},
            timeout=None,
        )

        assert response == {"message": "Success!"}

    @pytest.mark.asyncio
    async def test_delete_request(self):
        response = await self.http_client.request(
            "events", method="DELETE", token="test"
        )

        self.http_client._client.request.assert_called_with(
            method="DELETE",
            url="https://api.workos.test/events",
            headers=httpx.Headers(
                {
                    "accept": "application/json",
                    "content-type": "application/json",
                    "user-agent": "WorkOS Python/3.8.18 Python SDK/test",
                    "authorization": "Bearer test",
                }
            ),
            params=None,
            timeout=None,
        )

        assert response == {"message": "Success!"}

    @pytest.mark.asyncio
    async def test_post_request(self):
        response = await self.http_client.request(
            "events", method="POST", params={"test_param": "test_value"}, token="test"
        )

        self.http_client._client.request.assert_called_with(
            method="POST",
            url="https://api.workos.test/events",
            headers=httpx.Headers(
                {
                    "accept": "application/json",
                    "content-type": "application/json",
                    "user-agent": "WorkOS Python/3.8.18 Python SDK/test",
                    "authorization": "Bearer test",
                }
            ),
            json={"test_param": "test_value"},
            timeout=None,
        )

        assert response == {"message": "Success!"}

    @pytest.mark.asyncio
    async def test_put_request(self):
        response = await self.http_client.request(
            "events", method="PUT", params={"test_param": "test_value"}, token="test"
        )

        self.http_client._client.request.assert_called_with(
            method="PUT",
            url="https://api.workos.test/events",
            headers=httpx.Headers(
                {
                    "accept": "application/json",
                    "content-type": "application/json",
                    "user-agent": "WorkOS Python/3.8.18 Python SDK/test",
                    "authorization": "Bearer test",
                }
            ),
            json={"test_param": "test_value"},
            timeout=None,
        )

        assert response == {"message": "Success!"}

    @pytest.mark.asyncio
    async def test_patch_request(self):
        response = await self.http_client.request(
            "events", method="PATCH", params={"test_param": "test_value"}, token="test"
        )

        self.http_client._client.request.assert_called_with(
            method="PATCH",
            url="https://api.workos.test/events",
            headers=httpx.Headers(
                {
                    "accept": "application/json",
                    "content-type": "application/json",
                    "user-agent": "WorkOS Python/3.8.18 Python SDK/test",
                    "authorization": "Bearer test",
                }
            ),
            json={"test_param": "test_value"},
            timeout=None,
        )

        assert response == {"message": "Success!"}
