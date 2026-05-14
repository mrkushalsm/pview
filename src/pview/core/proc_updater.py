"""Live proc filesystem update engine."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from pathlib import Path


class ProcUpdater:
    """Watches for proc filesystem changes and triggers refreshes."""

    def __init__(self, check_interval: float = 2.0) -> None:
        self.check_interval = check_interval
        self._running = False
        self._last_pids: set[int] = set()
        self._callbacks: list[Callable[[], None]] = []

    def add_callback(self, callback: Callable[[], None]) -> None:
        """Register a callback to fire when processes appear/disappear."""
        self._callbacks.append(callback)

    async def start(self) -> None:
        """Start the watcher loop."""
        self._running = True
        while self._running:
            await self._check_for_changes()
            await asyncio.sleep(self.check_interval)

    async def stop(self) -> None:
        """Stop the watcher loop."""
        self._running = False

    async def _check_for_changes(self) -> None:
        """Check for PID changes and fire callbacks."""
        current_pids = await asyncio.to_thread(self._get_current_pids)
        if current_pids != self._last_pids:
            self._last_pids = current_pids
            for callback in self._callbacks:
                callback()

    def _get_current_pids(self) -> set[int]:
        """Get currently active PIDs."""
        try:
            return {int(d.name) for d in Path("/proc").iterdir() if d.name.isdigit()}
        except OSError:
            return set()
