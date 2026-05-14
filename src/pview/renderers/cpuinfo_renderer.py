"""Renderer for /proc/cpuinfo."""

from __future__ import annotations

from pathlib import Path

from rich.columns import Columns
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pview.utils.parsing import parse_key_value_line


class CpuInfoRenderer:
    """Render /proc/cpuinfo as a topology summary."""

    def can_render(self, path: Path) -> bool:
        return path.name == "cpuinfo"

    def render(self, path: Path, content: str | None):
        processors: list[dict[str, str]] = []
        current: dict[str, str] = {}

        if content:
            for line in content.splitlines():
                if not line.strip():
                    if current:
                        processors.append(current)
                        current = {}
                    continue
                parsed = parse_key_value_line(line)
                if parsed is not None:
                    key, value = parsed
                    current[key] = value
            if current:
                processors.append(current)

        cpu_count = len(processors)
        model_name = processors[0].get("model name", "Unknown") if processors else "Unknown"
        mhz = processors[0].get("cpu MHz", "n/a") if processors else "n/a"

        stats = Table.grid(expand=True)
        stats.add_column(ratio=1)
        stats.add_column(ratio=2)
        stats.add_row("CPUs", str(cpu_count))
        stats.add_row("Model", model_name)
        stats.add_row("Frequency", f"{mhz} MHz")

        processor_cards = []
        for cpu in processors[:8]:
            card = Table.grid(padding=(0, 1))
            card.add_column(style="bold cyan")
            card.add_column()
            card.add_row("processor", cpu.get("processor", "?"))
            card.add_row("core id", cpu.get("core id", "n/a"))
            card.add_row("physical id", cpu.get("physical id", "n/a"))
            processor_cards.append(Panel(card, title=f"CPU {cpu.get('processor', '?')}", border_style="cyan"))

        overview = Panel(stats, title="CPU Summary", border_style="green")
        cards = Columns(processor_cards) if processor_cards else Text("No CPU entries found.")
        return Panel(
            Group(
                Text("/proc/cpuinfo", style="bold cyan"),
                Text("Top-level CPU topology summary"),
                overview,
                cards,
            ),
            title="CPU",
        )
