"""Renderer for /proc/[pid]/net/unix (UNIX domain sockets)."""

from __future__ import annotations

from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

class NetUnixRenderer:
    def can_render(self, path: Path) -> bool:
        return path.name == "unix" and "/proc/" in str(path) and "/net/" in str(path)

    def render(self, path: Path, content: str | None) -> Panel:
        if not content:
            return Panel(Text("[dim]No unix socket data[/dim]"), title="UNIX Sockets")

        lines = content.strip().splitlines()
        table = Table(expand=True)
        table.add_column("Num", width=6, style="dim")
        table.add_column("RefCount", width=8)
        table.add_column("Protocol", width=8)
        table.add_column("Flags", width=8)
        table.add_column("Type", width=8)
        table.add_column("Path", overflow="fold")

        for line in lines[1:]:
            parts = line.split()
            if len(parts) < 7:
                continue
            num = parts[0]
            refcount = parts[1]
            proto = parts[2]
            flags = parts[3]
            typ = parts[4]
            pathstr = parts[6] if len(parts) > 6 else ""
            table.add_row(num, refcount, proto, flags, typ, pathstr)

        explanation = Text(
            "UNIX domain sockets show local IPC endpoints. Path field is the socket filesystem path. "
            "Useful to find which processes expose local sockets.",
            style="dim italic",
        )

        return Panel(Group(Text(f"{path}", style="bold cyan"), table, explanation), title="UNIX Domain Sockets")
