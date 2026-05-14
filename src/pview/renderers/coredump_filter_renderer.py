"""Renderer for /proc/[pid]/coredump_filter (core dump settings)."""

from __future__ import annotations

from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.text import Text


class CoredumpFilterRenderer:
    """Display core dump filter bitmask."""

    def can_render(self, path: Path) -> bool:
        return path.name == "coredump_filter" and "/proc/" in str(path)

    def render(self, path: Path, content: str | None) -> Panel:
        """Show which memory regions are included in core dumps."""
        if not content:
            return Panel(Text("[dim]No coredump filter[/dim]"), title="Core Dump Settings")

        value_hex = content.strip()
        try:
            value = int(value_hex, 16)
        except ValueError:
            return Panel(Text("[dim]Invalid format[/dim]"), title="Core Dump Settings")

        flags = {
            1: "Anonymous private memory",
            2: "Shared memory regions",
            4: "Huge pages (anonymous)",
            8: "Huge pages (shared)",
            16: "Text segments",
            32: "ELF shared libraries",
        }

        explanation = Text("Core Dump Filter (hex: ", style="dim italic")
        explanation.append(f"{value_hex}", style="bold cyan")
        explanation.append(")\n\n", style="dim italic")

        for bit, description in flags.items():
            included = "✓" if (value & bit) else "✗"
            style = "green" if (value & bit) else "dim red"
            explanation.append(f"  [{included}] {description}\n", style=style)

        explanation.append(
            "\nCore dumps (crash files) include the regions marked above. "
            "Small filter = smaller dumps, but less debugging info.",
            style="dim italic",
        )

        return Panel(Group(Text(f"{path}", style="bold cyan"), explanation), title="Core Dump Settings")
