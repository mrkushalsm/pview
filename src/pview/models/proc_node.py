"""Proc filesystem node abstraction."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class NodeType(Enum):
    """Classification of proc nodes."""

    DIRECTORY = "directory"
    FILE = "file"
    SYMLINK = "symlink"
    PROCESS = "process"
    THREAD = "thread"


@dataclass(frozen=True, slots=True)
class ProcNode:
    """A single node in the proc filesystem tree."""

    path: Path
    name: str
    node_type: NodeType
    pid: int | None = None
    process_name: str | None = None
    is_expandable: bool = False
    symlink_target: Path | None = None

    def display_label(self) -> str:
        """Return a human-readable label for the node."""
        if self.node_type == NodeType.PROCESS:
            return f"{self.name} ({self.process_name})" if self.process_name else self.name
        return self.name
