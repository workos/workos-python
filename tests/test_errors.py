# @oagen-ignore-file
"""How API errors read when printed or logged."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

import httpx2
import pytest

from workos import HTTPResponse
from workos._base_client import _BaseWorkOSClient
from workos._errors import (
    APIError,
    MfaChallengeError,
    NotFoundError,
)
from workos.session import _map_refresh_exception_to_reason


def raised(
    status_code: int,
    body: Any = None,
    headers: Optional[Dict[str, str]] = None,
) -> APIError:
    content = (
        body
        if isinstance(body, bytes)
        else b""
        if body is None
        else json.dumps(body).encode()
    )
    response = HTTPResponse(
        status_code=status_code,
        headers=httpx2.Headers(headers or {}),
        content=content,
        request_method="GET",
        request_url="https://api.workos.com/t",
    )
    with pytest.raises(APIError) as exc_info:
        _BaseWorkOSClient._raise_error(response)
    return exc_info.value


def test_an_empty_body_reads_as_the_status() -> None:
    error = raised(500)
    assert str(error) == "HTTP 500: Internal Server Error"
    assert error.message == ""
    assert error.request_id == ""


def test_message_and_request_id() -> None:
    error = raised(401, {"message": "Invalid API key"}, {"x-request-id": "req_123"})
    assert str(error) == "HTTP 401: Invalid API key (request_id=req_123)"


def test_code_is_included() -> None:
    error = raised(
        404,
        {"message": "Organization not found", "code": "entity_not_found"},
        {"x-request-id": "req_123"},
    )
    assert isinstance(error, NotFoundError)
    assert (
        str(error)
        == "HTTP 404: Organization not found (code=entity_not_found, request_id=req_123)"
    )


def test_an_oauth_style_body_reads_as_its_description_and_keeps_its_error() -> None:
    error = raised(
        400, {"error": "invalid_grant", "error_description": "The code has expired."}
    )
    assert str(error) == "HTTP 400: The code has expired. (error=invalid_grant)"


def test_an_oauth_style_body_with_only_an_error() -> None:
    assert str(raised(400, {"error": "invalid_grant"})) == "HTTP 400: invalid_grant"


def test_a_json_body_without_a_message_reads_as_the_status() -> None:
    assert (
        str(raised(409, {"errors": [{"field": "name"}]}))
        == "HTTP 409: Conflict (errors=[{'field': 'name'}])"
    )


def test_a_null_message_reads_as_the_status() -> None:
    assert str(raised(400, {"message": None})) == "HTTP 400: Bad Request"


def test_param_and_errors_are_included() -> None:
    error = raised(
        422,
        {
            "message": "Validation failed",
            "code": "invalid_request_parameters",
            "param": "domains",
            "errors": [{"code": "invalid_domain", "field": "domains"}],
        },
    )
    assert str(error) == (
        "HTTP 422: Validation failed (code=invalid_request_parameters, "
        "param=domains, errors=[{'code': 'invalid_domain', 'field': 'domains'}])"
    )


def test_a_refresh_failure_reason_keeps_the_oauth_error() -> None:
    error = raised(
        400,
        {"error": "invalid_grant", "error_description": "Session has already ended."},
        {"x-request-id": "req_123"},
    )
    assert _map_refresh_exception_to_reason(error) == (
        "HTTP 400: Session has already ended. (error=invalid_grant, request_id=req_123)"
    )


def test_a_plain_text_body_is_the_message() -> None:
    assert str(raised(502, b"upstream unavailable")) == "HTTP 502: upstream unavailable"


def test_an_unknown_status_without_a_message() -> None:
    assert str(raised(599)) == "HTTP 599: The request could not be completed"


def test_response_details_stay_out_of_the_string() -> None:
    error = raised(
        403,
        {
            "message": "MFA challenge required",
            "code": "mfa_challenge",
            "pending_authentication_token": "secret_token",
            "user": {"email": "person@example.com"},
        },
    )
    assert isinstance(error, MfaChallengeError)
    assert str(error) == "HTTP 403: MFA challenge required (code=mfa_challenge)"
    assert error.pending_authentication_token == "secret_token"
    assert error.response_json is not None and "user" in error.response_json


@pytest.mark.parametrize(
    "error, expected",
    [
        (APIError("Something broke"), "Something broke"),
        (
            APIError("Gone", status_code=410, code="expired"),
            "HTTP 410: Gone (code=expired)",
        ),
        (APIError(), "The request could not be completed"),
    ],
)
def test_errors_constructed_directly(error: APIError, expected: str) -> None:
    assert str(error) == expected
