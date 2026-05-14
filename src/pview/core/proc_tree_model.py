"""Dynamic procfs tree model with lazy loading."""

from __future__ import annotations

import asyncio
from pathlib import Path

from pview.core.proc_reader import ProcReader
from pview.models.proc_node import NodeType, ProcNode


class ProcTreeModel:
    """Builds and caches proc filesystem nodes on demand."""

    def __init__(self) -> None:
        self._reader = ProcReader()
        self._process_cache: dict[int, str] = {}

    async def get_children(self, parent_path: Path) -> list[ProcNode]:
        """Lazily enumerate children of a proc directory."""
        return await asyncio.to_thread(self._sync_get_children, parent_path)

    def _sync_get_children(self, parent_path: Path) -> list[ProcNode]:
        """Synchronous version for thread execution."""
        try:
            entries = sorted(parent_path.iterdir(), key=lambda p: (not p.is_dir(), p.name))
        except (OSError, PermissionError):
            return []

        nodes = []
        for entry in entries:
            node = self._classify_entry(entry, parent_path)
            if node is not None:
                nodes.append(node)
        return nodes

    def _classify_entry(self, entry: Path, parent_path: Path) -> ProcNode | None:
        """Classify a filesystem entry and create a node."""
        try:
            name = entry.name

            if entry.is_symlink():
                try:
                    target = entry.resolve()
                except (OSError, RuntimeError):
                    target = None
                return ProcNode(
                    path=entry,
                    name=name,
                    node_type=NodeType.SYMLINK,
                    symlink_target=target,
                    is_expandable=False,
                )

            if entry.is_dir():
                is_pid = name.isdigit() and parent_path == Path("/proc")
                if is_pid:
                    pid = int(name)
                    process_name = self._get_process_name(pid)
                    return ProcNode(
                        path=entry,
                        name=name,
                        node_type=NodeType.PROCESS,
                        pid=pid,
                        process_name=process_name,
                        is_expandable=True,
                    )
                else:
                    return ProcNode(
                        path=entry,
                        name=name,
                        node_type=NodeType.DIRECTORY,
                        is_expandable=True,
                    )
            else:
                return ProcNode(
                    path=entry,
                    name=name,
                    node_type=NodeType.FILE,
                    is_expandable=False,
                )

        except OSError:
            return None

    def _get_process_name(self, pid: int) -> str | None:
        """Fetch process name from /proc/[pid]/comm or status."""
        if pid in self._process_cache:
            return self._process_cache[pid]

        for candidate in [
            Path(f"/proc/{pid}/comm"),
            Path(f"/proc/{pid}/status"),
        ]:
            try:
                if candidate.name == "comm":
                    name = candidate.read_text(encoding="utf-8", errors="replace").strip()
                    if name:
                        self._process_cache[pid] = name
                        return name
                elif candidate.name == "status":
                    content = candidate.read_text(encoding="utf-8", errors="replace")
                    for line in content.splitlines():
                        if line.startswith("Name:"):
                            name = line.split(":", 1)[1].strip()
                            self._process_cache[pid] = name
                            return name
            except (FileNotFoundError, PermissionError):
                continue

        return None

    def get_root(self) -> ProcNode:
        """Get the /proc root node."""
        return ProcNode(
            path=Path("/proc"),
            name="/proc",
            node_type=NodeType.DIRECTORY,
            is_expandable=True,
        )
