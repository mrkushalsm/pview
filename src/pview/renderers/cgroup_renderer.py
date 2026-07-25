"""Renderer for /proc/[pid]/cgroup (cgroup membership)."""

from __future__ import annotations

from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.text import Text

from pview.utils.permissions import is_proc_path

class CgroupRenderer:
    """Display cgroup membership."""

    def can_render(self, path: Path) -> bool:
        return path.name == "cgroup" and is_proc_path(path)

    def render(self, path: Path, content: str | None) -> Panel:
        """Show which cgroups the process belongs to."""
        if not content:
            return Panel(Text("[dim]No cgroup info[/dim]"), title="Cgroup Membership")

        text = Text()
        lines = content.splitlines()

        for line in lines[:30]:
            parts = line.split(":")
            if len(parts) >= 3:
                hierarchy = parts[0]
                subsystems = parts[1]
                path_data = parts[2]
                text.append(f"[{hierarchy}] ", style="dim cyan")
                text.append(f"{subsystems}\n", style="cyan")
                text.append(f"  → {path_data}\n", style="dim")

        explanation = Text(
            "\nCgroups (control groups) limit and monitor resource usage. "
            "Each line shows: hierarchy : subsystems : path_in_cgroup. "
            "Cgroups v2 simplifies this (single unified hierarchy).",
            style="dim italic",
        )

        return Panel(
            Group(Text(f"{path}", style="bold cyan"), text, explanation), title="Cgroup Membership"
        )
