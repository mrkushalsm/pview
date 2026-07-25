"""Renderer for /proc/[pid]/limits (resource limits)."""

from __future__ import annotations

from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pview.utils.permissions import is_proc_path

class LimitsRenderer:
    """Display process resource limits with explanations."""

    def can_render(self, path: Path) -> bool:
        return path.name == "limits" and is_proc_path(path)

    def render(self, path: Path, content: str | None) -> Panel:
        """Parse /proc/[pid]/limits and show constraints."""
        if not content:
            return Panel(Text("[dim]No limits data[/dim]"), title="Resource Limits")

        table = Table.grid(expand=True, padding=(0, 1))
        table.add_column(style="cyan", width=25)
        table.add_column(width=15)
        table.add_column(width=15)
        table.add_column()

        lines = content.strip().split("\n")
        if lines:
            lines = lines[1:]

        for line in lines[:20]:
            parts = line.split()
            if len(parts) >= 4:
                name = " ".join(parts[:-3])
                soft = parts[-3]
                hard = parts[-2]
                units = parts[-1] if len(parts) > 4 else ""

                soft_str = "unlimited" if soft == "unlimited" else soft
                hard_str = "unlimited" if hard == "unlimited" else hard

                table.add_row(name, soft_str, hard_str, units)

        explanation = Text(
            "Soft limit: process can temporarily exceed but will be restricted. "
            "Hard limit: absolute maximum, cannot be exceeded. "
            "These are set by ulimit or cgroups.",
            style="dim italic",
        )

        return Panel(
            Group(Text(f"{path}", style="bold cyan"), table, explanation), title="Resource Limits"
        )
