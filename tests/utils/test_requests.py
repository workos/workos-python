import pytest

from workos.exceptions import (
    AuthenticationException,
    AuthorizationException,
    BadRequestException,
    ServerException,
)
from workos.utils.request import RequestHelper, BASE_HEADERS

STATUS_CODE_TO_EXCEPTION_MAPPING = {
    400: BadRequestException,
    401: AuthenticationException,
    403: AuthorizationException,
    500: ServerException,
}


class TestRequestHelper(object):
    def test_set_base_api_url(self):
        pass

    def test_request_raises_expected_exception_for_status_code(
        self, mock_request_method
    ):
        request_helper = RequestHelper()

        for status_code, exception in STATUS_CODE_TO_EXCEPTION_MAPPING.items():
            mock_request_method("get", {}, status_code)

            with pytest.raises(exception):
                request_helper.request("bad_place")

    def test_request_exceptions_include_expected_request_data(
        self, mock_request_method
    ):
        request_helper = RequestHelper()

        request_id = "request-123"
        response_message = "stuff happened"

        for status_code, exception in STATUS_CODE_TO_EXCEPTION_MAPPING.items():
            mock_request_method(
                "get",
                {"message": response_message},
                status_code,
                headers={"X-Request-ID": request_id},
            )

            try:
                request_helper.request("bad_place")
            except exception as ex:
                assert ex.message == response_message
                assert ex.request_id == request_id
            except Exception as ex:
                # This'll fail for sure here but... just using the nice error that'd come up
                assert ex.__class__ == exception

    def test_bad_request_exceptions_include_expected_request_data(
        self, mock_request_method
    ):
        request_helper = RequestHelper()

        request_id = "request-123"
        error = "example_error"
        error_description = "Example error description"

        mock_request_method(
            "get",
            {"error": error, "error_description": error_description},
            400,
            headers={"X-Request-ID": request_id},
        )

        try:
            request_helper.request("bad_place")
        except ServerException as ex:
            assert ex.request_id == request_id
            assert ex.error == error
            assert ex.error_description == error_description
        except Exception as ex:
            # This'll fail for sure here but... just using the nice error that'd come up
            assert ex.__class__ == BadRequestException

    def test_bad_request_exceptions_exclude_expected_request_data(
        self, mock_request_method
    ):
        request_helper = RequestHelper()

        request_id = "request-123"

        mock_request_method(
            "get", {"foo": "bar"}, 400, headers={"X-Request-ID": request_id},
        )

        try:
            request_helper.request("bad_place")
        except ServerException as ex:
            assert ex.request_id == request_id
            assert ex.error == None
            assert ex.error_description == None
        except Exception as ex:
            # This'll fail for sure here but... just using the nice error that'd come up
            assert ex.__class__ == BadRequestException

    def test_request_bad_body_raises_expected_exception_with_request_data(
        self, mock_request_method
    ):
        request_id = "request-123"

        mock_request_method(
            "get", "this_isnt_json", 200, headers={"X-Request-ID": request_id}
        )

        try:
            RequestHelper().request("bad_place")
        except ServerException as ex:
            assert ex.message == None
            assert ex.request_id == request_id
        except Exception as ex:
            # This'll fail for sure here but... just using the nice error that'd come up
            assert ex.__class__ == ServerException

    def test_request_includes_base_headers(self, capture_and_mock_request):
        request_args, request_kwargs = capture_and_mock_request("get", {}, 200)

        RequestHelper().request("ok_place")

        base_headers = set(BASE_HEADERS.items())
        headers = set(request_kwargs["headers"].items())

        assert base_headers.issubset(headers)

    def test_request_parses_json_when_content_type_present(self, mock_request_method):
        mock_request_method(
            "get", {"foo": "bar"}, 200, headers={"content-type": "application/json"}
        )

        assert RequestHelper().request("ok_place") == {"foo": "bar"}

    def test_request_parses_json_when_encoding_in_content_type(
        self, mock_request_method
    ):
        mock_request_method(
            "get",
            {"foo": "bar"},
            200,
            headers={"content-type": "application/json; charset=utf8"},
        )

        assert RequestHelper().request("ok_place") == {"foo": "bar"}
