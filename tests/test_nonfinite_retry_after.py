# @oagen-ignore-file

import math

import pytest

from workos import _base_client


@pytest.mark.parametrize("retry_after", ["NaN", "Infinity", "1e309"])
def test_nonfinite_retry_after_uses_backoff(
    workos, httpx_mock, monkeypatch, retry_after
):
    delays = []

    def sleep(delay):
        assert math.isfinite(delay)
        delays.append(delay)

    monkeypatch.setattr(_base_client.time, "sleep", sleep)
    httpx_mock.add_response(status_code=503, headers={"Retry-After": retry_after})
    httpx_mock.add_response(json={"ok": True})
    assert workos.request("GET", ("test",)) == {"ok": True}
    assert len(delays) == 1
    assert 0.5 <= delays[0] <= 1.5


@pytest.mark.asyncio
@pytest.mark.parametrize("retry_after", ["NaN", "Infinity", "1e309"])
async def test_async_nonfinite_retry_after_uses_backoff(
    async_workos, httpx_mock, monkeypatch, retry_after
):
    delays = []

    async def sleep(delay):
        assert math.isfinite(delay)
        delays.append(delay)

    monkeypatch.setattr(_base_client.asyncio, "sleep", sleep)
    httpx_mock.add_response(status_code=503, headers={"Retry-After": retry_after})
    httpx_mock.add_response(json={"ok": True})
    assert await async_workos.request("GET", ("test",)) == {"ok": True}
    assert len(delays) == 1
    assert 0.5 <= delays[0] <= 1.5
