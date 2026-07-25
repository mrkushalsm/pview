"""Renderer for /proc/[pid]/numa_maps (NUMA memory distribution)."""

from __future__ import annotations

from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pview.utils.permissions import is_proc_path

class NumaMapsRenderer:
    """Display NUMA node memory distribution."""

    def can_render(self, path: Path) -> bool:
        return path.name == "numa_maps" and is_proc_path(path)

    def render(self, path: Path, content: str | None) -> Panel:
        """Parse numa_maps to show memory distribution across NUMA nodes."""
        table = Table.grid(expand=True, padding=(0, 1))
        table.add_column(style="dim", width=18)
        table.add_column(overflow="fold")

        if not content:
            return Panel(Text("[dim]No NUMA info (single-node system)[/dim]"), title="NUMA Memory Map")

        lines = content.splitlines()
        for line in lines[:20]:
            parts = line.split()
            if parts:
                address = parts[0]
                table.add_row(address, " ".join(parts[1:]))

        explanation = Text(
            "NUMA (Non-Uniform Memory Access) maps show memory distribution across CPU nodes. "
            "Each line shows virtual address range and which NUMA nodes hold pages. "
            "Useful for analyzing memory locality in NUMA systems.",
            style="dim italic",
        )

        return Panel(
            Group(Text(f"{path}", style="bold cyan"), table, explanation), title="NUMA Memory Distribution"
        )
