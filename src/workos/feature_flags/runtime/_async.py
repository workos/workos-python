# @oagen-ignore-file
# This file is hand-maintained. The asynchronous feature flags runtime client
# polls in an asyncio task and evaluates flags locally.
# pyright: strict, reportPrivateUsage=false

from __future__ import annotations

import asyncio
import inspect
import time
from types import TracebackType
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Optional, Type, Union

from ..._errors import WorkOSTimeoutError
from . import _policy
from ._configuration import FeatureFlagsConfiguration
from ._context import LoggerLike
from ._core import Notification, RuntimeClientCore, utc_now
from ._types import FlagsChangedEvent, RuntimeStatus

if TYPE_CHECKING:
    from ..._base_client import AsyncWorkOSClient

ChangeListener = Callable[[FlagsChangedEvent], Union[None, Awaitable[None]]]
ErrorListener = Callable[[Exception], Union[None, Awaitable[None]]]
StatusListener = Callable[[RuntimeStatus], Union[None, Awaitable[None]]]


class _Closed(Exception):
    """The client was closed while a refresh was in progress."""


class AsyncFeatureFlagsRuntimeClient(RuntimeClientCore):
    """Polls an environment's feature flag configuration in an asyncio task and evaluates flags locally.

    Create one long-lived instance per event loop and share it. Evaluation
    (``is_enabled``, ``get_all_flags``, ``get_flag``) is synchronous, never
    makes a network request and never raises::

        flags = workos.create_feature_flags_runtime_client()
        await flags.start()
        await flags.wait_until_ready(timeout=5)
        flags.is_enabled("new-checkout", {"organization": "org_123"})

    The client polls through its ``AsyncWorkOSClient``, so use it on that
    client's event loop, and close it before closing the ``AsyncWorkOSClient``.
    """

    def __init__(
        self,
        client: AsyncWorkOSClient,
        *,
        polling_interval: float = _policy.DEFAULT_POLLING_INTERVAL,
        request_timeout: float = _policy.DEFAULT_REQUEST_TIMEOUT,
        max_retry_delay: float = _policy.DEFAULT_MAX_RETRY_DELAY,
        bootstrap: Optional[FeatureFlagsConfiguration] = None,
        logger: Optional[LoggerLike] = None,
        on_change: Optional[ChangeListener] = None,
        on_error: Optional[ErrorListener] = None,
        on_status: Optional[StatusListener] = None,
    ) -> None:
        """Create a runtime client. No request is made until :meth:`start` or :meth:`refresh`.

        Takes the same options as :class:`FeatureFlagsRuntimeClient`. Listeners
        may be plain functions or coroutine functions.

        Raises:
            ConfigurationError: If ``client`` has no API key.
        """
        super().__init__(
            client,
            polling_interval=polling_interval,
            request_timeout=request_timeout,
            max_retry_delay=max_retry_delay,
            bootstrap=bootstrap,
            logger=logger,
        )
        self._client = client
        self._started = False
        self._task: Optional[asyncio.Task[None]] = None
        # Neither primitive binds to an event loop until first awaited.
        self._refresh_lock = asyncio.Lock()
        self._ready = asyncio.Event()
        if self._status.ready:
            self._ready.set()
        if on_change is not None:
            self.add_change_listener(on_change)
        if on_error is not None:
            self.add_error_listener(on_error)
        if on_status is not None:
            self.add_status_listener(on_status)

    # --- Lifecycle ------------------------------------------------------------

    async def start(self) -> None:
        """Start background polling in a task on the running event loop. Idempotent.

        The first poll is sent right away, then every ``polling_interval``
        seconds. Failed polls retry with exponential backoff. A 401 stops
        polling permanently; the last good configuration stays usable.

        Raises:
            RuntimeError: If the client is closed or no event loop is running.
        """
        if self._closed:
            raise RuntimeError(
                "This feature flags runtime client is closed; create a new one"
            )
        if self._started:
            return
        loop = asyncio.get_running_loop()
        self._started = True
        if self._status.polling_stopped:
            self._logger.warning(
                "Not starting feature flag polling: it stopped after a 401. "
                "Create a new runtime client with a valid API key."
            )
            return
        self._task = loop.create_task(self._poll_forever(), name="workos-feature-flags")

    async def wait_until_ready(self, timeout: Optional[float] = None) -> None:
        """Wait until a bootstrap or a successful refresh makes flags available.

        Does not start polling: call :meth:`start` (or :meth:`refresh`).

        Args:
            timeout: Seconds to wait. ``None`` waits indefinitely.

        Raises:
            TimeoutError: If flags are not available within ``timeout``.
            AuthenticationError: If polling stopped after a 401 before any
                configuration was available.
            RuntimeError: If the client was closed before it became ready.
        """
        if self._status.ready:
            return
        try:
            await asyncio.wait_for(self._ready.wait(), timeout)
        except asyncio.TimeoutError:
            # The readiness timeout names the last refresh error as its cause.
            raise self._readiness_timeout(timeout)
        if not self._status.ready:
            raise self._readiness_failure()

    async def refresh(self) -> None:
        """Fetch the configuration now.

        Serialized with background polling. Errors are raised to the caller and
        the last good configuration is kept; ``on_error`` is not called. A 401
        also stops background polling, as it would from a background poll.

        Raises:
            WorkOSError: If the request fails or the payload cannot be read.
            RuntimeError: If the client is closed.
        """
        if self._closed:
            raise RuntimeError(
                "This feature flags runtime client is closed; create a new one"
            )
        try:
            await self._refresh(background=False)
        except _Closed:
            raise RuntimeError(
                "The feature flags runtime client was closed during the refresh"
            ) from None
        except Exception as error:
            if _policy.is_unauthorized(error):
                await self._stop_polling(error)
            raise

    async def close(self) -> None:
        """Stop polling and wait for the polling task to finish. Idempotent.

        Evaluation keeps serving the last configuration after closing.
        """
        if self._closed:
            return
        self._closed = True
        self._ready.set()
        task = self._task
        if task is None or task.done() or task is asyncio.current_task():
            # Called from a listener inside the polling task: the task exits on
            # its own once the listener returns.
            return
        task.cancel()
        # `wait` never raises the task's own cancellation, but still
        # propagates a cancellation of the caller.
        await asyncio.wait({task})

    async def __aenter__(self) -> AsyncFeatureFlagsRuntimeClient:
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        await self.close()

    # --- Listeners ------------------------------------------------------------

    def add_change_listener(self, listener: ChangeListener) -> None:
        """Call ``listener`` after a refresh installs a different configuration.

        Fires on the first load and on the first refresh that differs from a
        bootstrap; never for identical refreshes or failures. Coroutine
        listeners are awaited. Listeners run one at a time in refresh order;
        their exceptions are logged and never affect polling.
        """
        self._add_listener("change", listener)

    def remove_change_listener(self, listener: ChangeListener) -> None:
        """Stop calling a change listener."""
        self._remove_listener("change", listener)

    def add_error_listener(self, listener: ErrorListener) -> None:
        """Call ``listener`` with the error of every failed background poll."""
        self._add_listener("error", listener)

    def remove_error_listener(self, listener: ErrorListener) -> None:
        """Stop calling an error listener."""
        self._remove_listener("error", listener)

    def add_status_listener(self, listener: StatusListener) -> None:
        """Call ``listener`` with the new status after every refresh and when polling stops."""
        self._add_listener("status", listener)

    def remove_status_listener(self, listener: StatusListener) -> None:
        """Stop calling a status listener."""
        self._remove_listener("status", listener)

    # --- Polling --------------------------------------------------------------

    async def _poll_forever(self) -> None:
        failures = 0
        while not self._closed and not self._status.polling_stopped:
            retry_after: Optional[float] = None
            try:
                await self._refresh(background=True)
                failures = 0
            except _Closed:
                return
            except Exception as error:
                if self._closed:
                    return
                if _policy.is_unauthorized(error):
                    await self._stop_polling(error)
                    return
                failures = min(failures + 1, _policy.MAX_COUNTED_FAILURES)
                retry_after = _policy.retry_after(error)
            if self._closed:
                return
            delay = _policy.next_delay(
                self._polling_interval, failures, self._max_retry_delay
            )
            await asyncio.sleep(max(delay, retry_after or 0.0))

    async def _refresh(self, *, background: bool) -> None:
        async with self._refresh_lock:
            if self._closed or (background and self._status.polling_stopped):
                raise _Closed()
            attempted = utc_now()
            try:
                payload = await asyncio.wait_for(self._fetch(), self._request_timeout)
                configuration = self._parse(payload)
            except asyncio.TimeoutError as error:
                if self._closed:
                    raise _Closed() from error
                timeout = WorkOSTimeoutError(
                    f"Feature flag refresh exceeded its request timeout of {self._request_timeout} seconds"
                )
                await self._deliver(
                    self._record_failure(timeout, attempted, background=background)
                )
                raise timeout from error
            except Exception as error:
                if self._closed:
                    raise _Closed() from error
                await self._deliver(
                    self._record_failure(error, attempted, background=background)
                )
                raise
            if self._closed:
                raise _Closed()
            notifications = self._record_success(
                configuration, attempted, background=background
            )
            self._ready.set()
            await self._deliver(notifications)

    async def _fetch(self) -> Any:
        deadline = time.monotonic() + self._request_timeout
        attempt = 0
        while True:
            remaining = max(deadline - time.monotonic(), 0.001)
            try:
                return await self._client.request(
                    "get",
                    _policy.POLL_PATH,
                    params=dict(_policy.POLL_PARAMS),
                    request_options={"timeout": remaining, "max_retries": 0},
                )
            except Exception as error:
                delay = _policy.attempt_retry_delay(
                    error, attempt, deadline - time.monotonic(), self._max_retries
                )
                if delay is None:
                    raise
                await asyncio.sleep(delay)
                attempt += 1

    async def _stop_polling(self, error: Exception) -> None:
        async with self._refresh_lock:
            if self._status.polling_stopped:
                return
            notifications = self._record_polling_stopped(error)
            if not self._status.ready:
                self._readiness_error = error
            self._ready.set()
            task = self._task
            if task is not None and task is not asyncio.current_task():
                task.cancel()
            await self._deliver(notifications)

    async def _deliver(self, notifications: list[Notification]) -> None:
        if self._closed:
            return
        for listener, argument in notifications:
            try:
                result = listener(argument)
                if inspect.isawaitable(result):
                    await result
            except Exception:
                self._log_listener_error()
