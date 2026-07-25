"""Renderer for /proc/[pid]/stat (process scheduling statistics)."""

from __future__ import annotations

from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pview.utils.permissions import is_proc_path

class StatRenderer:
    """Display process scheduling stats with kernel time accounting."""

    def can_render(self, path: Path) -> bool:
        return path.name == "stat" and is_proc_path(path)

    def render(self, path: Path, content: str | None) -> Panel:
        """Parse /proc/[pid]/stat and display in human-readable format."""
        if not content:
            return Panel(Text("[dim]No stat data[/dim]"), title="Process Stats")

        parts = content.rsplit(")", 1)
        if len(parts) != 2:
            return Panel(Text("[dim]Invalid stat format[/dim]"), title="Process Stats")

        fields = parts[1].split()
        if len(fields) < 15:
            return Panel(Text("[dim]Incomplete stat data[/dim]"), title="Process Stats")

        state = fields[0] if fields else "?"
        ppid = fields[1] if len(fields) > 1 else "?"
        utime = int(fields[11]) if len(fields) > 11 else 0
        stime = int(fields[12]) if len(fields) > 12 else 0
        vsize = int(fields[20]) if len(fields) > 20 else 0
        rss = int(fields[21]) if len(fields) > 21 else 0

        state_text = self._decode_state(state)

        table = Table.grid(expand=True, padding=(0, 1))
        table.add_column(style="cyan", width=25)
        table.add_column()

        table.add_row("State", f"{state} ({state_text})")
        table.add_row("Parent PID", ppid)
        table.add_row("User CPU Time", f"{utime} jiffies (~{utime/100:.2f}s)")
        table.add_row("System CPU Time", f"{stime} jiffies (~{stime/100:.2f}s)")
        table.add_row("Virtual Memory", f"{vsize} bytes (~{vsize/1024/1024:.1f} MiB)")
        table.add_row("RSS Pages", f"{rss} pages (~{rss*4/1024:.1f} MiB)")

        explanation = Text(
            "The stat file provides low-level scheduling statistics. "
            "User time is how much CPU the process used; system time is kernel overhead. "
            "VSize is total virtual memory; RSS is physical RAM actually in use.",
            style="dim italic",
        )

        return Panel(Group(Text(f"{path}", style="bold cyan"), table, explanation), title="Process Stats")

    def _decode_state(self, state: str) -> str:
        states = {
            "R": "Running",
            "S": "Sleeping (interruptible)",
            "D": "Disk sleep (uninterruptible)",
            "Z": "Zombie",
            "T": "Stopped",
            "W": "Paging",
            "X": "Dead",
            "x": "Dead",
            "K": "Wakekill",
            "P": "Parked",
        }
        return states.get(state, "Unknown")
