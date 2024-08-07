from platform import python_version

import httpx
import pytest
from unittest.mock import AsyncMock

from tests.test_sync_http_client import STATUS_CODE_TO_EXCEPTION_MAPPING
from workos.exceptions import BadRequestException, BaseRequestException, ServerException
from workos.utils.http_client import AsyncHTTPClient


@pytest.mark.asyncio
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
    async def test_request_with_body(
        self, method: str, status_code: int, expected_response: dict
    ):
        self.http_client._client.request = AsyncMock(
            return_value=httpx.Response(
                status_code=status_code, json=expected_response
            ),
        )

        response = await self.http_client.request(
            "events", method=method, json={"test_param": "test_value"}, token="test"
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
            params=None,
            json={"test_param": "test_value"},
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
    async def test_request_with_body_and_query_parameters(
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
            params={"test_param": "test_param_value"},
            json={"test_json": "test_json_value"},
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
            params={"test_param": "test_param_value"},
            json={"test_json": "test_json_value"},
            timeout=25,
        )

        assert response == expected_response

    @pytest.mark.parametrize(
        "status_code,expected_exception",
        STATUS_CODE_TO_EXCEPTION_MAPPING,
    )
    async def test_request_raises_expected_exception_for_status_code(
        self, status_code: int, expected_exception: BaseRequestException
    ):
        self.http_client._client.request = AsyncMock(
            return_value=httpx.Response(status_code=status_code),
        )

        with pytest.raises(expected_exception):  # type: ignore
            await self.http_client.request("bad_place")

    @pytest.mark.parametrize(
        "status_code,expected_exception",
        STATUS_CODE_TO_EXCEPTION_MAPPING,
    )
    async def test_request_exceptions_include_expected_request_data(
        self, status_code: int, expected_exception: BaseRequestException
    ):
        request_id = "request-123"
        response_message = "stuff happened"

        self.http_client._client.request = AsyncMock(
            return_value=httpx.Response(
                status_code=status_code,
                json={"message": response_message},
                headers={"X-Request-ID": request_id},
            ),
        )

        try:
            await self.http_client.request("bad_place")
        except expected_exception as ex:  # type: ignore
            assert ex.message == response_message
            assert ex.request_id == request_id
        except Exception as ex:
            # This'll fail for sure here but... just using the nice error that'd come up
            assert ex.__class__ == expected_exception

    async def test_bad_request_exceptions_include_expected_request_data(self):
        request_id = "request-123"
        error = "example_error"
        error_description = "Example error description"

        self.http_client._client.request = AsyncMock(
            return_value=httpx.Response(
                status_code=400,
                json={"error": error, "error_description": error_description},
                headers={"X-Request-ID": request_id},
            ),
        )

        try:
            await self.http_client.request("bad_place")
        except BadRequestException as ex:
            assert (
                str(ex)
                == "(message=No message, request_id=request-123, error=example_error, error_description=Example error description)"
            )
        except Exception as ex:
            assert ex.__class__ == BadRequestException

    async def test_bad_request_exceptions_exclude_expected_request_data(self):
        request_id = "request-123"

        self.http_client._client.request = AsyncMock(
            return_value=httpx.Response(
                status_code=400,
                json={"foo": "bar"},
                headers={"X-Request-ID": request_id},
            ),
        )

        try:
            await self.http_client.request("bad_place")
        except BadRequestException as ex:
            assert str(ex) == "(message=No message, request_id=request-123)"
        except Exception as ex:
            assert ex.__class__ == BadRequestException

    async def test_request_bad_body_raises_expected_exception_with_request_data(self):
        request_id = "request-123"

        self.http_client._client.request = AsyncMock(
            return_value=httpx.Response(
                status_code=200,
                content="this_isnt_json",
                headers={"X-Request-ID": request_id},
            ),
        )

        try:
            await self.http_client.request("bad_place")
        except ServerException as ex:
            assert ex.message == None
            assert ex.request_id == request_id
        except Exception as ex:
            # This'll fail for sure here but... just using the nice error that'd come up
            assert ex.__class__ == ServerException

    async def test_request_includes_base_headers(
        self, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(self.http_client, {}, 200)

        await self.http_client.request("ok_place")

        default_headers = set(
            (header[0].lower(), header[1])
            for header in self.http_client.default_headers.items()
        )
        headers = set(request_kwargs["headers"].items())

        assert default_headers.issubset(headers)

    async def test_request_parses_json_when_content_type_present(self):
        self.http_client._client.request = AsyncMock(
            return_value=httpx.Response(
                status_code=200,
                json={"foo": "bar"},
                headers={"content-type": "application/json"},
            ),
        )

        assert await self.http_client.request("ok_place") == {"foo": "bar"}

    async def test_request_parses_json_when_encoding_in_content_type(self):
        self.http_client._client.request = AsyncMock(
            return_value=httpx.Response(
                status_code=200,
                json={"foo": "bar"},
                headers={"content-type": "application/json; charset=utf8"},
            ),
        )

        assert await self.http_client.request("ok_place") == {"foo": "bar"}
