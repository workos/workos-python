# @oagen-ignore-file
# This file is hand-maintained. It holds the polling and retry policy shared
# by the sync and async feature flags runtime clients.
# pyright: strict

from __future__ import annotations

import math
import random

from ..._base_client import RETRY_STATUS_CODES
from ..._errors import (
    APIError,
    RateLimitExceededError,
    WorkOSConnectionError,
    WorkOSError,
    WorkOSTimeoutError,
)
from ..._http import TransportError

# Matches the Node and .NET runtime clients.
DEFAULT_POLLING_INTERVAL = 30.0
MINIMUM_POLLING_INTERVAL = 5.0
DEFAULT_REQUEST_TIMEOUT = 10.0
DEFAULT_MAX_RETRY_DELAY = 60.0
MINIMUM_DELAY = 1.0
INITIAL_RETRY_DELAY = 1.0
JITTER_FACTOR = 0.1
MAX_COUNTED_FAILURES = 20

# Retries inside one refresh: at most the client's `max_retries`, like the
# Node SDK's transport retries, and always within the refresh's request timeout.
_ATTEMPT_RETRY_BASE = 0.5
# A retry is only worth sending with at least this much of the budget left
# for the request itself.
MINIMUM_ATTEMPT_TIME = 0.5
# Matches the Node SDK's MAXIMUM_RETRY_AFTER_TIME_IN_MILLISECONDS.
MAXIMUM_RETRY_AFTER = 60.0
_ATTEMPT_RETRY_MULTIPLIER = 1.5

POLL_PATH = ("sdk", "feature-flags")
POLL_PARAMS = {"payload_version": "2"}


def validate_duration(value: object, name: str) -> float:
    """Reject durations a timer cannot honor."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number of seconds")
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a positive, finite number of seconds")
    return float(value)


def polling_interval(value: float) -> float:
    return max(MINIMUM_POLLING_INTERVAL, validate_duration(value, "polling_interval"))


def next_delay(interval: float, failures: int, max_retry_delay: float) -> float:
    """Seconds until the next poll.

    Failures back off exponentially from one second up to ``max_retry_delay``,
    but never poll sooner than the polling interval. A ten percent jitter in
    either direction spreads polls from many processes, with a one second floor.
    """
    base = interval
    if failures > 0:
        exponent = min(failures, MAX_COUNTED_FAILURES) - 1
        base = max(base, min(INITIAL_RETRY_DELAY * 2**exponent, max_retry_delay))
    jitter = 1 + (random.random() * 2 - 1) * JITTER_FACTOR
    return max(MINIMUM_DELAY, base * jitter)


def is_unauthorized(error: BaseException) -> bool:
    """A 401 stops polling: the API key is invalid and retrying cannot help."""
    return isinstance(error, APIError) and error.status_code == 401


def attempt_retry_delay(
    error: BaseException, attempt: int, remaining: float, max_retries: int
) -> float | None:
    """Seconds to wait before retrying a failed request inside one refresh.

    ``None`` means give up and fail the refresh with ``error``: it is not
    transient, ``max_retries`` retries were already made, or the wait would not
    leave ``MINIMUM_ATTEMPT_TIME`` of the budget for the retry itself. A retry
    sent with almost no time left would only time out and hide the server's
    real error.
    """
    if attempt >= max_retries or not _is_transient(error):
        return None
    requested = retry_after(error)
    if requested is not None:
        delay = requested
    else:
        delay = (
            _ATTEMPT_RETRY_BASE
            * _ATTEMPT_RETRY_MULTIPLIER**attempt
            * (0.5 + random.random())
        )
    return delay if delay + MINIMUM_ATTEMPT_TIME <= remaining else None


def retry_after(error: BaseException) -> float | None:
    """The wait a 429 asked for, capped at ``MAXIMUM_RETRY_AFTER`` seconds.

    A retry inside a refresh waits this long. A refresh that could not honor it
    within its budget fails; the next poll then waits at least this long.
    """
    if isinstance(error, RateLimitExceededError) and error.retry_after is not None:
        return min(max(error.retry_after, 0.0), MAXIMUM_RETRY_AFTER)
    return None


def _is_transient(error: BaseException) -> bool:
    if isinstance(error, APIError):
        return error.status_code in RETRY_STATUS_CODES
    if isinstance(error, (WorkOSTimeoutError, WorkOSConnectionError)):
        return True
    return isinstance(error, WorkOSError) and isinstance(
        error.__cause__, TransportError
    )
