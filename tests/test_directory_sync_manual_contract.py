# @oagen-ignore-file

import pytest

from workos import (
    ConflictError,
    RateLimitExceededError,
    ServerError,
    UnprocessableEntityError,
)
from workos.directory_sync.models import DirectorySyncResponse


def test_manual_sync_accepts_202(workos, httpx_mock):
    httpx_mock.add_response(status_code=202, json={"status": "queued"})

    result = workos.directory_sync.sync_directory("directory_123")

    assert isinstance(result, DirectorySyncResponse)
    assert result.status == "queued"
    sent = httpx_mock.get_request()
    assert sent.method == "POST"
    assert sent.url.path == "/directories/directory_123/sync"
    assert sent.content == b""


@pytest.mark.asyncio
async def test_async_manual_sync_accepts_202(async_workos, httpx_mock):
    httpx_mock.add_response(status_code=202, json={"status": "queued"})

    result = await async_workos.directory_sync.sync_directory("directory_123")

    assert isinstance(result, DirectorySyncResponse)
    assert result.status == "queued"
    assert httpx_mock.get_request().url.path == "/directories/directory_123/sync"


def test_manual_sync_preserves_rate_limit_details(workos, httpx_mock):
    body = {
        "code": "directory_sync_rate_limited",
        "message": "Wait before requesting another sync.",
        "retry_after_seconds": 120,
    }
    httpx_mock.add_response(status_code=429, json=body, headers={"Retry-After": "120"})

    with pytest.raises(RateLimitExceededError) as raised:
        workos.directory_sync.sync_directory(
            "directory_123", request_options={"max_retries": 0}
        )

    assert raised.value.status_code == 429
    assert raised.value.code == "directory_sync_rate_limited"
    assert raised.value.response_json is not None
    assert raised.value.response_json["retry_after_seconds"] == 120
    assert raised.value.response is not None
    assert raised.value.response.headers["Retry-After"] == "120"
    assert len(httpx_mock.get_requests()) == 1


@pytest.mark.parametrize(
    ("status", "code", "error"),
    [
        (409, "directory_sync_in_progress", ConflictError),
        (422, "directory_sync_unsupported", UnprocessableEntityError),
        (503, "directory_sync_disabled", ServerError),
    ],
)
def test_manual_sync_does_not_report_errors_as_queued(
    workos, httpx_mock, status, code, error
):
    httpx_mock.add_response(
        status_code=status, json={"code": code, "message": "Not queued."}
    )

    with pytest.raises(error) as raised:
        workos.directory_sync.sync_directory(
            "directory_123", request_options={"max_retries": 0}
        )

    assert raised.value.status_code == status
    assert raised.value.code == code
    assert len(httpx_mock.get_requests()) == 1
