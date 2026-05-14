"""Renderer for /proc/[pid]/environ (environment variables)."""

from __future__ import annotations

from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class EnvironRenderer:
    """Display process environment variables."""

    def can_render(self, path: Path) -> bool:
        return path.name == "environ" and "/proc/" in str(path)

    def render(self, path: Path, content: str | None) -> Panel:
        """Parse and display environment variables."""
        table = Table.grid(expand=True, padding=(0, 1))
        table.add_column(style="cyan", width=30)
        table.add_column(overflow="fold")

        if not content:
            return Panel(Text("[dim]No environment[/dim]"), title="Environment Variables")

        env_vars = content.split("\x00")
        for var in env_vars[:50]:
            if "=" in var:
                key, value = var.split("=", 1)
                if len(value) > 80:
                    value = value[:77] + "..."
                table.add_row(key, value)

        return Panel(
            Group(Text(f"{path}", style="bold cyan"), Text(f"{len(env_vars)} variables", style="dim"), table),
            title="Environment Variables",
        )
