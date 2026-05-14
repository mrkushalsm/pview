"""Renderer for /proc/[pid]/net/dev (network device statistics per interface)."""

from __future__ import annotations

from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

class NetDevRenderer:
    def can_render(self, path: Path) -> bool:
        return path.name == "dev" and "/proc/" in str(path) and "/net/" in str(path)

    def render(self, path: Path, content: str | None) -> Panel:
        if not content:
            return Panel(Text("[dim]No dev data[/dim]"), title="Net Devices")

        lines = [l for l in content.splitlines() if l.strip()]
        table = Table(expand=True)
        table.add_column("Iface", style="cyan")
        table.add_column("RX bytes", justify="right")
        table.add_column("RX packets", justify="right")
        table.add_column("TX bytes", justify="right")
        table.add_column("TX packets", justify="right")

        # Skip two header lines
        for line in lines[2:]:
            parts = line.split()
            iface = parts[0].rstrip(":")
            rx_bytes = parts[1]
            rx_packets = parts[2]
            tx_bytes = parts[9]
            tx_packets = parts[10]
            table.add_row(iface, f"{int(rx_bytes):,}", f"{int(rx_packets):,}", f"{int(tx_bytes):,}", f"{int(tx_packets):,}")

        explanation = Text(
            "Per-interface counters (rx/tx bytes and packets). Useful to see which interface the process uses. "
            "These counters are kernel-wide but shown in the process's /proc/net view (namespace-aware).",
            style="dim italic",
        )

        return Panel(Group(Text(f"{path}", style="bold cyan"), table, explanation), title="Network Devices")
