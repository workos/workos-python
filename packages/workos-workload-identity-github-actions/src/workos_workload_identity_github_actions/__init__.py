# @oagen-ignore-file

"""GitHub Actions identity token provider for WorkOS workload identity federation.

``github_actions(audience)`` returns a callable that asks the GitHub Actions
OIDC endpoint for a JWT issued for that audience. Pass it to
``workos.WorkloadIdentityCredentials(identity_token_provider=...)``.

The provider keeps no cache and does no retries; the WorkOS SDK retries the
call as part of the token exchange.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from email.message import Message
from typing import IO, Callable

__all__ = ["GitHubActionsProviderError", "github_actions"]

_TIMEOUT_SECONDS = 10.0
_URL_ENV = "ACTIONS_ID_TOKEN_REQUEST_URL"
_TOKEN_ENV = "ACTIONS_ID_TOKEN_REQUEST_TOKEN"
_MISSING_ENV_MESSAGE = (
    "GitHub Actions did not provide an OIDC token endpoint. "
    "Add `permissions: id-token: write` to the workflow or job."
)


class GitHubActionsProviderError(Exception):
    """The GitHub Actions OIDC token could not be fetched."""


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
    parts = urllib.parse.urlsplit(url)
    if parts.scheme not in ("http", "https"):
        raise GitHubActionsProviderError(f"{_URL_ENV} must be an http or https URL.")
    encoded = "audience=" + urllib.parse.quote(audience, safe="")
    query = f"{parts.query}&{encoded}" if parts.query else encoded
    return urllib.parse.urlunsplit(parts._replace(query=query))


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

        request = urllib.request.Request(
            _with_audience(url, audience),
            headers={
                "Authorization": f"Bearer {request_token}",
                "Accept": "application/json",
            },
            method="GET",
        )
        try:
            with _OPENER.open(request, timeout=_TIMEOUT_SECONDS) as response:
                status: int = response.status
                body: bytes = response.read()
        except urllib.error.HTTPError as exc:
            exc.close()
            raise GitHubActionsProviderError(
                f"GitHub Actions OIDC token request failed with status {exc.code}."
            ) from None
        except OSError as exc:
            raise GitHubActionsProviderError(
                f"GitHub Actions OIDC token request failed: {type(exc).__name__}."
            ) from None
        if status != 200:
            raise GitHubActionsProviderError(
                f"GitHub Actions OIDC token request failed with status {status}."
            )

        try:
            payload = json.loads(body)
        except ValueError:
            payload = None
        value = payload.get("value") if isinstance(payload, dict) else None  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
        if not isinstance(value, str) or not value:
            raise GitHubActionsProviderError(
                "GitHub Actions OIDC token response had no token value."
            )
        return value

    return provider
