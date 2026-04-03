# @oagen-ignore-file
# This file is hand-maintained. Public client factory for PKCE-only /
# public-client usage (browser, mobile, CLI, desktop applications).

from __future__ import annotations

from typing import Optional


def create_public_client(
    *,
    client_id: str,
    base_url: Optional[str] = None,
    request_timeout: Optional[int] = None,
) -> "WorkOS":
    """Create a WorkOS client configured for public/PKCE-only usage.

    For browser, mobile, CLI, and desktop applications that cannot securely
    store an API key. Methods that require an API key will not include
    authorization headers.

    Args:
        client_id: The WorkOS client ID.
        base_url: Override the base URL. Defaults to ``https://api.workos.com``.
        request_timeout: HTTP request timeout in seconds.

    Returns:
        A WorkOS client instance with only ``client_id`` configured.
    """
    from ._client import WorkOS

    return WorkOS(
        client_id=client_id,
        base_url=base_url,
        request_timeout=request_timeout,
    )
