# @oagen-ignore-file
# This file is hand-maintained. The credentials contract every WorkOS client
# authenticates through, and its static API key implementation.

"""How a WorkOS client gets the authorization headers for a request.

A client resolves a :class:`CredentialSnapshot` before every HTTP attempt. A
static API key is the trivial implementation; workload identity federation
(:mod:`workos.workload_identity`) is the other.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Mapping, Optional, Protocol


@dataclass(frozen=True)
class CredentialSnapshot:
    """The authorization headers for one HTTP attempt.

    Attributes:
        headers: Headers to set on the attempt. They hold a bearer token, so
            they are left out of ``repr()``.
        generation: Identifies the credential the headers came from. A 401
            invalidates this generation, never a newer one.
        recoverable: True when a 401 on this snapshot is worth one re-resolve.
    """

    headers: Mapping[str, str] = field(repr=False)
    generation: int
    recoverable: bool


class Credentials(Protocol):
    """Source of authorization headers for a WorkOS client.

    Pass an implementation as ``credentials=`` to :class:`workos.WorkOSClient`
    or :class:`workos.AsyncWorkOSClient`. The synchronous client calls
    :meth:`resolve`; the asynchronous client awaits :meth:`aresolve`.
    """

    def resolve(self, *, timeout: Optional[float] = None) -> CredentialSnapshot:
        """Return the headers for the next HTTP attempt.

        May block. ``timeout`` is how long, in seconds, the caller is prepared
        to wait.
        """
        ...

    async def aresolve(self, *, timeout: Optional[float] = None) -> CredentialSnapshot:
        """Asynchronous twin of :meth:`resolve`."""
        ...

    def invalidate(self, generation: int) -> None:
        """Discard the credential of ``generation`` after the API rejected it.

        Never blocks on the network. Does nothing when a newer generation is
        already current.
        """
        ...


class StaticKeyCredentials:
    """Credentials for a static API key: one snapshot that never changes."""

    def __init__(self, api_key: Optional[str]) -> None:
        headers: Dict[str, str] = (
            {"Authorization": f"Bearer {api_key}"} if api_key else {}
        )
        self._snapshot = CredentialSnapshot(
            headers=headers, generation=0, recoverable=False
        )

    def resolve(self, *, timeout: Optional[float] = None) -> CredentialSnapshot:
        return self._snapshot

    async def aresolve(self, *, timeout: Optional[float] = None) -> CredentialSnapshot:
        return self._snapshot

    def invalidate(self, generation: int) -> None:
        return None


# Used for a request whose own ``Authorization`` header overrides a static API
# key: nothing to add, nothing to recover.
NO_CREDENTIALS = StaticKeyCredentials(None)


def apply_snapshot(
    headers: Dict[str, str], snapshot: CredentialSnapshot
) -> Dict[str, str]:
    """Return ``headers`` with the snapshot's headers set on top.

    A snapshot header replaces a header of the same name whatever its case, so
    a request never carries two ``Authorization`` headers. A header that is
    already spelled the same way keeps its position.
    """
    if not snapshot.headers:
        return headers
    merged = dict(headers)
    for name, value in snapshot.headers.items():
        lowered = name.lower()
        for existing in [key for key in merged if key.lower() == lowered]:
            if existing != name:
                del merged[existing]
        merged[name] = value
    return merged
