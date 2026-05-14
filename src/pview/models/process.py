"""Process-related models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ProcessSummary:
    """Minimal process summary used by the explorer."""

    pid: int
    ppid: int | None = None
    command: str = ""
    state: str = ""
    cpu_percent: float | None = None
    memory_rss_kib: int | None = None
    children: list[int] = field(default_factory=list)
