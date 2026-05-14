"""Renderer for /proc/[pid]/maps (memory map)."""

from __future__ import annotations

from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pview.utils.units import kib_to_human


class MapsRenderer:
    """Visualize process memory map regions."""

    def can_render(self, path: Path) -> bool:
        return path.name == "maps" and "/proc/" in str(path)

    def render(self, path: Path, content: str | None) -> Panel:
        """Parse and display memory map regions."""
        table = Table.grid(expand=True, padding=(0, 1))
        table.add_column(style="dim", width=18)
        table.add_column(style="cyan", width=8)
        table.add_column()

        if not content:
            return Panel(Text("[dim]Unable to read maps[/dim]"), title="Memory Map")

        lines = content.splitlines()
        total_size = 0

        for line in lines[:50]:
            parts = line.split()
            if len(parts) < 5:
                continue

            addr_range = parts[0]
            perms = parts[1]
            offset = parts[2]
            dev = parts[3]
            inode = parts[4]
            pathname = " ".join(parts[5:]) if len(parts) > 5 else ""

            start_addr = int(addr_range.split("-")[0], 16)
            end_addr = int(addr_range.split("-")[1], 16)
            size_bytes = end_addr - start_addr
            total_size += size_bytes

            size_kib = size_bytes // 1024
            size_str = kib_to_human(size_kib) if size_kib > 0 else "0 KiB"

            icon = self._icon_for_perms(perms)
            label = pathname or f"[{dev}]"

            table.add_row(f"{icon} {addr_range}", perms, f"{size_str} {label}")

        summary = Text(f"Total: {kib_to_human(total_size // 1024)}, {len(lines)} regions shown", style="dim")
        return Panel(Group(Text(f"{path}", style="bold cyan"), summary, table), title="Memory Map")

    def _icon_for_perms(self, perms: str) -> str:
        if "x" in perms:
            return "[X]"
        elif "w" in perms:
            return "[W]"
        else:
            return "[R]"
