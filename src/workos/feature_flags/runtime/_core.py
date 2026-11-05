# @oagen-ignore-file
# This file is hand-maintained. State and local evaluation shared by the sync
# and async feature flags runtime clients.
# pyright: strict, reportPrivateUsage=false

from __future__ import annotations

import copy
import logging
import os
import sys
import threading
from collections import deque
from dataclasses import replace
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Callable, Deque, Optional, Tuple, Union

from ..._errors import APIError
from ..._http import sent_requests_from_another_process
from . import _policy
from ._configuration import (
    FeatureFlagsConfiguration,
    FeatureFlagsConfigurationError,
    FlagDefinition,
    changed_flags,
    configuration_for,
)
from ._context import ContextWarnings, EvaluationContext, LoggerLike, normalize_context
from ._types import FlagsChangedEvent, RuntimeStatus

if TYPE_CHECKING:
    from ..._base_client import AsyncWorkOSClient, WorkOSClient, _BaseWorkOSClient

LOGGER_NAME = "workos.feature_flags.runtime"

Listener = Callable[[Any], object]
Notification = Tuple[Listener, Any]

# On macOS, once a process has created an HTTP client, a child it forks without
# exec'ing can crash inside system libraries (DNS resolution, proxy settings,
# the system trust store) when it opens a network connection. Every
# WorkOSClient has an HTTP client, so a runtime client created before the fork
# never polls in the child there.
FORK_SAFE_PLATFORM = sys.platform != "darwin"
MACOS_FORK_HAZARD = (
    "on macOS, a forked process cannot safely open network connections once its "
    "parent has created an HTTP client"
)


def fork_blocked_message(reason: str) -> str:
    return (
        f"Feature flag polling does not run in forked process {os.getpid()}: {reason}"
    )


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def used_by_another_process(client: Union[WorkOSClient, AsyncWorkOSClient]) -> bool:
    """Whether another process sent requests through ``client`` or its HTTP client.

    In a forked process, those are the parent's requests from before the
    fork, so the answer doesn't change when the child sends its own.
    """
    first_request_pid = client._first_request_pid
    return (
        first_request_pid is not None and first_request_pid != os.getpid()
    ) or sent_requests_from_another_process(client._backend)


