# @oagen-ignore-file
# This file is hand-maintained. Workload identity federation: a workload
# exchanges a JWT issued by its platform for a short-lived WorkOS access token,
# so it needs no stored API key.

"""Workload identity federation (WIF) credentials for the WorkOS client.

Build a :class:`WorkloadIdentityCredentials` and pass it as ``credentials=`` to
:class:`workos.WorkOSClient` or :class:`workos.AsyncWorkOSClient`::

    from workos import WorkOSClient, WorkloadIdentityCredentials, token_file

    client = WorkOSClient(
        credentials=WorkloadIdentityCredentials(
            client_id="client_...",
            token_url="https://.../oauth2/token",
            environment_id="environment_...",
            identity_token_provider=token_file("/run/workos/identity-token"),
        )
    )

The identity token provider is any callable that returns the workload's JWT.
:func:`token_file` and :func:`token_env` are built in; the GitHub Actions, GCP
and AWS providers are separate distributions.

The token URL must be an absolute ``https`` URL. Any other URL fails when the
credentials are built.
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import inspect
import math
import os
import threading
import time
import traceback
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    Protocol,
    Tuple,
    Union,
    cast,
)
from urllib.parse import urlencode

import httpx2

from ._base_client import MAX_RETRIES, _BaseWorkOSClient, _user_agent
from ._credentials import CredentialSnapshot
from ._errors import WorkOSError, WorkOSTimeoutError
from ._http import (
    HTTPResponse,
    HttpxBackend,
    TransportError,
    TransportTimeout,
)

__all__ = [
    "ENVIRONMENT_ID_HEADER",
    "IdentityTokenProvider",
    "WorkloadIdentityCredentials",
    "WorkloadIdentityError",
    "token_env",
    "token_file",
]

# --- constants ------------------------------------------------------------------

# Sent on API requests made with workload identity credentials that have an
# environment ID. Left off when they have none.
ENVIRONMENT_ID_HEADER = "x-url-environment-id"
GRANT_TYPE = "urn:ietf:params:oauth:grant-type:jwt-bearer"
DEFAULT_RESOURCE = "https://api.workos.com"
# A token is refreshed once less than min(60 seconds, 20% of its lifetime) is left.
REFRESH_THRESHOLD_SECONDS = 60.0
REFRESH_THRESHOLD_FRACTION = 0.2
# Used when the token response has no usable ``expires_in``.
DEFAULT_LIFETIME_SECONDS = 300.0
# The whole exchange, including retries and backoff.
EXCHANGE_DEADLINE_SECONDS = 30.0
DESCRIPTION_LIMIT = 500

# The only environment variable the credentials read.
_CLIENT_ID_ENV = "WORKOS_CLIENT_ID"

# How long past its deadline a synchronous exchange may run before a waiter
# gives it up for lost. See WorkloadIdentityCredentials._wait.
_DEADLINE_GRACE_SECONDS = 1.0
_DEADLINE_DESCRIPTION = (
    f"The exchange did not finish within {EXCHANGE_DEADLINE_SECONDS:g} seconds."
)
_ASYNC_PROVIDER_MESSAGE = (
    "The identity token provider is asynchronous. Use it with "
    "AsyncWorkOSClient, or pass a synchronous provider."
)
_PROVIDER_TIMEOUT_MESSAGE = (
    "The identity token provider did not return before the exchange's deadline."
)
_WAIT_TIMEOUT_MESSAGE = "Timed out waiting for the workload identity token exchange."

# --- errors ---------------------------------------------------------------------

# One sentence per error code. The wording is pending the server's final error
# codes; keep every hint in this table so a change is made in one place.
_HINTS: Dict[str, str] = {
    # OAuth error codes from the token endpoint.
    "invalid_grant": (
        "The identity token was not accepted. Check its issuer, audience and "
        "subject claims against the trust rule, and that it has not expired. "
        "A token that was already exchanged is also refused: each exchange "
        "needs a new identity token."
    ),
    "invalid_target": (
        "The resource is not one the token endpoint accepts. Leave the "
        "resource unset to use the default, https://api.workos.com."
    ),
    "invalid_client": (
        "The client ID is unknown, or the application has no enabled trust "
        "rule. Check that the client ID is the M2M application that has the "
        "trust rule."
    ),
    "unauthorized_client": (
        "This application cannot use workload identity federation. Check that "
        "the feature is enabled for your team and that the application is "
        "bound to a non-production environment."
    ),
    "invalid_scope": (
        "The requested scope is not allowed for this application. Fix the "
        "scope or leave it unset."
    ),
    "invalid_request": (
        "The token request was malformed. Check that the token URL points at "
        "the `/oauth2/token` endpoint."
    ),
    # Codes the SDK sets for failures that have no OAuth code.
    "exchange_failed": (
        "The token endpoint could not be reached or kept failing. Check the "
        "token URL and try again."
    ),
    "invalid_response": (
        "The token endpoint returned a response the SDK could not read. Check "
        "that the token URL points at the `/oauth2/token` endpoint."
    ),
    "provider_failed": (
        "The identity token provider failed, so there was no token to exchange."
    ),
    "invalid_configuration": (
        "Workload identity credentials are missing a required setting."
    ),
}
_OTHER_OAUTH_HINT = "The token endpoint rejected the exchange."


class WorkloadIdentityError(WorkOSError):
    """A workload identity token could not be obtained.

    Attributes:
        code: The OAuth error code from the token endpoint, or one of the SDK's
            own codes: ``exchange_failed``, ``invalid_response``,
            ``provider_failed``, ``invalid_configuration``.
        description: The server's ``error_description`` (at most 500
            characters), or detail from the SDK. May be empty.
        hint: One sentence on what to check. Never empty.

    The message is ``<code>: <hint>``, followed by the description when there
    is one. It never contains the identity token or the access token.
    """

    code: str
    description: str
    hint: str

    def __init__(self, code: str, description: str = "") -> None:
        self.code = code
        self.description = description[:DESCRIPTION_LIMIT]
        self.hint = _HINTS.get(code, _OTHER_OAUTH_HINT)
        message = f"{code}: {self.hint}"
        if self.description:
            message = f"{message} {self.description}"
        super().__init__(message)


# --- providers ------------------------------------------------------------------


class IdentityTokenProvider(Protocol):
    """A callable that returns the workload's JWT.

    Called once per exchange attempt; it may return the same token each time.
    A plain function may block: it runs on the exchange's own thread, never on
    an event loop. A coroutine function is awaited on the event loop of the
    asynchronous client that started the exchange (asynchronous client only).
    """

    def __call__(self) -> Union[str, Awaitable[str]]: ...


def token_file(path: Union[str, "os.PathLike[str]"]) -> IdentityTokenProvider:
    """Return a provider that reads the identity token from a file.

    The file is read on every exchange, so a rotated token is picked up, and
    surrounding whitespace is trimmed. A missing or empty file is an error.
    """

    def provider() -> str:
        with open(path, "r", encoding="utf-8") as handle:
            token = handle.read().strip()
        if not token:
            raise ValueError(f"The identity token file is empty: {os.fspath(path)}")
        return token

    return provider


def token_env(name: str) -> IdentityTokenProvider:
    """Return a provider that reads the identity token from an environment variable.

    The variable is read on every exchange. An unset or empty variable is an
    error.
    """

    def provider() -> str:
        token = os.environ.get(name, "")
        if not token:
            raise ValueError(f"The environment variable {name} is unset or empty.")
        return token

    return provider


class _AsyncProviderInSyncClient(Exception):
    """A provider returned an awaitable where there is no event loop to await it."""


def _is_coroutine_callable(provider: object) -> bool:
    return inspect.iscoroutinefunction(provider) or inspect.iscoroutinefunction(
        getattr(provider, "__call__", None)
    )


def _await_on(
    loop: asyncio.AbstractEventLoop, awaitable: Awaitable[object], timeout: float
) -> object:
    """Await ``awaitable`` on ``loop`` from another thread, for at most ``timeout`` seconds."""

    async def relay() -> object:
        return await awaitable

    coroutine = relay()
    try:
        future = asyncio.run_coroutine_threadsafe(coroutine, loop)
    except RuntimeError:
        # The loop has closed, so nothing will ever await these two.
        coroutine.close()
        if inspect.iscoroutine(awaitable):
            awaitable.close()
        raise
    try:
        return future.result(timeout)
    except concurrent.futures.TimeoutError:
        future.cancel()
        raise TimeoutError(_PROVIDER_TIMEOUT_MESSAGE) from None


def _require_token(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError(
            f"The identity token provider returned {type(value).__name__}, not a string."
        )
    if not value:
        raise ValueError("The identity token provider returned an empty token.")
    return value


# --- exchange -------------------------------------------------------------------


def _redact(text: str, secret: str) -> str:
    return text.replace(secret, "[redacted]") if secret else text


def _clear_frames(error: BaseException) -> None:
    """Empty the local variables of every frame the tracebacks of ``error`` hold.

    A traceback keeps the frames it passed through, and the frames of an
    exchange hold the assertion and what the server answered. Anything that
    records the local variables of a traceback, such as an error reporter,
    would find them there. The frames and their line numbers stay.
    """
    seen: List[BaseException] = []
    current: Optional[BaseException] = error
    while current is not None and current not in seen:
        seen.append(current)
        traceback.clear_frames(current.__traceback__)
        current = current.__cause__ or current.__context__


def _lifetime(expires_in: object) -> float:
    """``expires_in`` in seconds, or the default when absent, not a number or not positive."""
    if isinstance(expires_in, bool) or not isinstance(expires_in, (int, float)):
        return DEFAULT_LIFETIME_SECONDS
    lifetime = float(expires_in)
    if not math.isfinite(lifetime) or lifetime <= 0:
        return DEFAULT_LIFETIME_SECONDS
    return lifetime


def _json_object(response: HTTPResponse) -> Optional[Dict[str, Any]]:
    try:
        data = response.json()
    except (ValueError, RecursionError):
        return None
    return cast(Dict[str, Any], data) if isinstance(data, dict) else None


def _unreachable(error: TransportError, token_url: str) -> str:
    """The description of a request that got no HTTP response: the host and the reason.

    The reason is the HTTP client's own text for the failure, which is mostly
    the operating system's, such as ``[Errno 111] Connection refused``. It is
    never empty and never a class name. Of the token URL, only the host and
    port are shown.
    """
    if isinstance(error.__cause__, httpx2.RemoteProtocolError):
        # Its text can quote what the server sent, which may hold a token.
        reason = "the server did not send a valid HTTP response"
    else:
        reason = str(error).strip()
    if not reason:
        # Some timeouts arrive with no text.
        reason = (
            "timed out"
            if isinstance(error, TransportTimeout)
            else "unknown network error"
        )
    host = httpx2.URL(token_url).netloc.decode("ascii")
    return f"The request to the token endpoint at {host} failed: {reason}."


def _exchange_headers() -> Dict[str, str]:
    # No Authorization header: the exchange carries no client secret and no API key.
    return {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "User-Agent": _user_agent(),
    }


class _ExchangeRun:
    """State of one exchange across its attempts, shared by the sync and async loops."""

    def __init__(self, deadline: float) -> None:
        self._deadline = deadline
        self._code = "exchange_failed"
        self._description = ""
        self._cause: Optional[BaseException] = None
        self._retry_after: Optional[str] = None

    def remaining(self) -> float:
        """Seconds left before the deadline. Raises when there are none."""
        remaining = self._deadline - time.monotonic()
        if remaining <= 0:
            raise WorkloadIdentityError("exchange_failed", _DEADLINE_DESCRIPTION)
        return remaining

    def time_left(self) -> float:
        """Seconds left before the deadline, or zero when it has passed."""
        return max(self._deadline - time.monotonic(), 0.0)

    def attempt_timeout(self, attempt: int) -> float:
        """The HTTP timeout for ``attempt``: an even share of the time left.

        One attempt given the whole deadline would leave nothing to retry a
        timeout with.
        """
        return self.remaining() / (MAX_RETRIES + 1 - attempt)

    def backoff(self, attempt: int) -> float:
        """Seconds to sleep before ``attempt``, from the SDK's own retry policy."""
        delay = _BaseWorkOSClient._calculate_retry_delay(attempt - 1, self._retry_after)
        self._retry_after = None
        if delay >= self._deadline - time.monotonic():
            # The next attempt could not start in time; report the last failure.
            raise self.exhausted()
        return delay

    def provider_failed(self, error: Exception) -> None:
        self._code = "provider_failed"
        self._description = str(error) or type(error).__name__
        self._cause = error

    def transport_failed(
        self, error: TransportError, token_url: str, assertion: str
    ) -> None:
        # The reason in words, and no cause: the error's request holds the assertion.
        self._code = "exchange_failed"
        self._description = _redact(_unreachable(error, token_url), assertion)
        self._cause = None

    def exhausted(self) -> WorkloadIdentityError:
        """The error for an exchange whose every attempt failed."""
        error = WorkloadIdentityError(self._code, self._description)
        error.__cause__ = self._cause
        return error

    def read(
        self, response: HTTPResponse, assertion: str
    ) -> Optional[Tuple[str, float]]:
        """Return ``(access_token, lifetime)``, or None to retry. Raises when terminal.

        The status is checked before the body: a 429 or 5xx is retried even when
        its body carries an OAuth error; an OAuth error on any other status is
        terminal.
        """
        status = response.status_code
        body = _json_object(response)
        error = body.get("error") if body is not None else None
        oauth_code = (
            _redact(error, assertion) if isinstance(error, str) and error else ""
        )
        detail = body.get("error_description") if body is not None else None
        oauth_description = (
            _redact(detail, assertion) if isinstance(detail, str) else ""
        )

        if status == 429 or 500 <= status <= 599:
            self._code = oauth_code or "exchange_failed"
            self._description = (
                oauth_description or f"The token endpoint returned HTTP {status}."
            )
            self._cause = None
            self._retry_after = response.headers.get("Retry-After")
            return None
        if oauth_code:
            raise WorkloadIdentityError(oauth_code, oauth_description)
        if 300 <= status <= 399:
            raise WorkloadIdentityError(
                "exchange_failed",
                f"The token endpoint returned HTTP {status}; redirects are not followed.",
            )
        if status != 200:
            raise WorkloadIdentityError(
                "invalid_response", f"The token endpoint returned HTTP {status}."
            )
        if body is None:
            raise WorkloadIdentityError(
                "invalid_response", "The response body is not a JSON object."
            )
        access_token = body.get("access_token")
        if not isinstance(access_token, str) or not access_token:
            raise WorkloadIdentityError(
                "invalid_response", "The response has no access_token."
            )
        return access_token, _lifetime(body.get("expires_in"))


