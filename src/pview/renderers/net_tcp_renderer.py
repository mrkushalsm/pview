"""Renderer for /proc/[pid]/net/tcp and /proc/[pid]/net/tcp6 (TCP socket table)."""

from __future__ import annotations

from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


def _hex_ip_port(ip_hex: str, is_ipv6: bool = False) -> str:
    # Convert IPv4 hex like 0100007F:0035 to 127.0.0.1:53
    try:
        addr, port = ip_hex.split(":")
    except ValueError:
        return ip_hex

    port = int(port, 16)
    if not is_ipv6:
        # little-endian hex bytes
        raw = bytes.fromhex(addr)
        ip = ".".join(str(b) for b in raw[::-1])
        return f"{ip}:{port}"
    else:
        # IPv6 - skip detailed decoding for brevity (show hex groups)
        groups = [addr[i:i+8] for i in range(0, len(addr), 8)]
        ip = ":".join(g.lstrip("0") or "0" for g in groups)
        return f"{ip}:{port}"


class NetTcpRenderer:
    """Render /proc/*/net/tcp and tcp6 in table form with human-friendly addresses."""

    def can_render(self, path: Path) -> bool:
        return path.name in ("tcp", "tcp6") and "/proc/" in str(path) and "/net/" in str(path)

    def render(self, path: Path, content: str | None) -> Panel:
        if not content:
            return Panel(Text("[dim]No tcp data[/dim]"), title="TCP Sockets")

        lines = content.strip().splitlines()
        table = Table(expand=True)
        table.add_column("sl", width=4, style="dim")
        table.add_column("local", style="cyan")
        table.add_column("remote", style="magenta")
        table.add_column("st", width=6)
        table.add_column("tx_rx", width=12)

        is_ipv6 = path.name == "tcp6"
        for line in lines[1:]:
            parts = line.split()
            if len(parts) < 10:
                continue
            sl = parts[0].strip(":")
            local = _hex_ip_port(parts[1], is_ipv6)
            remote = _hex_ip_port(parts[2], is_ipv6)
            state = parts[3]
            tx_rx = f"{int(parts[8]):,}/{int(parts[9]):,}" if len(parts) > 9 else "-"
            table.add_row(sl, local, remote, state, tx_rx)

        explanation = Text(
            "Local and remote addresses are decoded from kernel hex encoding. "
            "State codes (01=ESTABLISHED, 0A=LISTEN, etc.) follow kernel's /proc/net/tcp format.",
            style="dim italic",
        )

        return Panel(Group(Text(f"{path}", style="bold cyan"), table, explanation), title="TCP Sockets")
