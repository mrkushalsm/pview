"""Renderer for /proc/[pid]/io (I/O stats)."""

from __future__ import annotations

from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pview.utils.parsing import parse_key_value_line
from pview.utils.units import kib_to_human


class IoRenderer:
    """Display process I/O statistics."""

    def can_render(self, path: Path) -> bool:
        return path.name == "io" and "/proc/" in str(path)

    def render(self, path: Path, content: str | None) -> Panel:
        """Parse and display I/O stats."""
        table = Table.grid(expand=True, padding=(0, 1))
        table.add_column(style="cyan", width=25)
        table.add_column()

        items: dict[str, str] = {}
        if content:
            for line in content.splitlines():
                parsed = parse_key_value_line(line)
                if parsed is not None:
                    key, value = parsed
                    items[key] = value

        key_order = [
            "rchar",
            "wchar",
            "syscr",
            "syscw",
            "read_bytes",
            "write_bytes",
            "cancelled_write_bytes",
        ]
        for key in key_order:
            value = items.get(key, "n/a")
            if value != "n/a":
                try:
                    bytes_val = int(value)
                    if "bytes" in key:
                        value = kib_to_human(bytes_val // 1024) if bytes_val > 0 else "0 B"
                except ValueError:
                    pass
            table.add_row(key, value)

        return Panel(Group(Text(f"{path}", style="bold cyan"), table), title="I/O Statistics")
