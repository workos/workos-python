# @oagen-ignore-file
"""Fixtures for the feature flags runtime client tests."""

from __future__ import annotations

from typing import Any, AsyncIterator, Callable, Iterator, List

import pytest
import pytest_asyncio

from workos import AsyncWorkOSClient, WorkOSClient
from workos.feature_flags.runtime import (
    AsyncFeatureFlagsRuntimeClient,
    FeatureFlagsRuntimeClient,
    _policy,
)

from tests.feature_flags_runtime.helpers import (
    API_KEY,
    BASE_URL,
    AsyncBackend,
    FlagServer,
    SyncBackend,
)


@pytest.fixture
def server() -> FlagServer:
    return FlagServer()


@pytest.fixture
def client(server: FlagServer) -> Iterator[WorkOSClient]:
    workos = WorkOSClient(
        api_key=API_KEY, base_url=BASE_URL, http_client=SyncBackend(server)
    )
    yield workos
    workos.close()


@pytest.fixture
def async_client(server: FlagServer) -> AsyncWorkOSClient:
    return AsyncWorkOSClient(
        api_key=API_KEY, base_url=BASE_URL, http_client=AsyncBackend(server)
    )


@pytest.fixture
def fast_polling(monkeypatch: pytest.MonkeyPatch) -> List[int]:
    """Poll every 10 ms and retry inside a refresh after 5 ms.

    Returns the failure counts the poller computed delays for, so tests can
    assert on backoff without waiting for it.
    """
    failures: List[int] = []

    def next_delay(interval: float, count: int, max_retry_delay: float) -> float:
        failures.append(count)
        return 0.01

    monkeypatch.setattr(_policy, "next_delay", next_delay)
    monkeypatch.setattr(_policy, "_ATTEMPT_RETRY_BASE", 0.005)
    return failures


@pytest.fixture
def make_runtime(
    client: WorkOSClient,
) -> Iterator[Callable[..., FeatureFlagsRuntimeClient]]:
    """Create runtime clients that are always closed at teardown."""
    created: List[FeatureFlagsRuntimeClient] = []

    def make(**options: Any) -> FeatureFlagsRuntimeClient:
        runtime = client.create_feature_flags_runtime_client(**options)
        created.append(runtime)
        return runtime

    yield make
    for runtime in created:
        runtime.close()


@pytest_asyncio.fixture
async def make_async_runtime(
    async_client: AsyncWorkOSClient,
) -> AsyncIterator[Callable[..., AsyncFeatureFlagsRuntimeClient]]:
    """Create async runtime clients that are always closed at teardown."""
    created: List[AsyncFeatureFlagsRuntimeClient] = []

    def make(**options: Any) -> AsyncFeatureFlagsRuntimeClient:
        runtime = async_client.create_feature_flags_runtime_client(**options)
        created.append(runtime)
        return runtime

    yield make
    for runtime in created:
        await runtime.close()
