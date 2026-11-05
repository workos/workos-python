# @oagen-ignore-file
# This file is hand-maintained. The synchronous feature flags runtime client
# polls on a background thread and evaluates flags locally.
# pyright: strict, reportPrivateUsage=false

from __future__ import annotations

import inspect
import os
import threading
import time
import weakref
from types import TracebackType
from typing import TYPE_CHECKING, Any, Callable, Optional, Type

from . import _core, _policy
from ._configuration import FeatureFlagsConfiguration
from ._context import LoggerLike
from ._core import (
    Listener,
    Notification,
    RuntimeClientCore,
    fork_blocked_message,
    utc_now,
)
from ._transport import PollTransport
from ._types import FlagsChangedEvent, RuntimeStatus

if TYPE_CHECKING:
    from ..._base_client import WorkOSClient


class _Closed(Exception):
    """The client was closed while a refresh was in progress."""


class FeatureFlagsRuntimeClient(RuntimeClientCore):
    """Polls an environment's feature flag configuration and evaluates flags locally.

    Create one long-lived instance per process and share it across requests.
    Evaluation never makes a network request and never raises. Polling runs on
    a daemon thread started by :meth:`start` and stopped by :meth:`close`::

        flags = workos.create_feature_flags_runtime_client()
        flags.start()
        flags.wait_until_ready(timeout=5)
        flags.is_enabled("new-checkout", {"organization": "org_123"})

    Polling uses the ``WorkOSClient``'s API key, base URL, headers and retry
    settings. With the SDK's default HTTP client it polls through an HTTP
    client of its own, which a forked child replaces; with an HTTP client you
    supplied, close this client before closing yours. A client created before
    a fork can start in the child, and one that was polling resumes there,
    except through an HTTP client you supplied that the parent already sent
    requests through, and on macOS. That includes a fork that skips Python's
    fork hooks, as uWSGI's does by default: the client checks for a new
    process each time it is used.
    """

    def __init__(
        self,
        client: WorkOSClient,
        *,
        polling_interval: float = _policy.DEFAULT_POLLING_INTERVAL,
        request_timeout: float = _policy.DEFAULT_REQUEST_TIMEOUT,
        max_retry_delay: float = _policy.DEFAULT_MAX_RETRY_DELAY,
        bootstrap: Optional[FeatureFlagsConfiguration] = None,
        logger: Optional[LoggerLike] = None,
        on_change: Optional[Callable[[FlagsChangedEvent], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        on_status: Optional[Callable[[RuntimeStatus], None]] = None,
    ) -> None:
        """Create a runtime client. No request is made until :meth:`start` or :meth:`refresh`.

        Args:
            client: The ``WorkOSClient`` whose API key, base URL and HTTP client to poll with.
            polling_interval: Seconds between polls, before a 10% jitter. At least 5.
            request_timeout: Seconds one refresh may take, including retries of
                transient failures. The response is streamed and every network
                wait gets only the time left, so a refresh ends within this, plus
                at most one read of a response body that stalls. A custom
                ``HTTPBackend`` that is not an httpx client gets the remaining
                time as its per-request timeout instead.
            max_retry_delay: Upper bound in seconds for the exponential backoff
                after failed polls. Polls never come sooner than the interval.
            bootstrap: A cached configuration to evaluate from before the first
                successful poll. Makes the client ready immediately.
            logger: Where to log failures and ignored context. Defaults to the
                ``workos.feature_flags.runtime`` logger.
            on_change: Called after a refresh installs a different configuration,
                including the first load.
            on_error: Called when a background poll fails.
            on_status: Called after every refresh, successful or not, and when
                polling stops.

        Raises:
            ConfigurationError: If ``client`` has no API key.
            TypeError: If a listener is an async function.
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
        self._transport = PollTransport(client)
        self._thread: Optional[threading.Thread] = None
        self._delivering: Optional[int] = None
        self._fork_restart_pending = False
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
        self._lifecycle_lock = threading.Lock()
        self._refresh_lock = threading.RLock()
        self._drain_lock = threading.Lock()
        # `_stop` is set by close(); `_wake` also interrupts the poller's sleep
        # when polling stops after a 401.
        self._stop = threading.Event()
        self._wake = threading.Event()
        self._ready = threading.Event()
        if self._closed or self._status.ready or self._readiness_error is not None:
            self._ready.set()
        if self._closed:
            self._stop.set()
            self._wake.set()

    # --- Lifecycle ------------------------------------------------------------

    def start(self) -> None:
        """Start background polling. Returns immediately and is idempotent.

        The first poll is sent right away, then every ``polling_interval``
        seconds. Failed polls retry with exponential backoff. A 401 stops
        polling permanently; the last good configuration stays usable. In a
        forked child on macOS, a client created before the fork does not
        poll: this logs a warning and returns.

        Raises:
            RuntimeError: If the client is closed, or cannot poll in this forked
                process because the parent sent requests through the HTTP
                client you supplied.
        """
        self._before_use()
        with self._lifecycle_lock:
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
            self._started = True
            if self._status.polling_stopped:
                self._logger.warning(
                    "Not starting feature flag polling: it stopped after a 401. "
                    "Create a new runtime client with a valid API key."
                )
                return
            self._spawn_poller()

    def wait_until_ready(self, timeout: Optional[float] = None) -> None:
        """Block until a bootstrap or a successful refresh makes flags available.

        Does not start polling: call :meth:`start` (or :meth:`refresh`), possibly
        from another thread.

        Args:
            timeout: Seconds to wait. ``None`` waits indefinitely.

        Raises:
            TimeoutError: If flags are not available within ``timeout``.
            AuthenticationError: If polling stopped after a 401 before any
                configuration was available.
            RuntimeError: If the client was closed before it became ready, or
                has no configuration and cannot poll in this forked process.
        """
        self._before_use()
        if self._status.ready:
            return
        # Nothing can make the client ready in a forked child that cannot poll.
        self._raise_if_fork_blocked()
        if not self._ready.wait(timeout):
            raise self._readiness_timeout(timeout)
        if not self._status.ready:
            raise self._readiness_failure()

    def refresh(self) -> None:
        """Fetch the configuration now, on the calling thread.

        Serialized with background polling. Errors are raised to the caller and
        the last good configuration is kept; ``on_error`` is not called. A 401
        also stops background polling, as it would from a background poll.

        Raises:
            WorkOSError: If the request fails or the payload cannot be read.
            RuntimeError: If the client is closed or cannot poll in this forked
                process.
        """
        self._before_use()
        if self._closed:
            raise RuntimeError(
                "This feature flags runtime client is closed; create a new one"
            )
        self._raise_if_fork_blocked()
        try:
            self._refresh(background=False)
        except _Closed:
            raise RuntimeError(
                "The feature flags runtime client was closed during the refresh"
            ) from None
        except Exception as error:
            if _policy.is_unauthorized(error):
                self._stop_polling(error)
            raise

    def close(self) -> None:
        """Stop polling and release the background thread. Idempotent.

        Waits up to ``request_timeout`` for an in-flight poll to finish, then
        closes the HTTP client polling used, if the runtime created it. A poll
        still running after that, such as one reading a stalled response, is
        abandoned: it ends on its own and changes nothing. Every caller waits,
        including one that calls while another close() is still waiting.
        Evaluation keeps serving the last configuration after closing.
        """
        self._reinitialize_if_forked()
        with self._lifecycle_lock:
            if not self._closed:
                self._closed = True
                self._stop.set()
                self._wake.set()
                self._ready.set()
            thread = self._thread
        if (
            thread is not None
            and thread is not threading.current_thread()
            and self._delivering != threading.get_ident()
            and thread.is_alive()
        ):
            thread.join(self._request_timeout + 1.0)
        self._transport.close()

    def __enter__(self) -> FeatureFlagsRuntimeClient:
        self.start()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.close()

    # --- Listeners ------------------------------------------------------------

    def _add_listener(self, kind: str, listener: Listener) -> None:
        # Nothing awaits what a listener returns, so an async function would
        # never run.
        if inspect.iscoroutinefunction(listener):
            raise TypeError(
                f"{kind} listener must be a plain function, not an async function; "
                "use AsyncFeatureFlagsRuntimeClient for async listeners"
            )
        super()._add_listener(kind, listener)

    def add_change_listener(
        self, listener: Callable[[FlagsChangedEvent], None]
    ) -> None:
        """Call ``listener`` after a refresh installs a different configuration.

        Fires on the first load and on the first refresh that differs from a
        bootstrap; never for identical refreshes or failures. Persist
        ``event.current.to_json()`` here to keep a bootstrap cache fresh.
        Listeners run one at a time in refresh order, on the thread that
        refreshed or on one already delivering notifications; their exceptions
        are logged and never affect polling. Listeners must be plain functions:
        an async function raises ``TypeError``.
        """
        self._add_listener("change", listener)

    def remove_change_listener(
        self, listener: Callable[[FlagsChangedEvent], None]
    ) -> None:
        """Stop calling a change listener."""
        self._remove_listener("change", listener)

    def add_error_listener(self, listener: Callable[[Exception], None]) -> None:
        """Call ``listener`` with the error of every failed background poll."""
        self._add_listener("error", listener)

    def remove_error_listener(self, listener: Callable[[Exception], None]) -> None:
        """Stop calling an error listener."""
        self._remove_listener("error", listener)

    def add_status_listener(self, listener: Callable[[RuntimeStatus], None]) -> None:
        """Call ``listener`` with the new status after every refresh and when polling stops."""
        self._add_listener("status", listener)

    def remove_status_listener(self, listener: Callable[[RuntimeStatus], None]) -> None:
        """Stop calling a status listener."""
        self._remove_listener("status", listener)

    # --- Polling --------------------------------------------------------------

    def _spawn_poller(self) -> None:
        thread = threading.Thread(
            target=self._poll_forever, name="workos-feature-flags", daemon=True
        )
        self._thread = thread
        thread.start()

    def _poll_forever(self) -> None:
        failures = 0
        while not self._stop.is_set() and not self._status.polling_stopped:
            retry_after: Optional[float] = None
            try:
                self._refresh(background=True)
                failures = 0
            except _Closed:
                return
            except Exception as error:
                if self._stop.is_set():
                    return
                if _policy.is_unauthorized(error):
                    self._stop_polling(error)
                    return
                failures = min(failures + 1, _policy.MAX_COUNTED_FAILURES)
                retry_after = _policy.retry_after(error)
            delay = _policy.next_delay(
                self._polling_interval, failures, self._max_retry_delay
            )
            if self._wake.wait(max(delay, retry_after or 0.0)):
                return

    def _refresh(self, *, background: bool) -> None:
        try:
            with self._refresh_lock:
                self._refresh_locked(background=background)
        finally:
            self._drain()

    def _refresh_locked(self, *, background: bool) -> None:
        if self._closed or (background and self._status.polling_stopped):
            raise _Closed()
        attempted = utc_now()
        # close() sets `_closed` under the lifecycle lock, so checking it and
        # recording the outcome under that lock means nothing a refresh does
        # lands after close() returns.
        try:
            configuration = self._parse(self._fetch())
        except _Closed:
            raise
        except Exception as error:
            with self._lifecycle_lock:
                if self._closed:
                    raise _Closed() from error
                self._pending.append(
                    self._record_failure(error, attempted, background=background)
                )
            raise
        with self._lifecycle_lock:
            if self._closed:
                raise _Closed()
            notifications = self._record_success(
                configuration, attempted, background=background
            )
        self._ready.set()
        self._pending.append(notifications)

    def _fetch(self) -> Any:
        deadline = time.monotonic() + self._request_timeout
        attempt = 0
        while True:
            try:
                return self._transport.get(deadline)
            except Exception as error:
                delay = _policy.attempt_retry_delay(
                    error, attempt, deadline - time.monotonic(), self._max_retries
                )
                if delay is None:
                    raise
                if self._stop.wait(delay):
                    raise _Closed() from error
                attempt += 1

    def _stop_polling(self, error: Exception) -> None:
        with self._refresh_lock:
            if self._status.polling_stopped:
                return
            notifications = self._record_polling_stopped(error)
            if not self._status.ready:
                self._readiness_error = error
            self._wake.set()
            self._ready.set()
            self._pending.append(notifications)
        self._drain()

    def _drain(self) -> None:
        """Deliver pending notifications in refresh order, one batch at a time.

        Only one thread delivers at once. A refresh that finishes while
        another thread is delivering leaves its batch to that thread, which
        also covers a listener calling refresh(): its batch is delivered after
        the current one, never interleaved with it.
        """
        with self._drain_lock:
            if self._delivering is not None:
                return
            self._delivering = threading.get_ident()
        try:
            while True:
                with self._drain_lock:
                    if not self._pending:
                        self._delivering = None
                        return
                    batch = self._pending.popleft()
                if not self._closed:
                    self._deliver(batch)
        except BaseException:
            with self._drain_lock:
                self._delivering = None
            raise

    def _deliver(self, notifications: list[Notification]) -> None:
        for listener, argument in notifications:
            try:
                result = listener(argument)
            except Exception:
                self._log_listener_error()
                continue
            if inspect.isawaitable(result):
                _discard_awaitable(result)
                self._logger.warning(
                    "A FeatureFlagsRuntimeClient listener returned an awaitable, "
                    "which was not awaited; use AsyncFeatureFlagsRuntimeClient for "
                    "async listeners"
                )

    # --- Fork safety ----------------------------------------------------------

    def _before_use(self) -> None:
        # Evaluation runs this on every call, so the common case is one compare.
        if self._pid != os.getpid():
            self._reinitialize_after_unhooked_fork()
        if self._fork_restart_pending:
            self._restart_after_fork()
        else:
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

    def _restart_after_fork(self) -> None:
        with self._lifecycle_lock:
            if not self._fork_restart_pending:
                return
            self._fork_restart_pending = False
            if self._closed:
                return
            self._logger.info(
                "Restarting feature flag polling in forked process %d", os.getpid()
            )
            self._spawn_poller()

    def _reinitialize_after_fork(self) -> None:
        # The parent's other threads don't exist in the child. Locks may have
        # been held by them, the poller thread is gone, and the parent's HTTP
        # connections must not be shared, so rebuild all of it and restart
        # polling, with a new HTTP client, on the next use.
        self._reinitialize_core_after_fork()
        self._transport.reinitialize_after_fork()
        self._delivering = None
        self._thread = None
        self._init_synchronization()
        polling = (
            self._started and not self._closed and not self._status.polling_stopped
        )
        self._fork_blocker = (
            None
            if self._closed
            else self._transport.fork_blocker(self._used_before_fork())
        )
        # On macOS every client created before the fork is blocked, however
        # the parent used it, so start() warns instead of raising there.
        self._fork_blocked_by_platform = (
            self._fork_blocker is not None and not _core.FORK_SAFE_PLATFORM
        )
        self._fork_restart_pending = polling and self._fork_blocker is None
        # Only a client that was polling warns, on first use, that it no longer
        # polls. On macOS any other warns once started; elsewhere start()
        # raises instead.
        self._fork_warned = not polling


def _discard_awaitable(awaitable: object) -> None:
    close = getattr(awaitable, "close", None)
    if callable(close):
        close()


_clients: weakref.WeakSet[FeatureFlagsRuntimeClient] = weakref.WeakSet()


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
