# @oagen-ignore-file
# This file is hand-maintained. Factory methods that WorkOSClient and
# AsyncWorkOSClient expose as `create_feature_flags_runtime_client`.
# pyright: strict

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Optional

from . import _policy
from ._async import (
    AsyncFeatureFlagsRuntimeClient,
    ChangeListener,
    ErrorListener,
    StatusListener,
)
from ._configuration import FeatureFlagsConfiguration
from ._context import LoggerLike
from ._sync import FeatureFlagsRuntimeClient
from ._types import FlagsChangedEvent, RuntimeStatus

if TYPE_CHECKING:
    from ..._base_client import AsyncWorkOSClient, WorkOSClient


def create_feature_flags_runtime_client(
    self: WorkOSClient,
    *,
    polling_interval: float = _policy.DEFAULT_POLLING_INTERVAL,
    request_timeout: float = _policy.DEFAULT_REQUEST_TIMEOUT,
    max_retry_delay: float = _policy.DEFAULT_MAX_RETRY_DELAY,
    bootstrap: Optional[FeatureFlagsConfiguration] = None,
    logger: Optional[LoggerLike] = None,
    on_change: Optional[Callable[[FlagsChangedEvent], None]] = None,
    on_error: Optional[Callable[[Exception], None]] = None,
    on_status: Optional[Callable[[RuntimeStatus], None]] = None,
) -> FeatureFlagsRuntimeClient:
    """Create a feature flags runtime client that polls through this client.

    The runtime client evaluates flags locally from a configuration it polls in
    the background. Call ``start()`` to begin polling. See
    :class:`~workos.feature_flags.runtime.FeatureFlagsRuntimeClient` for the
    options.
    """
    return FeatureFlagsRuntimeClient(
        self,
        polling_interval=polling_interval,
        request_timeout=request_timeout,
        max_retry_delay=max_retry_delay,
        bootstrap=bootstrap,
        logger=logger,
        on_change=on_change,
        on_error=on_error,
        on_status=on_status,
    )


def create_async_feature_flags_runtime_client(
    self: AsyncWorkOSClient,
    *,
    polling_interval: float = _policy.DEFAULT_POLLING_INTERVAL,
    request_timeout: float = _policy.DEFAULT_REQUEST_TIMEOUT,
    max_retry_delay: float = _policy.DEFAULT_MAX_RETRY_DELAY,
    bootstrap: Optional[FeatureFlagsConfiguration] = None,
    logger: Optional[LoggerLike] = None,
    on_change: Optional[ChangeListener] = None,
    on_error: Optional[ErrorListener] = None,
    on_status: Optional[StatusListener] = None,
) -> AsyncFeatureFlagsRuntimeClient:
    """Create an async feature flags runtime client that polls through this client.

    The runtime client evaluates flags locally from a configuration it polls in
    an asyncio task. Call ``await start()`` to begin polling. See
    :class:`~workos.feature_flags.runtime.AsyncFeatureFlagsRuntimeClient` for
    the options.
    """
    return AsyncFeatureFlagsRuntimeClient(
        self,
        polling_interval=polling_interval,
        request_timeout=request_timeout,
        max_retry_delay=max_retry_delay,
        bootstrap=bootstrap,
        logger=logger,
        on_change=on_change,
        on_error=on_error,
        on_status=on_status,
    )
