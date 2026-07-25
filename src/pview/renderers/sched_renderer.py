"""Renderer for /proc/[pid]/sched (scheduler info)."""

from __future__ import annotations

from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pview.utils.permissions import is_proc_path

class SchedRenderer:
    """Display process scheduler information."""

    def can_render(self, path: Path) -> bool:
        return path.name == "sched" and is_proc_path(path)

    def render(self, path: Path, content: str | None) -> Panel:
        """Parse and display scheduler stats."""
        table = Table.grid(expand=True, padding=(0, 1))
        table.add_column(style="cyan", width=30)
        table.add_column(overflow="fold")

        if not content:
            return Panel(Text("[dim]No sched info[/dim]"), title="Scheduler")

        lines = content.splitlines()
        for line in lines[:40]:
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                if len(value) > 80:
                    value = value[:77] + "..."
                table.add_row(key, value)

        return Panel(Group(Text(f"{path}", style="bold cyan"), table), title="Scheduler Information")
