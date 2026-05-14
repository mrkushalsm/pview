"""Renderer for /proc/[pid]/net/udp and /proc/[pid]/net/udp6 (UDP sockets)."""

from __future__ import annotations

from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pview.renderers.net_tcp_renderer import _hex_ip_port

class NetUdpRenderer:
    def can_render(self, path: Path) -> bool:
        return path.name in ("udp", "udp6") and "/proc/" in str(path) and "/net/" in str(path)

    def render(self, path: Path, content: str | None) -> Panel:
        if not content:
            return Panel(Text("[dim]No udp data[/dim]"), title="UDP Sockets")

        lines = content.strip().splitlines()
        table = Table(expand=True)
        table.add_column("sl", width=4, style="dim")
        table.add_column("local", style="cyan")
        table.add_column("remote", style="magenta")
        table.add_column("st", width=6)

        is_ipv6 = path.name == "udp6"
        for line in lines[1:]:
            parts = line.split()
            if len(parts) < 4:
                continue
            sl = parts[0].strip(":")
            local = _hex_ip_port(parts[1], is_ipv6)
            remote = _hex_ip_port(parts[2], is_ipv6)
            state = parts[3]
            table.add_row(sl, local, remote, state)

        explanation = Text(
            "UDP table: local/remote endpoints. Kernel encodes addresses in hex. "
            "Use this to find sockets bound to ports or remote endpoints.",
            style="dim italic",
        )

        return Panel(Group(Text(f"{path}", style="bold cyan"), table, explanation), title="UDP Sockets")
