# @oagen-ignore-file
# This file is hand-maintained. The asynchronous feature flags runtime client
# polls in an asyncio task and evaluates flags locally.
# pyright: strict, reportPrivateUsage=false

from __future__ import annotations

import asyncio
import inspect
import os
import time
import weakref
from types import TracebackType
from typing import TYPE_CHECKING, Any, Awaitable, Callable, Optional, Type, Union

from ..._errors import WorkOSTimeoutError
from . import _core, _policy
from ._configuration import FeatureFlagsConfiguration
from ._context import LoggerLike
from ._core import Notification, RuntimeClientCore, fork_blocked_message, utc_now
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
    A client created before a fork, including one that skips Python's fork
    hooks, can start in the child unless the ``AsyncWorkOSClient`` already
    sent requests in the parent, or the platform is macOS.
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
        self._task: Optional[asyncio.Task[None]] = None
        # The task delivering notifications, and the coroutine listener it is
        # waiting for, if any.
        self._drainer: Optional[asyncio.Task[Any]] = None
        self._listener_task: Optional[asyncio.Future[Any]] = None
        # Why polling cannot run in this forked child, if it cannot, and
        # whether the platform is why.
        self._fork_blocker: Optional[str] = None
        self._fork_blocked_by_platform = False
        self._fork_warned = False
        self._init_synchronization()
        if on_change is not None:
            self.add_change_listener(on_change)
        if on_error is not None:
            self.add_error_listener(on_error)
        if on_status is not None:
            self.add_status_listener(on_status)
        _clients.add(self)

    def _init_synchronization(self) -> None:
        # None of these binds to an event loop until first awaited.
        self._refresh_lock = asyncio.Lock()
        self._ready = asyncio.Event()
        # Set when polling stops after a 401, to end the polling task's sleep.
        self._wake = asyncio.Event()
        if self._closed or self._status.ready or self._readiness_error is not None:
            self._ready.set()

    # --- Lifecycle ------------------------------------------------------------

    async def start(self) -> None:
        """Start background polling in a task on the running event loop. Idempotent.

        The first poll is sent right away, then every ``polling_interval``
        seconds. Failed polls retry with exponential backoff. A 401 stops
        polling permanently; the last good configuration stays usable. In a
        forked child on macOS, a client created before the fork does not
        poll: this logs a warning and returns.

        Raises:
            RuntimeError: If the client is closed, no event loop is running, or
                the client cannot poll in this forked process because the
                parent used the ``AsyncWorkOSClient`` or its HTTP client.
        """
        self._reinitialize_if_forked()
        if self._closed:
            raise RuntimeError(
                "This feature flags runtime client is closed; create a new one"
            )
        if self._fork_blocked_by_platform:
            self._skip_start_after_fork()
            return
        self._raise_if_fork_blocked()
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
            RuntimeError: If the client was closed before it became ready, or
                has no configuration and cannot poll in this forked process.
        """
        self._reinitialize_if_forked()
        if self._status.ready:
            return
        # Nothing can make the client ready in a forked child that cannot poll.
        self._raise_if_fork_blocked()
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
            RuntimeError: If the client is closed or cannot poll in this forked
                process.
        """
        self._reinitialize_if_forked()
        if self._closed:
            raise RuntimeError(
                "This feature flags runtime client is closed; create a new one"
            )
        self._raise_if_fork_blocked()
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

        Every caller waits, including one that calls while another close() is
        still waiting. Evaluation keeps serving the last configuration after
        closing.
        """
        self._reinitialize_if_forked()
        first = not self._closed
        self._closed = True
        self._ready.set()
        task = self._task
        current = asyncio.current_task()
        if (
            task is None
            or task.done()
            or task is current
            or (current is self._listener_task and self._drainer is task)
        ):
            # Called from a listener the polling task is delivering to: the
            # task exits on its own once the listener returns.
            return
        if first:
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
            try:
                await asyncio.wait_for(
                    self._wake.wait(), timeout=max(delay, retry_after or 0.0)
                )
            except asyncio.TimeoutError:
                pass

    async def _refresh(self, *, background: bool) -> None:
        try:
            async with self._refresh_lock:
                await self._refresh_locked(background=background)
        finally:
            await self._drain()

    async def _refresh_locked(self, *, background: bool) -> None:
        if (
            self._closed
            or self._fork_blocker is not None
            or (background and self._status.polling_stopped)
        ):
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
            self._pending.append(
                self._record_failure(timeout, attempted, background=background)
            )
            raise timeout from error
        except Exception as error:
            if self._closed:
                raise _Closed() from error
            self._pending.append(
                self._record_failure(error, attempted, background=background)
            )
            raise
        if self._closed:
            raise _Closed()
        notifications = self._record_success(
            configuration, attempted, background=background
        )
        self._ready.set()
        self._pending.append(notifications)

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
            self._wake.set()
            self._pending.append(notifications)
        await self._drain()

    async def _drain(self) -> None:
        """Deliver pending notifications in refresh order, one batch at a time.

        A refresh that finishes while another task is delivering, including a
        listener calling refresh(), leaves its batch to that task, so batches
        are never interleaved.
        """
        if self._drainer is not None:
            return
        self._drainer = asyncio.current_task()
        try:
            while self._pending:
                batch = self._pending.popleft()
                if not self._closed:
                    await self._deliver(batch)
        finally:
            self._drainer = None

    async def _deliver(self, notifications: list[Notification]) -> None:
        for listener, argument in notifications:
            try:
                result = listener(argument)
                if inspect.isawaitable(result):
                    await self._await_listener(result)
            except Exception:
                self._log_listener_error()

    async def _await_listener(self, awaitable: Awaitable[Any]) -> None:
        # The listener runs in a task of its own, so a CancelledError raised
        # inside it, such as from awaiting work something else cancelled, ends
        # only that listener. Cancelling the delivering task, as close() does,
        # cancels the listener with it.
        listener_task = asyncio.ensure_future(awaitable)
        self._listener_task = listener_task
        try:
            await asyncio.wait({listener_task})
        except asyncio.CancelledError:
            listener_task.cancel()
            await asyncio.wait({listener_task})
            raise
        finally:
            self._listener_task = None
        if listener_task.cancelled():
            self._logger.error("A feature flags runtime client listener was cancelled")
        else:
            listener_task.result()

    # --- Fork safety ----------------------------------------------------------

    def _reinitialize_after_fork(self) -> None:
        # Once the AsyncWorkOSClient's HTTP client has sent requests, its
        # connections belong to the parent's event loop, so a copy of a client
        # that polled, or whose HTTP client carried other calls (from this or
        # another AsyncWorkOSClient), stops polling here (even if the child
        # keeps running a copy of the loop) and keeps serving its last
        # configuration. Otherwise it starts over on the child's own loop.
        self._reinitialize_core_after_fork()
        polling = (
            self._started and not self._closed and not self._status.polling_stopped
        )
        # The polling task and anything waiting on these primitives belong to
        # the parent's event loop, which may not run here: close() must not
        # wait for that task.
        self._task = None
        self._drainer = None
        self._listener_task = None
        self._init_synchronization()
        if self._closed:
            self._fork_blocker = None
        elif not _core.FORK_SAFE_PLATFORM:
            self._fork_blocker = (
                f"{_core.MACOS_FORK_HAZARD}. Create the AsyncWorkOSClient and the "
                "runtime client after forking instead, for example in gunicorn's "
                "post_fork hook"
            )
        elif self._used_before_fork() or _core.used_by_another_process(self._client):
            self._fork_blocker = (
                "the AsyncWorkOSClient or its HTTP client was used in the parent, "
                "on the parent's event loop and connections. Create the "
                "AsyncWorkOSClient and the runtime client after forking instead"
            )
        else:
            self._fork_blocker = None
        # On macOS every client created before the fork is blocked, however
        # the parent used it, so start() warns instead of raising there.
        self._fork_blocked_by_platform = (
            self._fork_blocker is not None and not _core.FORK_SAFE_PLATFORM
        )
        # Only a client that was polling warns, on first use, that it no longer
        # polls. On macOS any other warns once started; elsewhere start()
        # raises instead.
        self._fork_warned = not polling

    def _before_use(self) -> None:
        # Evaluation runs this on every call, so the common case is one compare.
        if self._pid != os.getpid():
            self._reinitialize_after_unhooked_fork()
        self._warn_if_fork_blocked()

    def _warn_if_fork_blocked(self) -> None:
        if self._fork_blocker is not None and not self._fork_warned:
            self._fork_warned = True
            self._logger.warning(
                "%s. Evaluation keeps serving the last configuration.",
                fork_blocked_message(self._fork_blocker),
            )

    def _raise_if_fork_blocked(self) -> None:
        if self._fork_blocker is not None:
            raise RuntimeError(fork_blocked_message(self._fork_blocker))

    def _skip_start_after_fork(self) -> None:
        # A client that was polling warns once, on first use. Starting one
        # that was not makes it such a client, which has not warned yet.
        if not self._started:
            self._started = True
            self._fork_warned = False
        self._warn_if_fork_blocked()


_clients: weakref.WeakSet[AsyncFeatureFlagsRuntimeClient] = weakref.WeakSet()


def _reinitialize_clients_after_fork() -> None:
    for client in list(_clients):
        # One client that fails must not leave the others unprepared.
        try:
            client._after_fork_in_child()
        except Exception:
            client._logger.exception(
                "Could not prepare a feature flags runtime client for forked "
                "process %d",
                os.getpid(),
            )


if hasattr(os, "register_at_fork"):
    os.register_at_fork(after_in_child=_reinitialize_clients_after_fork)
