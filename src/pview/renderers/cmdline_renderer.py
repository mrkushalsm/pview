"""Renderer for /proc/[pid]/cmdline."""

from __future__ import annotations

from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.text import Text

from pview.utils.permissions import is_proc_path

class CmdlineRenderer:
    """Display process command line arguments."""

    def can_render(self, path: Path) -> bool:
        return path.name == "cmdline" and is_proc_path(path)

    def render(self, path: Path, content: str | None) -> Panel:
        """Parse and display command line arguments."""
        if not content:
            return Panel(Text("[dim]No cmdline[/dim]"), title="Command Line")

        args = content.split("\x00")
        args = [arg for arg in args if arg]

        output = Text()
        output.append(f"Command: ", style="bold")
        output.append(args[0] if args else "(unknown)\n", style="cyan")

        if len(args) > 1:
            output.append("\nArguments:\n", style="bold")
            for i, arg in enumerate(args[1:], 1):
                if len(arg) > 100:
                    arg = arg[:97] + "..."
                output.append(f"  [{i}] {arg}\n")

        return Panel(Group(Text(f"{path}", style="bold cyan"), output), title="Command Line")
