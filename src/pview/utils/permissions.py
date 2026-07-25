"""Permission and path helpers."""

from __future__ import annotations

from pathlib import Path


def is_proc_path(path: Path) -> bool:
    """Return True if path lives under /proc.

    Uses startswith on the resolved POSIX path to avoid false matches
    on directories like /home/proc/ or /var/someproc/.
    """
    parent = path if path.is_dir() else path.parent
    try:
        resolved = parent.resolve(strict=False)
    except (OSError, RuntimeError):
        return False
    return resolved == Path("/proc") or resolved.as_posix().startswith("/proc/")
