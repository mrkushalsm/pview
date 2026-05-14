"""Renderer for /proc/[pid]/task/ - list threads and allow drilling into thread files."""

from __future__ import annotations

from pathlib import Path
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class TaskRenderer:
    def can_render(self, path: Path) -> bool:
        # Matches the task directory itself
        return path.name == "task" and "/proc/" in str(path)

    def render(self, path: Path, content: str | None) -> Panel:
        try:
            task_dir = Path(path)
            entries = sorted([p for p in task_dir.iterdir() if p.name.isdigit()])
        except (OSError, PermissionError):
            return Panel(Text("[dim]No task access or empty[/dim]"), title="Threads")

        table = Table(expand=True)
        table.add_column("TID", style="cyan", width=10)
        table.add_column("Name", overflow="fold")

        for tid_dir in entries[:200]:
            name = "n/a"
            try:
                # Try to read comm
                comm = (tid_dir / "comm").read_text(errors="ignore").strip()
                name = comm or "<no name>"
            except Exception:
                pass
            table.add_row(tid_dir.name, name)

        explanation = Text(
            "Threads are shown by TID. Click a thread to inspect its own stat/status/cmdline/files. "
            "Thread files have the same format as the main process files.",
            style="dim italic",
        )

        return Panel(table, title="Threads (task)")
