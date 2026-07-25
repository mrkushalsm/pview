"""Renderer for /proc/[pid]/mountinfo (mount table)."""

from __future__ import annotations

from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pview.utils.permissions import is_proc_path

class MountinfoRenderer:
    """Display process mount information."""

    def can_render(self, path: Path) -> bool:
        return path.name == "mountinfo" and is_proc_path(path)

    def render(self, path: Path, content: str | None) -> Panel:
        """Parse mountinfo and show mounted filesystems."""
        table = Table.grid(expand=True, padding=(0, 1))
        table.add_column(style="cyan", width=20)
        table.add_column()

        if not content:
            return Panel(Text("[dim]No mount info[/dim]"), title="Mounts")

        lines = content.strip().split("\n")
        for line in lines[:30]:
            parts = line.split()
            if len(parts) >= 8:
                mount_id = parts[0]
                parent_id = parts[1]
                mount_point = parts[4]
                fs_type = parts[7]

                table.add_row(f"[{mount_id}] {mount_point}", fs_type)

        explanation = Text(
            "Shows filesystem mounts as seen by this process. "
            "Different processes may see different mounts due to mount namespaces. "
            "Important for containers and chroots.",
            style="dim italic",
        )

        return Panel(
            Group(Text(f"{path}", style="bold cyan"), table, explanation), title="Mount Information"
        )
