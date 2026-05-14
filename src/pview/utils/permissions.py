"""Permission and path helpers."""

from __future__ import annotations

from pathlib import Path


def is_proc_path(path: Path) -> bool:
    """Return True for procfs paths."""

    return "/proc" in path.as_posix().split("/")
