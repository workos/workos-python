from platform import python_version

import httpx
import pytest
from unittest.mock import AsyncMock

from workos.utils.http_client import AsyncHTTPClient


class TestAsyncHTTPClient(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        response = httpx.Response(200, json={"message": "Success!"})

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"message": "Success!"})

        self.http_client = AsyncHTTPClient(
            base_url="https://api.workos.test",
            version="test",
            transport=httpx.MockTransport(handler),
        )

        self.http_client._client.request = AsyncMock(
            return_value=response,
        )

    @pytest.mark.parametrize(
        "method,status_code,expected_response",
        [
            ("GET", 200, {"message": "Success!"}),
            ("DELETE", 204, None),
            ("DELETE", 202, None),
        ],
    )
    @pytest.mark.asyncio
    async def test_request_without_body(
        self, method: str, status_code: int, expected_response: dict
    ):
        self.http_client._client.request = AsyncMock(
            return_value=httpx.Response(
                status_code=status_code, json=expected_response
            ),
        )

        response = await self.http_client.request(
            "events",
            method=method,
            params={"test_param": "test_value"},
            token="test",
        )

        self.http_client._client.request.assert_called_with(
            method=method,
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
            timeout=25,
        )

        assert response == expected_response

    @pytest.mark.parametrize(
        "method,status_code,expected_response",
        [
            ("POST", 201, {"message": "Success!"}),
            ("PUT", 200, {"message": "Success!"}),
            ("PATCH", 200, {"message": "Success!"}),
        ],
    )
    @pytest.mark.asyncio
    async def test_request_with_body(
        self, method: str, status_code: int, expected_response: dict
    ):
        self.http_client._client.request = AsyncMock(
            return_value=httpx.Response(
                status_code=status_code, json=expected_response
            ),
        )

        response = await self.http_client.request(
            "events", method=method, params={"test_param": "test_value"}, token="test"
        )

        self.http_client._client.request.assert_called_with(
            method=method,
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
            timeout=25,
        )

        assert response == expected_response
