"""Renderer for /proc/[pid]/oom_score_adj (user-adjustable OOM priority)."""

from __future__ import annotations

from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.text import Text


class OomScoreAdjRenderer:
    """Display OOM killer score adjustment setting."""

    def can_render(self, path: Path) -> bool:
        return path.name == "oom_score_adj" and "/proc/" in str(path)

    def render(self, path: Path, content: str | None) -> Panel:
        """Show user-adjustable OOM priority."""
        value = content.strip() if content else "0"

        try:
            adj = int(value)
        except ValueError:
            adj = 0

        if adj < -1000:
            priority = "Protected (won't be killed)"
            style = "green"
        elif adj < -100:
            priority = "Very Low (unlikely to be killed)"
            style = "green"
        elif adj < 0:
            priority = "Low (less likely to be killed)"
            style = "yellow"
        elif adj == 0:
            priority = "Default (normal)"
            style = "blue"
        elif adj < 500:
            priority = "High (more likely to be killed)"
            style = "orange"
        else:
            priority = "Very High (will be killed first)"
            style = "red"

        explanation = Text()
        explanation.append("OOM Score Adjustment: ", style="bold cyan")
        explanation.append(f"{value}\n\n", style="bold")
        explanation.append("Priority: ", style="bold")
        explanation.append(f"{priority}\n", style=style)
        explanation.append(
            "\nThis is a user-adjustable setting (set via 'echo N > /proc/self/oom_score_adj'). "
            "Values range from -1000 (protected) to 1000 (first to kill). "
            "Adjusts the kernel's OOM killer priority.",
            style="dim italic",
        )

        return Panel(Group(Text(f"{path}", style="bold cyan"), explanation), title="OOM Score Adjustment")
