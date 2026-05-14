"""Renderer for /proc/[pid]/smaps (detailed memory maps with PSS)."""

from __future__ import annotations

from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pview.utils.units import kib_to_human


class SmapsRenderer:
    """Display detailed memory maps with proportional set size."""

    def can_render(self, path: Path) -> bool:
        return path.name == "smaps" and "/proc/" in str(path)

    def render(self, path: Path, content: str | None) -> Panel:
        """Parse smaps to show memory breakdown per region."""
        if not content:
            return Panel(Text("[dim]No smaps data[/dim]"), title="Detailed Memory Map")

        table = Table.grid(expand=True, padding=(0, 1))
        table.add_column(style="dim", width=18)
        table.add_column(style="cyan", width=8)
        table.add_column()

        lines = content.splitlines()
        total_pss = 0
        current_mapping = None

        for line in lines[:100]:
            if "-" in line and line[0].isalnum():
                current_mapping = line.split()[0]
                table.add_row(current_mapping, "mapping", "")
            elif "Pss:" in line:
                parts = line.split()
                pss_kib = int(parts[1]) if len(parts) > 1 else 0
                total_pss += pss_kib
                table.add_row("  PSS", kib_to_human(pss_kib), "(proportional set size)")
            elif "Size:" in line:
                parts = line.split()
                size_kib = int(parts[1]) if len(parts) > 1 else 0
                table.add_row("  Size", kib_to_human(size_kib), "")
            elif "Rss:" in line:
                parts = line.split()
                rss_kib = int(parts[1]) if len(parts) > 1 else 0
                table.add_row("  RSS", kib_to_human(rss_kib), "(resident)")

        summary = Text(f"Total PSS: {kib_to_human(total_pss)}", style="bold cyan")
        explanation = Text(
            "PSS (Proportional Set Size) divides shared pages by the number of processes using them. "
            "Better than RSS for accounting memory across processes.",
            style="dim italic",
        )

        return Panel(
            Group(Text(f"{path}", style="bold cyan"), summary, table, explanation),
            title="Detailed Memory Map",
        )
