# @oagen-ignore-file
# This file is hand-maintained. Public value types of the feature flags
# runtime client.
# pyright: strict

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from ._configuration import FeatureFlagsConfiguration


@dataclass(frozen=True, slots=True)
class FlagsChangedEvent:
    """A refresh installed a configuration that differs from the previous one."""

    previous: FeatureFlagsConfiguration | None
    """The snapshot this refresh replaced.

    ``None`` on a first load without bootstrap, and the bootstrap configuration
    on the first refresh after one.
    """
    current: FeatureFlagsConfiguration
    """The newly installed snapshot. Persist ``current.to_json()`` to bootstrap later."""
    changed_flags: frozenset[str]
    """Slugs that were added, removed or modified. Every slug on a first load.

    Empty when only fields outside the flags changed.
    """


@dataclass(frozen=True, slots=True)
class RuntimeStatus:
    """An immutable view of readiness and the most recent refresh result."""

    configuration: FeatureFlagsConfiguration | None = None
    """The last valid snapshot. Failed refreshes never replace it."""
    last_successful_refresh_at: datetime | None = None
    """When the last successful network refresh finished. ``None`` for bootstrap-only readiness."""
    last_refresh_attempt_at: datetime | None = None
    """When the most recent finished refresh started."""
    last_error: Exception | None = None
    """The most recent refresh failure, cleared by the next successful refresh."""
    refresh_count: int = 0
    """Refreshes that finished, successfully or not, whether polled or manual."""
    failed_refresh_count: int = 0
    """Finished refreshes that failed, including timeouts and unreadable payloads."""
    polling_stopped: bool = False
    """Background polling stopped after a 401.

    The last good snapshot stays usable but is never refreshed again. Fix the
    API key and create a new runtime client. Closing the client does not set
    this.
    """

    @property
    def ready(self) -> bool:
        """Whether a validated configuration is available for local evaluation."""
        return self.configuration is not None

    @property
    def flag_count(self) -> int:
        """Number of flags in the current snapshot."""
        return len(self.configuration) if self.configuration is not None else 0

    def cache_age(self) -> float | None:
        """Seconds since the last successful network refresh, or ``None`` if there was none."""
        if self.last_successful_refresh_at is None:
            return None
        return (
            datetime.now(timezone.utc) - self.last_successful_refresh_at
        ).total_seconds()
