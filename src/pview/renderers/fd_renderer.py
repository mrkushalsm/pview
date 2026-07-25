"""Renderer for /proc/[pid]/fd (file descriptors)."""

from __future__ import annotations

from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pview.utils.permissions import is_proc_path

class FdRenderer:
    """Display file descriptor table with resolved targets."""

    def can_render(self, path: Path) -> bool:
        return path.name == "fd" and is_proc_path(path)

    def render(self, path: Path, content: str | None) -> Panel:
        """Enumerate and display FDs in the fd directory."""
        table = Table.grid(expand=True, padding=(0, 1))
        table.add_column(style="cyan", width=8)
        table.add_column()

        try:
            fds = sorted(path.iterdir(), key=lambda p: int(p.name) if p.name.isdigit() else 999999)
        except (OSError, PermissionError):
            fds = []

        if not fds:
            table.add_row("[dim]<no fds>[/dim]", "")
        else:
            for fd_path in fds[:100]:
                try:
                    target = fd_path.resolve()
                    table.add_row(fd_path.name, str(target))
                except (OSError, RuntimeError):
                    table.add_row(fd_path.name, "[dim]<unresolvable>[/dim]")

        return Panel(
            Group(Text(f"{path}", style="bold cyan"), Text(f"{len(fds)} file descriptors"), table),
            title="Open File Descriptors",
        )