class RuntimeClientCore:
    """Readiness, status, listeners and local evaluation for a runtime client.

    The configuration snapshot is immutable and replaced by a single reference
    assignment, so evaluation never locks and always sees one complete
    snapshot, even while a refresh replaces it on another thread.
    """

    def __init__(
        self,
        client: _BaseWorkOSClient,
        *,
        polling_interval: float,
        request_timeout: float,
        max_retry_delay: float,
        bootstrap: Optional[FeatureFlagsConfiguration],
        logger: Optional[LoggerLike],
    ) -> None:
        # A client built for public (PKCE) flows has no API key, and every
        # poll would fail with a 401. Fail before starting instead.
        client._require_api_key()
        _require_configuration(bootstrap)
        self._polling_interval = _policy.polling_interval(polling_interval)
        self._request_timeout = _policy.validate_duration(
            request_timeout, "request_timeout"
        )
        self._max_retry_delay = _policy.validate_duration(
            max_retry_delay, "max_retry_delay"
        )
        # Retries of transient failures inside one refresh follow the client's
        # `max_retries`, as the Node SDK's transport retries do.
        self._max_retries = client._resolve_max_retries(None)
        self._logger: LoggerLike = (
            logger if logger is not None else logging.getLogger(LOGGER_NAME)
        )
        self._context_warnings = ContextWarnings(self._logger)
        self._status = RuntimeStatus(configuration=bootstrap)
        self._status_lock = threading.Lock()
        self._listeners_lock = threading.Lock()
        self._listeners: dict[str, tuple[Listener, ...]] = {
            "change": (),
            "error": (),
            "status": (),
        }
        self._started = False
        self._closed = False
        # Notification batches, appended in refresh order while the refresh
        # lock is held and delivered after it is released, so a listener may
        # call refresh() itself.
        self._pending: Deque[list[Notification]] = deque()
        # The 401 that stopped polling before any configuration was available.
        self._readiness_error: Optional[Exception] = None
        # The process this client was created in or last prepared for. A
        # different one means a fork that skipped Python's fork hooks.
        self._pid = os.getpid()
        # The threads preparing this client for a process, by process ID; see
        # _reinitialize_after_unhooked_fork.
        self._fork_claims: dict[int, threading.Event] = {}

    # --- Evaluation -----------------------------------------------------------

    def is_enabled(
        self,
        slug: str,
        context: Optional[EvaluationContext] = None,
        *,
        default: bool = False,
    ) -> bool:
        """Evaluate one flag locally, without a network request.

        A disabled flag serves its off value. For an enabled flag, the first rule
        whose conditions all match the context wins; otherwise the flag's
        default value applies. ``default`` is returned for a missing flag, an
        unready client, and a flag without a boolean answer. Never raises:
        invalid context entries are ignored with a logged warning.

        Args:
            slug: The flag's slug.
            context: Target type to exact ID, e.g. ``{"user": "user_123",
                "organization": "org_123", "workspace": "ws_1"}``.
            default: Returned when the flag has no answer.
        """
        self._before_use()
        configuration = self._status.configuration
        flag = configuration._compiled(slug) if configuration is not None else None
        if flag is None:
            return default
        answer = flag.evaluate(normalize_context(context, self._context_warnings))
        return default if answer is None else answer

    def get_all_flags(
        self, context: Optional[EvaluationContext] = None
    ) -> dict[str, bool]:
        """Evaluate every flag in one snapshot for the given context.

        Flags without a boolean answer, such as a future multivariate flag, are
        omitted so that ``flags.get(slug, my_default)`` applies your default.
        An unready client returns an empty dict.
        """
        self._before_use()
        configuration = self._status.configuration
        if configuration is None:
            return {}
        targets = normalize_context(context, self._context_warnings)
        evaluated: dict[str, bool] = {}
        for slug, flag in configuration._compiled_items():
            answer = flag.evaluate(targets)
            if answer is not None:
                evaluated[slug] = answer
        return evaluated

    def get_flag(self, slug: str) -> Optional[FlagDefinition]:
        """Return one flag's configuration from the current snapshot, for inspection."""
        self._before_use()
        configuration = self._status.configuration
        return configuration.get_flag(slug) if configuration is not None else None

    @property
    def status(self) -> RuntimeStatus:
        """Readiness, the current snapshot, refresh timestamps, counts and the last error."""
        self._before_use()
        return self._status

    @property
    def configuration(self) -> Optional[FeatureFlagsConfiguration]:
        """The current snapshot, suitable for persisting with ``to_json()``."""
        self._before_use()
        return self._status.configuration

    @property
    def is_ready(self) -> bool:
        """Whether a validated configuration is available for local evaluation."""
        self._before_use()
        return self._status.configuration is not None

    @property
    def is_closed(self) -> bool:
        """Whether ``close()`` has been called."""
        self._before_use()
        return self._closed

    # --- Listeners ------------------------------------------------------------

    def _add_listener(self, kind: str, listener: Listener) -> None:
        if not callable(listener):
            raise TypeError(f"{kind} listener must be callable")
        self._reinitialize_if_forked()
        with self._listeners_lock:
            self._listeners[kind] = (*self._listeners[kind], listener)

    def _remove_listener(self, kind: str, listener: Listener) -> None:
        self._reinitialize_if_forked()
        with self._listeners_lock:
            self._listeners[kind] = tuple(
                registered
                for registered in self._listeners[kind]
                if registered != listener
            )

    def _notifications(self, kind: str, argument: object) -> list[Notification]:
        return [(listener, argument) for listener in self._listeners[kind]]

    # --- Refresh outcomes -----------------------------------------------------

    def _record_success(
        self,
        configuration: FeatureFlagsConfiguration,
        attempted: datetime,
        *,
        background: bool,
    ) -> list[Notification]:
        with self._status_lock:
            previous = self._status
            current = replace(
                previous,
                configuration=configuration,
                last_successful_refresh_at=utc_now(),
                last_refresh_attempt_at=attempted,
                last_error=None,
                refresh_count=previous.refresh_count + 1,
            )
            self._status = current
        if background and previous.last_error is not None:
            self._logger.info("Feature flag refresh recovered")
        self._logger.debug(
            "Feature flag refresh succeeded (%d flags)", len(configuration)
        )
        notifications = self._notifications("status", current)
        # An unchanged payload keeps the same snapshot. A new one can differ
        # only outside its flags, and a cache persisted from change events
        # still needs it.
        if configuration is not previous.configuration:
            changed = changed_flags(previous.configuration, configuration)
            event = FlagsChangedEvent(previous.configuration, configuration, changed)
            notifications += self._notifications("change", event)
        return notifications

    def _record_failure(
        self, error: Exception, attempted: datetime, *, background: bool
    ) -> list[Notification]:
        with self._status_lock:
            previous = self._status
            current = replace(
                previous,
                last_refresh_attempt_at=attempted,
                last_error=error,
                refresh_count=previous.refresh_count + 1,
                failed_refresh_count=previous.failed_refresh_count + 1,
            )
            self._status = current
        notifications = self._notifications("status", current)
        if not background:
            self._logger.debug("Feature flag refresh failed. %s", describe_error(error))
            return notifications
        if not _policy.is_unauthorized(error):
            # A 401 is logged once polling stops; see _record_polling_stopped.
            level = logging.ERROR if _status_code(error) == 403 else logging.WARNING
            self._logger.log(
                level,
                "Feature flag refresh failed; keeping the last good flags and retrying. %s",
                describe_error(error),
            )
        return notifications + self._notifications("error", error)

    def _record_polling_stopped(self, error: Exception) -> list[Notification]:
        with self._status_lock:
            current = replace(self._status, polling_stopped=True)
            self._status = current
        self._logger.error(
            "Feature flag polling stopped after a 401; keeping the last good flags. "
            "Create a new runtime client with a valid API key to resume. %s",
            describe_error(error),
        )
        return self._notifications("status", current)

    def _parse(self, payload: object) -> FeatureFlagsConfiguration:
        # The transport returns None for a body that is not JSON; the
        # configuration rejects that like any other payload it can't read.
        try:
            return configuration_for(payload, self._status.configuration)
        except FeatureFlagsConfigurationError as error:
            raise FeatureFlagsConfigurationError(
                "Feature flag poll returned a payload this SDK can't read; "
                f"keeping the last good flags. {error}"
            ) from error

    def _readiness_timeout(self, timeout: Optional[float]) -> TimeoutError:
        last_error = self._status.last_error
        message = f"Feature flags were not ready within {timeout} seconds"
        if last_error is not None:
            message += f"; the last refresh failed: {describe_error(last_error)}"
        error = TimeoutError(message)
        error.__cause__ = last_error
        error.__suppress_context__ = True
        return error

    def _readiness_failure(self) -> Exception:
        """A new exception for each waiter, so no shared traceback keeps growing."""
        stored = self._readiness_error
        if stored is None:
            return RuntimeError(
                "The feature flags runtime client was closed before it became ready"
            )
        try:
            # Same type and attributes, with an empty traceback.
            error = copy.copy(stored)
        except Exception:
            error = RuntimeError(
                f"Feature flag polling stopped before it was ready: {describe_error(stored)}"
            )
        error.__cause__ = stored
        error.__suppress_context__ = True
        return error

    def _before_use(self) -> None:
        """Hook run before public calls; the sync client restarts polling after a fork."""

    def _used_before_fork(self) -> bool:
        """Whether this client sent requests, or was polling, in the parent."""
        return self._started or self._status.refresh_count > 0

    # --- Fork safety ----------------------------------------------------------

    def _after_fork_in_child(self) -> None:
        """What the at-fork hook runs in a forked child, which has only one thread."""
        # Recorded first, so a client that fails to rebuild isn't retried on use.
        self._pid = os.getpid()
        self._fork_claims = {}
        self._reinitialize_after_fork()

    def _reinitialize_if_forked(self) -> None:
        if self._pid != os.getpid():
            self._reinitialize_after_unhooked_fork()

    def _reinitialize_after_unhooked_fork(self) -> None:
        """Run the at-fork rebuild in a process forked without Python's fork hooks.

        uWSGI, for one, forks its workers that way unless told otherwise.
        Public calls check the process ID first and come here once it has
        changed, so a client is rebuilt on its first use in the new process,
        with the rules the at-fork hook applies. Any of this process's threads
        may get here, and possibly at once: the first claims the process and
        rebuilds the client, and the others wait for it.
        """
        pid = os.getpid()
        claim = threading.Event()
        claimed = self._fork_claims.setdefault(pid, claim)
        if claimed is not claim:
            claimed.wait()
            return
        try:
            # A thread that read the old process ID can claim the process after
            # another thread finished rebuilding the client.
            if self._pid != pid:
                self._reinitialize_after_fork()
        except Exception:
            self._logger.exception(
                "Could not prepare a feature flags runtime client for forked "
                "process %d",
                pid,
            )
        finally:
            self._pid = pid
            self._fork_claims.pop(pid, None)
            claim.set()

    def _reinitialize_after_fork(self) -> None:
        """Rebuild what a forked child can't use from the parent."""
        raise NotImplementedError

    def _reinitialize_core_after_fork(self) -> None:
        # The parent's other threads don't exist in the child, and any of them
        # may have held these locks.
        self._status_lock = threading.Lock()
        self._listeners_lock = threading.Lock()
        self._context_warnings.reinitialize_after_fork()
        self._pending.clear()

    def _log_listener_error(self) -> None:
        self._logger.exception("A feature flags runtime client listener raised")


def describe_error(error: BaseException) -> str:
    """A one-line description for logs, with the HTTP status of API errors."""
    if isinstance(error, APIError):
        parts = [type(error).__name__]
        if error.status_code is not None:
            parts.append(f"HTTP {error.status_code}")
        if error.message and error.message != "No message":
            parts.append(error.message)
        description = ": ".join(parts)
        return (
            f"{description} (request {error.request_id})"
            if error.request_id
            else description
        )
    message = str(error)
    return f"{type(error).__name__}: {message}" if message else type(error).__name__


def _status_code(error: Exception) -> Optional[int]:
    status_code = getattr(error, "status_code", None)
    return status_code if isinstance(status_code, int) else None


def _require_configuration(bootstrap: object) -> None:
    if bootstrap is not None and not isinstance(bootstrap, FeatureFlagsConfiguration):
        raise TypeError(
            "bootstrap must be a FeatureFlagsConfiguration; parse cached JSON with "
            "FeatureFlagsConfiguration.from_json()"
        )
