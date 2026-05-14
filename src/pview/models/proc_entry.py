"""Proc entry metadata used by the explorer tree and render pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ProcEntry:
    """A navigable procfs entry."""

    path: Path
    label: str
    description: str = ""
