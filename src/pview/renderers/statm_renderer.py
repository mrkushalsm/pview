"""Renderer for /proc/[pid]/statm (process memory summary)."""

from __future__ import annotations

from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pview.utils.permissions import is_proc_path

class StatmRenderer:
    """Display simplified memory usage statistics."""

    def can_render(self, path: Path) -> bool:
        return path.name == "statm" and is_proc_path(path)

    def render(self, path: Path, content: str | None) -> Panel:
        """Parse /proc/[pid]/statm for memory breakdown."""
        if not content:
            return Panel(Text("[dim]No statm data[/dim]"), title="Memory Usage")

        parts = content.split()
        if len(parts) < 7:
            return Panel(Text("[dim]Incomplete statm data[/dim]"), title="Memory Usage")

        try:
            vsize = int(parts[0])  # Total program size
            rss = int(parts[1])    # Resident set size
            shared = int(parts[2])  # Shared memory
            text = int(parts[3])   # Text (code)
            lib = int(parts[4])    # Shared library
            data = int(parts[5])   # Data + stack
            dt = int(parts[6])     # Dirty pages
        except ValueError:
            return Panel(Text("[dim]Invalid statm format[/dim]"), title="Memory Usage")

        page_kb = 4  # 4KB per page on most systems

        table = Table.grid(expand=True, padding=(0, 1))
        table.add_column(style="cyan", width=25)
        table.add_column()
        table.add_column(style="dim")

        table.add_row("Total VM Size", f"{vsize * page_kb // 1024} MiB", f"({vsize} pages)")
        table.add_row("Resident (RSS)", f"{rss * page_kb // 1024} MiB", f"({rss} pages)")
        table.add_row("Shared", f"{shared * page_kb // 1024} MiB", f"({shared} pages)")
        table.add_row("Code (Text)", f"{text * page_kb // 1024} MiB", f"({text} pages)")
        table.add_row("Libraries", f"{lib * page_kb // 1024} MiB", f"({lib} pages)")
        table.add_row("Data + Stack", f"{data * page_kb // 1024} MiB", f"({data} pages)")
        table.add_row("Dirty Pages", f"{dt * page_kb // 1024} MiB", f"({dt} pages)")

        explanation = Text(
            "RSS (Resident Set Size) is actual physical RAM used. "
            "Shared includes memory mapped from libraries. "
            "Dirty pages need to be written back to disk.",
            style="dim italic",
        )

        return Panel(
            Group(Text(f"{path}", style="bold cyan"), table, explanation), title="Memory Summary"
        )
