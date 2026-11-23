# @oagen-ignore-file

"""GitHub Actions identity token provider for WorkOS workload identity federation.

``github_actions(audience)`` returns a callable that asks the GitHub Actions
OIDC endpoint for a JWT issued for that audience. Pass it to
``workos.WorkloadIdentityCredentials(identity_token_provider=...)``.

The provider keeps no cache and does no retries; the WorkOS SDK retries the
call as part of the token exchange.
"""

from __future__ import annotations

import http.client
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from email.message import Message
from typing import IO, Callable, Tuple

__all__ = ["GitHubActionsProviderError", "github_actions"]

_TIMEOUT_SECONDS = 10.0
_URL_ENV = "ACTIONS_ID_TOKEN_REQUEST_URL"
_TOKEN_ENV = "ACTIONS_ID_TOKEN_REQUEST_TOKEN"
_MISSING_ENV_MESSAGE = (
    "GitHub Actions did not provide an OIDC token endpoint. "
    "Add `permissions: id-token: write` to the workflow or job."
)
_INVALID_URL_MESSAGE = f"{_URL_ENV} is not a valid URL."
# For a value with a character outside visible ASCII. The value is not shown.
_UNUSABLE_TOKEN_MESSAGE = (
    f"{_TOKEN_ENV} contains a character that is not allowed in an HTTP header, "
    "such as a line break. GitHub Actions sets this variable; pass it to the "
    "program unchanged."
)
_UNUSABLE_URL_MESSAGE = (
    f"{_URL_ENV} contains a character that is not allowed in a URL, such as a "
    "space or a line break. GitHub Actions sets this variable; pass it to the "
    "program unchanged."
)


class GitHubActionsProviderError(Exception):
    """The GitHub Actions OIDC token could not be fetched."""


def _unreachable(exc: OSError, url: str) -> GitHubActionsProviderError:
    """The error for a request that got no HTTP response, with the cause in words."""
    # urllib wraps a failed connection in ``URLError`` and keeps the cause in
    # ``reason``. A timeout while waiting for the response arrives unwrapped.
    cause: object = exc.reason if isinstance(exc, urllib.error.URLError) else exc
    reason = str(cause).strip()
    if not reason:
        reason = (
            "timed out" if isinstance(cause, TimeoutError) else "unknown network error"
        )
    # Of the URL, only the host and port are shown: no user name, path or query.
    host = urllib.parse.urlsplit(url).netloc.rpartition("@")[2]
    at = f" at {host}" if host else ""
    return GitHubActionsProviderError(
        f"The GitHub Actions OIDC token endpoint{at} could not be reached: {reason}. "
        "This provider works only in a GitHub Actions job, which sets the "
        f"endpoint in {_URL_ENV}."
    )


def _require_visible_ascii(value: str, message: str) -> None:
    """Refuse a value that has a character outside visible ASCII (0x21 to 0x7E).

    Neither a URL nor a bearer token has such a character. The value is not
    repaired, and ``message`` shows no part of it.
    """
    if any(not "!" <= char <= "~" for char in value):
        raise GitHubActionsProviderError(message)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Turns every redirect into an ``HTTPError`` instead of following it."""

    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: IO[bytes],
        code: int,
        msg: str,
        headers: Message,
        newurl: str,
    ) -> None:
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def _with_audience(url: str, audience: str) -> str:
    """Append ``audience`` to the URL's query string, keeping what is there."""
    try:
        parts = urllib.parse.urlsplit(url)
    except ValueError:
        # For example, a bracket of an IPv6 address that is never closed.
        parts = None
    if parts is None:
        raise GitHubActionsProviderError(_INVALID_URL_MESSAGE)
    if parts.scheme not in ("http", "https"):
        raise GitHubActionsProviderError(f"{_URL_ENV} must be an http or https URL.")
    encoded = "audience=" + urllib.parse.quote(audience, safe="")
    query = f"{parts.query}&{encoded}" if parts.query else encoded
    return urllib.parse.urlunsplit(parts._replace(query=query))


def _get(url: str, request_token: str) -> Tuple[int, bytes]:
    """Send the token request and return the status and the body of the response.

    Every failure leaves as a ``GitHubActionsProviderError`` that shows nothing
    of the request token.
    """
    try:
        request = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {request_token}",
                "Accept": "application/json",
            },
            method="GET",
        )
        with _OPENER.open(request, timeout=_TIMEOUT_SECONDS) as response:
            status: int = response.status
            body: bytes = response.read()
            return status, body
    except urllib.error.HTTPError as exc:
        exc.close()
        raise GitHubActionsProviderError(
            f"GitHub Actions OIDC token request failed with status {exc.code}."
        ) from None
    except OSError as exc:
        raise _unreachable(exc, url) from None
    except http.client.InvalidURL:
        message = _INVALID_URL_MESSAGE
    except http.client.HTTPException:
        message = "GitHub Actions OIDC token response was not valid HTTP."
    except Exception as exc:
        message = (
            "GitHub Actions OIDC token request failed with an unexpected "
            f"{type(exc).__name__}. Check {_URL_ENV} and {_TOKEN_ENV}."
        )
    # The text of these three kinds of error can quote the request token, the
    # URL or what the server sent, so none of it is shown. The error is raised
    # here, outside the handlers, so that the one that was caught is not kept
    # as its context either.
    raise GitHubActionsProviderError(message) from None


def github_actions(audience: str) -> Callable[[], str]:
    """Return a provider of GitHub Actions OIDC tokens for ``audience``.

    The job needs ``permissions: id-token: write``. The conventional audience
    is ``https://api.workos.com``.
    """
    if not audience:
        raise ValueError("audience is required")

    def provider() -> str:
        # Both variables are read on every call; the runner may rotate them.
        url = os.environ.get(_URL_ENV, "")
        request_token = os.environ.get(_TOKEN_ENV, "")
        if not url or not request_token:
            raise GitHubActionsProviderError(_MISSING_ENV_MESSAGE)
        # Checked before a request is built. urllib would drop a line break
        # from the URL, and would quote the request token in its own error.
        _require_visible_ascii(request_token, _UNUSABLE_TOKEN_MESSAGE)
        _require_visible_ascii(url, _UNUSABLE_URL_MESSAGE)

        status, body = _get(_with_audience(url, audience), request_token)
        if status != 200:
            raise GitHubActionsProviderError(
                f"GitHub Actions OIDC token request failed with status {status}."
            )

        try:
            payload = json.loads(body)
        except (ValueError, RecursionError):
            payload = None
        value = payload.get("value") if isinstance(payload, dict) else None  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
        if not isinstance(value, str) or not value:
            raise GitHubActionsProviderError(
                "GitHub Actions OIDC token response had no token value."
            )
        return value

    return provider
