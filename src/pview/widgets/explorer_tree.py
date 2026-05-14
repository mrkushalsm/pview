"""Proc explorer tree widget helpers."""

from __future__ import annotations

from collections.abc import Callable

from textual.widgets import Tree

from pview.core.proc_tree_model import ProcTreeModel
from pview.models.proc_node import ProcNode


class ProcExplorerTree(Tree[ProcNode]):
    """Tree rooted at procfs with dynamic lazy-loaded nodes."""

    def __init__(self) -> None:
        self._model = ProcTreeModel()
        root_node = self._model.get_root()
        super().__init__(root_node.display_label(), root_node, id="explorer-tree")
        self.selection_handler: Callable[[ProcNode], None] | None = None

    def on_mount(self) -> None:
        self.root.expand()

    async def on_tree_node_expanded(self, event: Tree.NodeExpanded[ProcNode]) -> None:
        """Load and display children when a node is expanded."""
        event.stop()
        node = event.node.data
        if node is None or not node.is_expandable:
            return

        if event.node.children:
            return

        children = await self._model.get_children(node.path)
        for child in children:
            if child.is_expandable:
                event.node.add(child.display_label(), child)
            else:
                event.node.add_leaf(child.display_label(), child)

    async def on_tree_node_selected(self, event: Tree.NodeSelected[ProcNode]) -> None:
        """Handle node selection."""
        event.stop()
        node = event.node.data
        if node is not None and self.selection_handler is not None:
            self.selection_handler(node)

