"""Renderer for proc symlinks such as /proc/[pid]/ns/*, exe, cwd, root, and fd/*."""

from __future__ import annotations

from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class SymlinkRenderer:
    """Render proc symlink targets with context-aware explanations."""

    def can_render(self, path: Path) -> bool:
        return path.is_symlink() and "/proc/" in str(path)

    def render(self, path: Path, content: str | None) -> Panel:
        target = content.strip() if content else "<unavailable>"
        table = Table.grid(expand=True)
        table.add_column(style="cyan", width=22)
        table.add_column(overflow="fold")

        table.add_row("Link target", target)
        table.add_row("Entry", str(path))

        if "/ns/" in str(path):
            table.add_row("Kind", "Namespace handle")
            table.add_row("Meaning", "Same target inode means shared namespace")
        elif path.name in {"exe", "cwd", "root"}:
            meanings = {
                "exe": "Executable image for the process",
                "cwd": "Current working directory",
                "root": "Process root directory",
            }
            table.add_row("Kind", "Process path link")
            table.add_row("Meaning", meanings.get(path.name, "Process path link"))
        elif "/fd/" in str(path):
            table.add_row("Kind", "Open file descriptor")
            table.add_row("Meaning", "Descriptor target as seen by the kernel")
        else:
            table.add_row("Kind", "Proc symlink")
            table.add_row("Meaning", "Kernel-managed link")

        explanation = Text(
            "These entries are symlinks, not regular files. "
            "That is why `cat` fails on them. pview resolves the target and explains what it means.",
            style="dim italic",
        )

        return Panel(Group(Text(f"{path}", style="bold cyan"), table, explanation), title="Proc Symlink")
