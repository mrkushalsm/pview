"""Renderer for /proc/meminfo."""

from __future__ import annotations

from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pview.utils.parsing import parse_key_value_line
from pview.utils.units import kib_to_human


class MemInfoRenderer:
    """Render /proc/meminfo as a summarized memory dashboard."""

    def can_render(self, path: Path) -> bool:
        return path.name == "meminfo"

    def render(self, path: Path, content: str | None):
        items: dict[str, str] = {}
        if content:
            for line in content.splitlines():
                parsed = parse_key_value_line(line)
                if parsed is not None:
                    key, value = parsed
                    items[key] = value

        total = self._parse_kib(items.get("MemTotal"))
        free = self._parse_kib(items.get("MemFree"))
        available = self._parse_kib(items.get("MemAvailable"))
        cached = self._parse_kib(items.get("Cached"))

        table = Table.grid(expand=True)
        table.add_column(ratio=1)
        table.add_column(ratio=1)
        table.add_row("Total", kib_to_human(total))
        table.add_row("Free", kib_to_human(free))
        table.add_row("Available", kib_to_human(available))
        table.add_row("Cached", kib_to_human(cached))

        summary = Text()
        if total is not None and available is not None:
            used = max(total - available, 0)
            summary.append(f"Used approx: {kib_to_human(used)}\n", style="bold")
            summary.append(f"Available: {available / total:.0%} of total")
        else:
            summary.append("Unable to compute memory summary from /proc/meminfo.")

        return Panel(Group(Text("/proc/meminfo", style="bold cyan"), summary, table), title="Memory")

    def _parse_kib(self, value: str | None) -> int | None:
        if value is None:
            return None
        head = value.split()[0]
        try:
            return int(head)
        except ValueError:
            return None