class _Exchange:
    """One in-flight exchange and its result, shared by every caller that waits for it.

    The exchange runs on a thread of its own, so it depends on no caller's
    thread and on no event loop. A synchronous caller blocks on ``done``. An
    asynchronous caller is woken on its own event loop through ``wakers``.
    """

    __slots__ = ("deadline", "done", "error", "loop", "result", "settled", "wakers")

    def __init__(
        self, deadline: float, loop: Optional[asyncio.AbstractEventLoop]
    ) -> None:
        self.deadline = deadline
        # The event loop of the asynchronous caller that started the exchange,
        # where an asynchronous provider is awaited. None when a synchronous
        # caller started it.
        self.loop = loop
        self.done = threading.Event()
        self.settled = False
        self.result: Optional[Tuple[str, int]] = None
        self.error: Optional[BaseException] = None
        # One per waiting coroutine. Each wakes its own event loop.
        self.wakers: List[Callable[[], None]] = []

    def outcome(self) -> Tuple[str, int]:
        if self.error is not None:
            raise self.error
        assert self.result is not None
        return self.result


# --- credentials ----------------------------------------------------------------


def _https_url(token_url: str) -> str:
    """``token_url`` unchanged, if it is an absolute https URL. Raises when it is not.

    https only, on every host: the POST carries the workload's identity token
    and the response carries the access token. Nothing relaxes this, for
    localhost or a loopback address either.

    The URL is parsed by httpx2, which also sends the exchange, so the check
    and the request read it the same way.
    """
    try:
        url = httpx2.URL(token_url)
    except (TypeError, httpx2.InvalidURL):
        url = None
    if url is None or url.scheme != "https" or not url.host:
        # The URL itself is left out of the error: it may hold credentials.
        raise WorkloadIdentityError(
            "invalid_configuration", "token_url must be an absolute https URL"
        )
    return token_url


