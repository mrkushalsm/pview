"""Background refresh helpers for live panels."""

from __future__ import annotations

from dataclasses import dataclass, field
from time import monotonic


@dataclass
class RefreshState:
    """Track refresh timing and pause state."""

    interval_seconds: float = 1.0
    paused: bool = False
    last_refresh_at: float = field(default_factory=monotonic)

    def should_refresh(self, now: float | None = None) -> bool:
        current = monotonic() if now is None else now
        return not self.paused and (current - self.last_refresh_at) >= self.interval_seconds

    def mark_refreshed(self, now: float | None = None) -> None:
        self.last_refresh_at = monotonic() if now is None else now
