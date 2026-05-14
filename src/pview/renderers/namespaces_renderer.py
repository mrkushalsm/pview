"""Renderer for /proc/[pid]/ns/ (namespaces)."""

from __future__ import annotations

from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class NamespacesRenderer:
    """Display process namespaces (container/isolation info)."""

    def can_render(self, path: Path) -> bool:
        return path.name == "ns" and "/proc/" in str(path)

    def render(self, path: Path, content: str | None) -> Panel:
        """Parse namespace symlinks to show isolation."""
        table = Table.grid(expand=True, padding=(0, 1))
        table.add_column(style="cyan", width=15)
        table.add_column(overflow="fold")

        try:
            ns_dir = Path(path)
            ns_files = sorted(ns_dir.iterdir())
        except (OSError, PermissionError):
            return Panel(Text("[dim]No namespace access[/dim]"), title="Namespaces")

        ns_info = {
            "cgroup": "Cgroup namespace - resource management isolation",
            "ipc": "IPC namespace - shared memory & message queues",
            "mnt": "Mount namespace - filesystem mount points",
            "net": "Network namespace - network interfaces & routing",
            "pid": "PID namespace - process ID isolation",
            "user": "User namespace - user/group ID mapping",
            "uts": "UTS namespace - hostname & domainname",
            "time": "Time namespace - clock isolation",
        }

        for ns_file in ns_files:
            ns_type = ns_file.name
            try:
                inode = ns_file.stat().st_ino
                description = ns_info.get(ns_type, "Unknown namespace")
                table.add_row(ns_type, f"inode: {inode}\n{description}")
            except (OSError, PermissionError):
                table.add_row(ns_type, "[dim]<no access>[/dim]")

        explanation = Text(
            "Namespaces isolate system resources. Same inode = shared namespace. "
            "Containers use separate namespaces; host typically has inode 4026531836+ (PID ns).",
            style="dim italic",
        )

        return Panel(
            Group(Text(f"{path}", style="bold cyan"), table, explanation), title="Namespaces (Isolation)"
        )
