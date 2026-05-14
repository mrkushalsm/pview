"""Safe procfs file reading helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Optional


@dataclass(frozen=True)
class ProcReadResult:
    """Result of reading a proc entry."""

    path: Path
    content: str | None
    error: str | None = None


class ProcReader:
    """Read procfs paths defensively."""

    def __init__(self) -> None:
        self.sudo = SudoManager()

    def read_text(self, path: Path) -> ProcReadResult:
        try:
            return ProcReadResult(path=path, content=path.read_text(encoding="utf-8", errors="replace"))
        except FileNotFoundError:
            return ProcReadResult(path=path, content=None, error="entry disappeared")
        except PermissionError:
            # Try a non-interactive sudo read first
            try:
                content = self.sudo.sudo_cat(path)
                return ProcReadResult(path=path, content=content)
            except PermissionError:
                return ProcReadResult(path=path, content=None, error="permission denied")
        except OSError as exc:
            return ProcReadResult(path=path, content=None, error=str(exc))

    def read_link(self, path: Path) -> ProcReadResult:
        try:
            return ProcReadResult(path=path, content=str(path.readlink()))
        except FileNotFoundError:
            return ProcReadResult(path=path, content=None, error="entry disappeared")
        except PermissionError:
            # Try reading link via sudo-aware helper
            try:
                # reading a symlink target via sudo: readlink requires privileged reads in some cases
                content = self.sudo.sudo_readlink(path)
                return ProcReadResult(path=path, content=content)
            except PermissionError:
                return ProcReadResult(path=path, content=None, error="permission denied")
        except OSError as exc:
            return ProcReadResult(path=path, content=None, error=str(exc))


class SudoManager:
    """Manage simple sudo-backed reads with cached password for the session.

    Password is cached in-memory and persists for the entire pview session.
    It is cleared only when the app exits.
    """

    def __init__(self) -> None:
        self._password: Optional[str] = None

    def _has_cached(self) -> bool:
        return self._password is not None

    def can_sudo_noninteractive(self) -> bool:
        try:
            subprocess.run(["sudo", "-n", "true"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False

    def cache_password(self, password: str) -> bool:
        """Verify and cache the provided password. Returns True on success."""
        try:
            p = subprocess.run(["sudo", "-S", "-k", "true"], input=(password + "\n").encode(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if p.returncode == 0:
                self._password = password
                return True
            return False
        except Exception:
            return False

    def sudo_cat(self, path: Path) -> str:
        # Try non-interactive sudo first
        if self.can_sudo_noninteractive():
            proc = subprocess.run(["sudo", "cat", str(path)], capture_output=True)
            if proc.returncode == 0:
                return proc.stdout.decode(errors="replace")
            raise PermissionError("sudo failed")

        # Use cached password if available
        if self._has_cached():
            proc = subprocess.run(["sudo", "-S", "cat", str(path)], input=(self._password + "\n").encode(), capture_output=True)
            if proc.returncode == 0:
                return proc.stdout.decode(errors="replace")
            raise PermissionError("sudo failed with cached password")

        raise PermissionError("no sudo available")

    def sudo_readlink(self, path: Path) -> str:
        # readlink via sudo: use `readlink -f` to get canonical target
        if self.can_sudo_noninteractive():
            proc = subprocess.run(["sudo", "readlink", "-f", str(path)], capture_output=True)
            if proc.returncode == 0:
                return proc.stdout.decode(errors="replace").strip()
            raise PermissionError("sudo readlink failed")

        if self._has_cached():
            proc = subprocess.run(["sudo", "-S", "readlink", "-f", str(path)], input=(self._password + "\n").encode(), capture_output=True)
            if proc.returncode == 0:
                return proc.stdout.decode(errors="replace").strip()
            raise PermissionError("sudo readlink failed with cached password")

        raise PermissionError("no sudo available")
