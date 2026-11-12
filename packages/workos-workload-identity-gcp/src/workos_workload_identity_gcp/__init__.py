# @oagen-ignore-file

"""GCP identity token provider for WorkOS workload identity federation.

``gcp_metadata(audience)`` returns a callable that asks the GCP metadata server
for the default service account's identity token for that audience. Pass it to
``workos.WorkloadIdentityCredentials(identity_token_provider=...)``.

The provider keeps no cache and does no retries; the WorkOS SDK retries the
call as part of the token exchange.
"""

from __future__ import annotations

import urllib.error
import urllib.parse
import urllib.request
from email.message import Message
from typing import IO, Callable

__all__ = ["GcpMetadataProviderError", "gcp_metadata"]

_TIMEOUT_SECONDS = 10.0
_IDENTITY_PATH = "/computeMetadata/v1/instance/service-accounts/default/identity"

# Tests point this at a local mock. It is not a public option and is never read
# from the environment.
_METADATA_BASE_URL = "http://metadata.google.internal"


class GcpMetadataProviderError(Exception):
    """The GCP metadata server did not return an identity token."""


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


def gcp_metadata(audience: str) -> Callable[[], str]:
    """Return a provider of GCP metadata-server identity tokens for ``audience``.

    The conventional audience is ``https://api.workos.com``.
    """
    if not audience:
        raise ValueError("audience is required")
    query = f"audience={urllib.parse.quote(audience, safe='')}&format=full"
    # The metadata server is link-local. The request never goes through a
    # proxy named in the environment, which could not reach it or would answer
    # with its own identity.
    opener = urllib.request.build_opener(_NoRedirect, urllib.request.ProxyHandler({}))

    def provider() -> str:
        request = urllib.request.Request(
            f"{_METADATA_BASE_URL}{_IDENTITY_PATH}?{query}",
            headers={"Metadata-Flavor": "Google"},
            method="GET",
        )
        try:
            with opener.open(request, timeout=_TIMEOUT_SECONDS) as response:
                status: int = response.status
                body: bytes = response.read()
        except urllib.error.HTTPError as exc:
            exc.close()
            raise GcpMetadataProviderError(
                f"GCP metadata identity request failed with status {exc.code}."
            ) from None
        except OSError as exc:
            raise GcpMetadataProviderError(
                f"GCP metadata identity request failed: {type(exc).__name__}."
            ) from None
        if status != 200:
            raise GcpMetadataProviderError(
                f"GCP metadata identity request failed with status {status}."
            )

        token = body.decode("utf-8", errors="replace").strip()
        if not token:
            raise GcpMetadataProviderError("GCP metadata identity response was empty.")
        return token

    return provider
