"""Smart fallback renderer for proc entries that lack a dedicated renderer."""

from __future__ import annotations

from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.text import Text


class TextRenderer:
    """Render unknown proc content as structured, human-readable output."""

    def can_render(self, path: Path) -> bool:
        return True

    def render(self, path: Path, content: str | None) -> Panel:
        if not content:
            return Panel(Text(f"{path} is unavailable.", style="dim"), title=path.name)

        text = content.strip()
        if not text:
            return Panel(Text("[dim]Empty file[/dim]"), title=path.name)

        lines = [line for line in text.splitlines() if line.strip()]

        if self._looks_key_value(lines):
            return Panel(self._render_key_values(path, lines), title=path.name)

        if self._looks_table(lines):
            return Panel(self._render_table(path, lines), title=path.name)

        if len(lines) == 1:
            return self._render_single_value(path, lines[0])

        return Panel(
            Group(
                Text(f"{path}", style="bold cyan"),
                Syntax(text, "text", word_wrap=True),
            ),
            title=path.name,
        )

    def _looks_key_value(self, lines: list[str]) -> bool:
        scored = 0
        for line in lines[:20]:
            if ":" in line or "=" in line:
                scored += 1
        return scored >= max(2, len(lines) // 3)

    def _looks_table(self, lines: list[str]) -> bool:
        if len(lines) < 2:
            return False
        widths = []
        for line in lines[:20]:
            parts = line.split()
            if len(parts) >= 3:
                widths.append(len(parts))
        return len(widths) >= 2 and max(widths) - min(widths) <= 2

    def _render_key_values(self, path: Path, lines: list[str]) -> Table:
        table = Table.grid(expand=True)
        table.add_column(style="cyan", width=28)
        table.add_column(overflow="fold")

        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
            elif "=" in line:
                key, value = line.split("=", 1)
            else:
                key, value = line, ""
            table.add_row(key.strip(), value.strip())

        return Group(Text(f"{path}", style="bold cyan"), table)

    def _render_table(self, path: Path, lines: list[str]) -> Table:
        header = lines[0].split()
        table = Table(expand=True, header_style="bold cyan")
        for column in header[:8]:
            table.add_column(column, overflow="fold")

        for line in lines[1:50]:
            parts = line.split()
            if not parts:
                continue
            padded = parts[: len(header[:8])] + [""] * max(0, len(header[:8]) - len(parts))
            table.add_row(*padded[: len(header[:8])])

        return Group(Text(f"{path}", style="bold cyan"), table)

    def _render_single_value(self, path: Path, value: str) -> Panel:
        text = Text()
        text.append(f"{path}\n", style="bold cyan")
        if value.isdigit():
            text.append(f"Numeric value: {int(value):,}\n", style="bold")
            text.append("This file contains a single integer. In procfs that often means a score, count, or limit.", style="dim")
        elif value.startswith("0x"):
            try:
                intval = int(value, 16)
                text.append(f"Hex value: {value} ({intval:,})\n", style="bold")
                text.append(f"Binary: {intval:b}\n", style="dim")
                text.append("This is usually a bitmask. Bits represent enabled features.", style="dim")
            except ValueError:
                text.append(value, style="bold")
        else:
            text.append(value, style="bold")
        return Panel(text, title=path.name)
