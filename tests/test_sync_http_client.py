from platform import python_version

import httpx
import pytest
from unittest.mock import MagicMock

from workos.exceptions import (
    AuthenticationException,
    AuthorizationException,
    BadRequestException,
    BaseRequestException,
    ConflictException,
    ServerException,
)
from workos.utils.http_client import SyncHTTPClient


STATUS_CODE_TO_EXCEPTION_MAPPING = [
    (400, BadRequestException),
    (401, AuthenticationException),
    (403, AuthorizationException),
    (500, ServerException),
]


class TestSyncHTTPClient(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        response = httpx.Response(200, json={"message": "Success!"})

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"message": "Success!"})

        self.http_client = SyncHTTPClient(
            api_key="sk_test",
            base_url="https://api.workos.test/",
            client_id="client_b27needthisforssotemxo",
            version="test",
            transport=httpx.MockTransport(handler),
        )

        self.http_client._client.request = MagicMock(
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
    def test_request_without_body(
        self, method: str, status_code: int, expected_response: dict
    ):
        self.http_client._client.request = MagicMock(
            return_value=httpx.Response(
                status_code=status_code, json=expected_response
            ),
        )

        response = self.http_client.request(
            "events",
            method=method,
            params={"test_param": "test_value"},
        )

        self.http_client._client.request.assert_called_with(
            method=method,
            url="https://api.workos.test/events",
            headers=httpx.Headers(
                {
                    "accept": "application/json",
                    "content-type": "application/json",
                    "user-agent": f"WorkOS Python/{python_version()} Python SDK/test",
                    "authorization": "Bearer sk_test",
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
    def test_request_with_body(
        self, method: str, status_code: int, expected_response: dict
    ):
        self.http_client._client.request = MagicMock(
            return_value=httpx.Response(
                status_code=status_code, json=expected_response
            ),
        )

        response = self.http_client.request(
            "events", method=method, json={"test_param": "test_value"}
        )

        self.http_client._client.request.assert_called_with(
            method=method,
            url="https://api.workos.test/events",
            headers=httpx.Headers(
                {
                    "accept": "application/json",
                    "content-type": "application/json",
                    "user-agent": f"WorkOS Python/{python_version()} Python SDK/test",
                    "authorization": "Bearer sk_test",
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
    def test_request_with_body_and_query_parameters(
        self, method: str, status_code: int, expected_response: dict
    ):
        self.http_client._client.request = MagicMock(
            return_value=httpx.Response(
                status_code=status_code, json=expected_response
            ),
        )

        response = self.http_client.request(
            "events",
            method=method,
            params={"test_param": "test_param_value"},
            json={"test_json": "test_json_value"},
        )

        self.http_client._client.request.assert_called_with(
            method=method,
            url="https://api.workos.test/events",
            headers=httpx.Headers(
                {
                    "accept": "application/json",
                    "content-type": "application/json",
                    "user-agent": f"WorkOS Python/{python_version()} Python SDK/test",
                    "authorization": "Bearer sk_test",
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
    def test_request_raises_expected_exception_for_status_code(
        self, status_code: int, expected_exception: BaseRequestException
    ):
        self.http_client._client.request = MagicMock(
            return_value=httpx.Response(status_code=status_code),
        )

        with pytest.raises(expected_exception):  # type: ignore
            self.http_client.request("bad_place")

    @pytest.mark.parametrize(
        "status_code,expected_exception",
        STATUS_CODE_TO_EXCEPTION_MAPPING,
    )
    def test_request_exceptions_include_expected_request_data(
        self, status_code: int, expected_exception: BaseRequestException
    ):
        request_id = "request-123"
        response_message = "stuff happened"

        self.http_client._client.request = MagicMock(
            return_value=httpx.Response(
                status_code=status_code,
                json={"message": response_message},
                headers={"X-Request-ID": request_id},
            ),
        )

        try:
            self.http_client.request("bad_place")
        except expected_exception as ex:  # type: ignore
            assert ex.message == response_message
            assert ex.request_id == request_id
            assert ex.__class__ == expected_exception

    def test_bad_request_exceptions_include_request_data(self):
        request_id = "request-123"
        error = "example_error"
        error_description = "Example error description"

        self.http_client._client.request = MagicMock(
            return_value=httpx.Response(
                status_code=400,
                json={
                    "error": error,
                    "error_description": error_description,
                    "foo": "bar",
                },
                headers={"X-Request-ID": request_id},
            ),
        )

        try:
            self.http_client.request("bad_place")
        except BadRequestException as ex:
            assert (
                str(ex)
                == "(message=No message, request_id=request-123, error=example_error, error_description=Example error description, foo=bar)"
            )
            assert ex.__class__ == BadRequestException

    def test_request_bad_body_raises_expected_exception_with_request_data(self):
        request_id = "request-123"

        self.http_client._client.request = MagicMock(
            return_value=httpx.Response(
                status_code=200,
                content="this_isnt_json",
                headers={"X-Request-ID": request_id},
            ),
        )

        try:
            self.http_client.request("bad_place")
        except ServerException as ex:
            assert ex.message == None
            assert ex.request_id == request_id
            assert ex.__class__ == ServerException

    def test_conflict_exception(self):
        request_id = "request-123"

        self.http_client._client.request = MagicMock(
            return_value=httpx.Response(
                status_code=409,
                headers={"X-Request-ID": request_id},
            ),
        )

        try:
            self.http_client.request("bad_place")
        except ConflictException as ex:
            assert str(ex) == "(message=No message, request_id=request-123)"
            assert ex.__class__ == ConflictException

    def test_request_includes_base_headers(self, capture_and_mock_http_client_request):
        request_kwargs = capture_and_mock_http_client_request(self.http_client, {}, 200)

        self.http_client.request("ok_place")

        default_headers = set(
            (header[0].lower(), header[1])
            for header in self.http_client.default_headers.items()
        )
        headers = set(request_kwargs["headers"].items())

        assert default_headers.issubset(headers)

    def test_request_parses_json_when_content_type_present(self):
        self.http_client._client.request = MagicMock(
            return_value=httpx.Response(
                status_code=200,
                json={"foo": "bar"},
                headers={"content-type": "application/json"},
            ),
        )

        assert self.http_client.request("ok_place") == {"foo": "bar"}

    def test_request_parses_json_when_encoding_in_content_type(self):
        self.http_client._client.request = MagicMock(
            return_value=httpx.Response(
                status_code=200,
                json={"foo": "bar"},
                headers={"content-type": "application/json; charset=utf8"},
            ),
        )

        assert self.http_client.request("ok_place") == {"foo": "bar"}

    def test_request_removes_none_parameter_values(
        self, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(self.http_client, {}, 200)

        self.http_client.request(
            path="/test",
            method="get",
            params={"organization_id": None, "test": "value"},
        )
        assert request_kwargs["params"] == {"test": "value"}

    def test_request_removes_none_json_values(
        self, capture_and_mock_http_client_request
    ):
        request_kwargs = capture_and_mock_http_client_request(self.http_client, {}, 200)

        self.http_client.request(
            path="/test",
            method="post",
            json={"organization_id": None, "test": "value"},
        )
        assert request_kwargs["json"] == {"test": "value"}
