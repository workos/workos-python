import pytest

from workos.exceptions import (
    AuthenticationException, AuthorizationException, BadRequestException,
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
            mock_request_method('get', {}, status_code)

            with pytest.raises(exception):
                request_helper.request('bad_place')

    def test_request_exceptions_include_expected_request_data(
        self, mock_request_method
    ):
        request_helper = RequestHelper()

        request_id = 'request-123'
        response_message = 'stuff happened'

        for status_code, exception in STATUS_CODE_TO_EXCEPTION_MAPPING.items():
            mock_request_method(
                'get',
                {'message': response_message, },
                status_code,
                headers={'X-Request-ID': request_id}
            )

            try:
                request_helper.request('bad_place')
            except exception as ex:
                assert ex.message == response_message
                assert ex.request_id == request_id
            except Exception as ex:
                # This'll fail for sure here but... just using the nice error that'd come up
                assert ex.__class__ == exception

    def test_request_bad_body_raises_expected_exception_with_request_data(
        self, mock_request_method
    ):
        request_id = 'request-123'

        mock_request_method(
            'get',
            'this_isnt_json',
            200,
            headers={'X-Request-ID': request_id}
        )

        try:
            RequestHelper().request('bad_place')
        except ServerException as ex:
            assert ex.message == None
            assert ex.request_id == request_id
        except Exception as ex:
            # This'll fail for sure here but... just using the nice error that'd come up
            assert ex.__class__ == ServerException

    def test_request_includes_base_headers(self, capture_and_mock_requests):
        requests = capture_and_mock_requests()

        RequestHelper().request('ok_place')

        assert len(requests) == 1

        base_headers = set(BASE_HEADERS.items()) 
        headers = set(requests[0][1]['headers'].items())

        assert base_headers.issubset(headers)