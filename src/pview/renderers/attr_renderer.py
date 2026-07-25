"""Renderer for /proc/[pid]/attr/ (SELinux attributes)."""

from __future__ import annotations

from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pview.utils.permissions import is_proc_path

class AttrRenderer:
    """Display SELinux security attributes."""

    def can_render(self, path: Path) -> bool:
        return path.name == "attr" and is_proc_path(path)

    def render(self, path: Path, content: str | None) -> Panel:
        """Show SELinux security context information."""
        table = Table.grid(expand=True, padding=(0, 1))
        table.add_column(style="cyan", width=20)
        table.add_column(overflow="fold")

        try:
            attr_dir = Path(path)
            attr_files = sorted(attr_dir.iterdir())
        except (OSError, PermissionError):
            return Panel(Text("[dim]No attribute access[/dim]"), title="SELinux Attributes")

        for attr_file in attr_files:
            try:
                content_data = attr_file.read_text(errors="ignore").strip()
                table.add_row(attr_file.name, content_data)
            except (OSError, PermissionError):
                table.add_row(attr_file.name, "[dim]<no access>[/dim]")

        explanation = Text(
            "SELinux attributes define security context (user, role, type, level). "
            "Only visible if SELinux is enabled (getenforce: Enforcing/Permissive). "
            "Type is the main security policy constraint.",
            style="dim italic",
        )

        return Panel(Group(Text(f"{path}", style="bold cyan"), table, explanation), title="SELinux Attributes")
