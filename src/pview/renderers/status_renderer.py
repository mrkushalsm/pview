"""Renderer for /proc/[pid]/status."""

from __future__ import annotations

from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pview.utils.permissions import is_proc_path
from pview.utils.parsing import parse_key_value_line
from pview.utils.units import kib_to_human


class StatusRenderer:
    """Render process status file with key metrics highlighted."""

    def can_render(self, path: Path) -> bool:
        return path.name == "status" and is_proc_path(path)

    def render(self, path: Path, content: str | None) -> Panel:
        items: dict[str, str] = {}
        if content:
            for line in content.splitlines():
                parsed = parse_key_value_line(line)
                if parsed is not None:
                    key, value = parsed
                    items[key] = value

        table = Table.grid(expand=True, padding=(0, 1))
        table.add_column(style="bold cyan", width=20)
        table.add_column()

        key_fields = [
            ("Name", "Process name"),
            ("Pid", "Process ID"),
            ("PPid", "Parent process ID"),
            ("State", "Process state (R/S/D/Z/T)"),
            ("Threads", "Number of threads"),
            ("VmPeak", "Peak virtual memory"),
            ("VmSize", "Current virtual memory"),
            ("VmRSS", "Resident set size (physical RAM)"),
            ("VmLib", "Shared libraries"),
            ("VmSwap", "Memory swapped to disk"),
            ("Uid", "Real/effective/saved/filesystem UID"),
            ("Gid", "Real/effective/saved/filesystem GID"),
            ("FDSize", "Number of file descriptors"),
            ("Seccomp", "Seccomp filtering status (0=no)"),
            ("SigBlk", "Blocked signals"),
            ("SigIgn", "Ignored signals"),
            ("SigPnd", "Pending signals"),
        ]

        for key, description in key_fields:
            value = items.get(key, "n/a")
            if value != "n/a" and "Vm" in key:
                try:
                    kib = int(value.split()[0])
                    value = kib_to_human(kib)
                except (ValueError, IndexError):
                    pass
            table.add_row(key, f"{value}\n[dim]{description}[/dim]")

        explanation = Text(
            "The status file gives a snapshot of the process state. "
            "VmRSS is actual memory used; VmSwap shows memory on disk. "
            "Multiple threads share virtual memory but run independently.",
            style="dim italic",
        )

        return Panel(Group(Text(f"{path}", style="bold cyan"), table, explanation), title="Process Status")

