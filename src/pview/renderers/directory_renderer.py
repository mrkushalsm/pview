"""Renderer for proc directories and process browsers."""

from __future__ import annotations

from pathlib import Path

from rich.console import Group
from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pview.core.proc_tree_model import ProcTreeModel
from pview.models.proc_node import NodeType
from pview.core.proc_reader import ProcReader
from pview.renderers.registry import RendererRegistry


class DirectoryRenderer:
    """Display a directory listing."""

    def __init__(
        self,
        model: ProcTreeModel | None = None,
        reader: ProcReader | None = None,
        registry: RendererRegistry | None = None,
    ) -> None:
        self._model = model if model is not None else ProcTreeModel()
        self._reader = reader if reader is not None else ProcReader()
        self._registry = registry if registry is not None else RendererRegistry()

    def can_render(self, node_type: NodeType) -> bool:
        return node_type in (NodeType.DIRECTORY, NodeType.PROCESS)

    def render(self, path: Path, node_type: NodeType) -> Panel:
        children = self._model._sync_get_children(path)

        table = Table.grid(expand=True)
        table.add_column(style="cyan", width=28)
        table.add_column()

        if not children:
            table.add_row("[dim]<empty>[/dim]", "")
        else:
            for child in children[:50]:
                label = child.display_label()
                icon = self._get_icon(child.node_type)
                table.add_row(f"{icon} {label}", child.node_type.value)

        # Build preview of first file-like child using shared renderers
        preview = Text("[dim]No preview available[/dim]")
        try:
            preview_candidate = next(
                (c for c in children if c.node_type in (NodeType.FILE, NodeType.SYMLINK)), None
            )
            if preview_candidate is not None:
                res = (
                    self._reader.read_link(preview_candidate.path)
                    if preview_candidate.node_type == NodeType.SYMLINK
                    else self._reader.read_text(preview_candidate.path)
                )
                preview = self._registry.render(preview_candidate.path, res.content)
        except Exception:
            preview = Text("[dim]Preview unavailable[/dim]")

        node_type_label = "Process" if node_type == NodeType.PROCESS else "Directory"
        contents = Group(
            Text(f"{path}", style="bold cyan"),
            Text(f"{node_type_label} with {len(children)} entries"),
            table,
        )

        return Panel(Columns([contents, preview], expand=True), title="Contents")

    def _get_icon(self, node_type: NodeType) -> str:
        icons = {
            NodeType.DIRECTORY: "[D]",
            NodeType.PROCESS: "[P]",
            NodeType.FILE: "[F]",
            NodeType.SYMLINK: "[L]",
            NodeType.THREAD: "[T]",
        }
        return icons.get(node_type, "[ ]")
