"""Memory models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class MemorySummary:
    """Selected process or system memory metrics."""

    total_kib: int | None = None
    free_kib: int | None = None
    available_kib: int | None = None
    cached_kib: int | None = None
    active_kib: int | None = None
    inactive_kib: int | None = None