class WorkloadIdentityCredentials:
    """Credentials that exchange a workload's JWT for a WorkOS access token.

    The access token is cached on this instance, in memory only, and refreshed
    on demand once less than ``min(60 seconds, 20% of its lifetime)`` remains.
    Concurrent callers share one exchange, whether they come from a
    synchronous client, an asynchronous one, or both. Two instances never
    share a token, even with identical settings.

    Settings are fixed at construction; build a new instance to change one. An
    omitted ``client_id`` falls back to ``WORKOS_CLIENT_ID``, the only
    environment variable the credentials read. No environment variable
    switches workload identity on.

    Args:
        identity_token_provider: A callable returning the workload's JWT, such
            as :func:`token_file`, :func:`token_env`, a platform provider, or
            your own function.
        client_id: The M2M application's client ID. Falls back to
            ``WORKOS_CLIENT_ID``.
        token_url: The token exchange endpoint. Required, and set only here:
            no environment variable is read for it and there is no built-in
            default. It must be an absolute ``https`` URL. The scheme is not
            case-sensitive. Any other URL is refused, ``http://localhost``
            included, because the request carries the identity token and the
            response carries the access token.
        environment_id: Optional, and set only here: no environment variable
            is read for it. When set, it is sent as the
            ``x-url-environment-id`` header on every API request; when not
            set (an empty string counts as not set), the header is not sent.
            The server binds a workload identity client to exactly one
            environment, so the header selects nothing. Setting it is a
            safety check: a value that names a different environment gets
            ``403 environment_mismatch``.
        resource: The ``resource`` to request a token for. Defaults to
            ``https://api.workos.com``.
        scope: The ``scope`` to request. Optional, and set only here: no
            environment variable is read for it. Left out of the request when
            not set or empty.

    Raises:
        WorkloadIdentityError: With code ``invalid_configuration`` when a
            required setting is missing; for ``client_id``, that is after
            ``WORKOS_CLIENT_ID`` is consulted. The same code is raised when
            ``token_url`` is not an absolute ``https`` URL.
    """

    def __init__(
        self,
        *,
        identity_token_provider: IdentityTokenProvider,
        client_id: Optional[str] = None,
        token_url: Optional[str] = None,
        environment_id: Optional[str] = None,
        resource: Optional[str] = None,
        scope: Optional[str] = None,
    ) -> None:
        if not callable(identity_token_provider):
            raise WorkloadIdentityError(
                "invalid_configuration",
                "identity_token_provider is required and must be callable",
            )
        self._provider = identity_token_provider
        # Only an asynchronous caller can start an exchange with such a provider.
        self._provider_is_async = _is_coroutine_callable(identity_token_provider)
        self._client_id = self._required("client_id", client_id, _CLIENT_ID_ENV)
        self._token_url = _https_url(self._required("token_url", token_url))
        self._environment_id = environment_id or None
        self._resource = resource or DEFAULT_RESOURCE
        self._scope = scope or None

        # The cache. Guarded by _lock, which is held only for these few fields
        # and never across I/O, so both the sync and the async path may take it.
        self._lock = threading.Lock()
        self._token: Optional[str] = None
        self._expires_at = -math.inf
        self._lifetime = 0.0
        self._generation = 0
        # The exchange in flight. Callers of both kinds of client wait for the
        # same one, whichever kind started it.
        self._inflight: Optional[_Exchange] = None

        # Seams for tests: the clock that decides freshness, and the sleep
        # between exchange attempts.
        self._clock: Callable[[], float] = time.monotonic
        self._sleep: Callable[[float], None] = time.sleep

    @staticmethod
    def _required(field: str, value: Optional[str], env: Optional[str] = None) -> str:
        """A required setting, from the argument or, when it has one, ``env``."""
        resolved = value or (os.environ.get(env) if env else None)
        if not resolved:
            description = f"{field} is required"
            if env:
                description = f"{description} (or set {env})"
            raise WorkloadIdentityError("invalid_configuration", description)
        return resolved

    @property
    def client_id(self) -> str:
        """The M2M application's client ID."""
        return self._client_id

    @property
    def token_url(self) -> str:
        """The token exchange endpoint, an absolute ``https`` URL."""
        return self._token_url

    @property
    def environment_id(self) -> Optional[str]:
        """The environment ID sent with every API request, or None when none is sent."""
        return self._environment_id

    @property
    def resource(self) -> str:
        """The resource a token is requested for."""
        return self._resource

    @property
    def scope(self) -> Optional[str]:
        """The scope requested, or None when no scope is sent."""
        return self._scope

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(client_id={self._client_id!r}, "
            f"token_url={self._token_url!r}, environment_id={self._environment_id!r})"
        )

    # --- the credentials contract ---

    def resolve(self, *, timeout: Optional[float] = None) -> CredentialSnapshot:
        """Return headers carrying a fresh access token, exchanging if needed.

        Blocks while an exchange runs, for at most ``timeout`` seconds. A caller
        that times out stops waiting; the exchange carries on for the others.

        Raises:
            WorkloadIdentityError: The exchange failed.
            WorkOSTimeoutError: ``timeout`` passed before the exchange finished.
        """
        with self._lock:
            current = self._fresh()
            exchange = None if current is not None else self._join_or_start(None)
        if exchange is not None:
            current = self._wait(exchange, timeout)
        assert current is not None
        return self._snapshot(*current)

    async def aresolve(self, *, timeout: Optional[float] = None) -> CredentialSnapshot:
        """Asynchronous twin of :meth:`resolve`.

        Canceling the awaiting task, or its ``timeout`` passing, stops that
        caller waiting. The shared exchange carries on for the others.
        """
        with self._lock:
            current = self._fresh()
            exchange = (
                None
                if current is not None
                else self._join_or_start(asyncio.get_running_loop())
            )
        if exchange is not None:
            current = await self._wait_async(exchange, timeout)
        assert current is not None
        return self._snapshot(*current)

    def invalidate(self, generation: int) -> None:
        """Discard the cached token if it is still the one of ``generation``.

        A late 401 for an old token leaves a newer token in place.
        """
        with self._lock:
            if self._generation == generation:
                self._expires_at = -math.inf

    # --- cache ---

    def _snapshot(self, token: str, generation: int) -> CredentialSnapshot:
        headers = {"Authorization": f"Bearer {token}"}
        if self._environment_id:
            headers[ENVIRONMENT_ID_HEADER] = self._environment_id
        return CredentialSnapshot(
            headers=headers,
            generation=generation,
            recoverable=True,
        )

    def _fresh(self) -> Optional[Tuple[str, int]]:
        """The cached token and its generation, if it is not due a refresh. Lock held."""
        if self._token is None:
            return None
        threshold = min(
            REFRESH_THRESHOLD_SECONDS, REFRESH_THRESHOLD_FRACTION * self._lifetime
        )
        if self._expires_at - self._clock() < threshold:
            return None
        return self._token, self._generation

    def _store(self, token: str, lifetime: float) -> int:
        """Cache a new token and return its generation. Lock held."""
        self._token = token
        self._lifetime = lifetime
        self._expires_at = self._clock() + lifetime
        self._generation += 1
        return self._generation

    # --- shared exchange ---

    def _join_or_start(self, loop: Optional[asyncio.AbstractEventLoop]) -> _Exchange:
        """The exchange in progress, started if there is none. Lock held.

        ``loop`` is the caller's event loop, or None for a synchronous caller.
        """
        if loop is None and self._provider_is_async:
            # Nothing can await the provider for this caller, and waiting for
            # an exchange that needs the caller's own thread to do so would
            # never end.
            raise WorkloadIdentityError("provider_failed", _ASYNC_PROVIDER_MESSAGE)
        exchange = self._inflight
        if exchange is None:
            exchange = _Exchange(time.monotonic() + EXCHANGE_DEADLINE_SECONDS, loop)
            self._inflight = exchange
            try:
                # Its own thread, not the first caller's thread or event loop:
                # a caller that gives up, or a loop that is blocked or closed,
                # must not take the exchange down with it.
                threading.Thread(
                    target=self._run_exchange,
                    args=(exchange,),
                    name="workos-workload-identity-exchange",
                    daemon=True,
                ).start()
            except BaseException:
                self._inflight = None
                raise
        return exchange

    def _run_exchange(self, exchange: _Exchange) -> None:
        try:
            token, lifetime = self._exchange(exchange.deadline, exchange.loop)
        except BaseException as error:
            _clear_frames(error)
            self._settle(exchange, error=error)
            return
        self._settle(exchange, token=token, lifetime=lifetime)

    def _settle(
        self,
        exchange: _Exchange,
        *,
        token: Optional[str] = None,
        lifetime: float = 0.0,
        error: Optional[BaseException] = None,
    ) -> None:
        """Record an exchange's outcome, clear it as in-flight, then wake its waiters.

        The in-flight slot is cleared before anyone is woken, so a caller that
        gets an error and calls again starts a new exchange. On success the
        token is stored under the same lock that clears the slot.

        Only the first outcome counts. An exchange that a waiter gave up at its
        deadline has failed, and a token it comes back with later is dropped:
        by then a newer exchange may have stored a token of its own.
        """
        with self._lock:
            if self._inflight is exchange:
                self._inflight = None
            if exchange.settled:
                return
            exchange.settled = True
            if token is not None:
                exchange.result = (token, self._store(token, lifetime))
            else:
                exchange.error = error
            # No waker is added once the exchange is settled.
            wakers = exchange.wakers
        exchange.done.set()
        for wake in wakers:
            wake()

    def _wait(self, exchange: _Exchange, timeout: Optional[float]) -> Tuple[str, int]:
        overdue_at = exchange.deadline + _DEADLINE_GRACE_SECONDS
        budget = overdue_at - time.monotonic()
        patience = budget if timeout is None else min(timeout, budget)
        if exchange.done.wait(max(patience, 0.0)):
            return exchange.outcome()
        if time.monotonic() < overdue_at:
            # This caller's own timeout. The exchange is left alone.
            raise WorkOSTimeoutError(_WAIT_TIMEOUT_MESSAGE)
        # The exchange outran its deadline, which only a provider that does not
        # return can cause: a thread cannot be interrupted. Give it up so the
        # next caller starts a new exchange instead of waiting on this one.
        self._settle(
            exchange,
            error=WorkloadIdentityError("exchange_failed", _DEADLINE_DESCRIPTION),
        )
        exchange.done.wait()
        return exchange.outcome()

    async def _wait_async(
        self, exchange: _Exchange, timeout: Optional[float]
    ) -> Tuple[str, int]:
        """Asynchronous twin of :meth:`_wait`. It never blocks the event loop."""
        loop = asyncio.get_running_loop()
        woken = asyncio.Event()

        def wake() -> None:
            # Called by whichever thread settles the exchange.
            try:
                loop.call_soon_threadsafe(woken.set)
            except RuntimeError:
                # This waiter's loop has closed. Nobody is waiting on it.
                pass

        with self._lock:
            if exchange.settled:
                return exchange.outcome()
            exchange.wakers.append(wake)
        overdue_at = exchange.deadline + _DEADLINE_GRACE_SECONDS
        budget = overdue_at - time.monotonic()
        patience = budget if timeout is None else min(timeout, budget)
        try:
            await asyncio.wait_for(woken.wait(), max(patience, 0.0))
        except asyncio.TimeoutError:
            if time.monotonic() < overdue_at:
                # This caller's own timeout. The exchange is left alone.
                raise WorkOSTimeoutError(_WAIT_TIMEOUT_MESSAGE) from None
            # As in _wait: given up, so the next caller starts a new exchange.
            self._settle(
                exchange,
                error=WorkloadIdentityError("exchange_failed", _DEADLINE_DESCRIPTION),
            )
        return exchange.outcome()

    # --- the exchange itself ---

    def _form(self, assertion: str) -> bytes:
        fields = {
            "grant_type": GRANT_TYPE,
            "assertion": assertion,
            "client_id": self._client_id,
            "resource": self._resource,
        }
        if self._scope:
            fields["scope"] = self._scope
        return urlencode(fields).encode("ascii")

    def _provide(
        self, loop: Optional[asyncio.AbstractEventLoop], run: _ExchangeRun
    ) -> str:
        """Call the provider on this thread, the exchange's own, and return its token.

        A plain callable may block (a file read, a cloud SDK call) without
        stalling an event loop. What an asynchronous provider returns is
        awaited on ``loop``, the event loop of the caller that started the
        exchange.
        """
        result = self._provider()
        if inspect.isawaitable(result):
            if loop is None:
                if inspect.iscoroutine(result):
                    result.close()
                raise _AsyncProviderInSyncClient(_ASYNC_PROVIDER_MESSAGE)
            result = _await_on(loop, result, run.time_left())
        return _require_token(result)

    def _exchange(
        self, deadline: float, loop: Optional[asyncio.AbstractEventLoop]
    ) -> Tuple[str, float]:
        """Exchange the identity token, retrying per the SDK's retry policy.

        Retried: a provider failure, a transport failure, HTTP 429 and 5xx. The
        provider is called again and the form rebuilt on every attempt.
        """
        run = _ExchangeRun(deadline)
        # A client of its own: redirects are never followed, and nothing a
        # caller installed on the API client (hooks, auth, logging) sees the
        # assertion or the token.
        with httpx2.Client(follow_redirects=False) as http:
            backend = HttpxBackend(http)
            for attempt in range(MAX_RETRIES + 1):
                if attempt > 0:
                    self._sleep(run.backoff(attempt))
                try:
                    assertion = self._provide(loop, run)
                except _AsyncProviderInSyncClient as error:
                    raise WorkloadIdentityError("provider_failed", str(error)) from None
                except Exception as error:
                    run.provider_failed(error)
                    continue
                try:
                    response = backend.request(
                        "POST",
                        self._token_url,
                        headers=_exchange_headers(),
                        content=self._form(assertion),
                        timeout=run.attempt_timeout(attempt),
                    )
                except TransportError as error:
                    run.transport_failed(error, self._token_url, assertion)
                    continue
                result = run.read(response, assertion)
                if result is not None:
                    return result
        raise run.exhausted()
