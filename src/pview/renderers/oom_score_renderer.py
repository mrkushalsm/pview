"""Renderer for /proc/[pid]/oom_score (OOM killer priority)."""

from __future__ import annotations

from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.text import Text


class OomScoreRenderer:
    """Display OOM killer score and badness."""

    def can_render(self, path: Path) -> bool:
        return path.name == "oom_score" and "/proc/" in str(path)

    def render(self, path: Path, content: str | None) -> Panel:
        """Show OOM killer priority and explanation."""
        score = content.strip() if content else "?"

        try:
            score_int = int(score)
        except ValueError:
            score_int = -1

        # OOM score interpretation
        if score_int < 0:
            priority = "Protected (kernel/critical)"
            risk = "[green]Very Low[/green]"
        elif score_int < 100:
            priority = "Low"
            risk = "[green]Low[/green]"
        elif score_int < 500:
            priority = "Medium"
            risk = "[yellow]Medium[/yellow]"
        elif score_int < 1000:
            priority = "High"
            risk = "[orange]High[/orange]"
        else:
            priority = "Very High"
            risk = "[red]Very High[/red]"

        explanation = Text()
        explanation.append("OOM Score: ", style="bold cyan")
        explanation.append(f"{score}\n\n")
        explanation.append("Priority: ", style="bold")
        explanation.append(f"{priority}\n")
        explanation.append("Kill Risk: ", style="bold")
        explanation.append(risk)
        explanation.append(
            "\n\nWhen system runs out of memory, the kernel kills the process with the highest score. "
            "Negative scores are protected. You can adjust with oom_score_adj.",
            style="dim italic",
        )

        return Panel(Group(Text(f"{path}", style="bold cyan"), explanation), title="OOM Killer Score")
