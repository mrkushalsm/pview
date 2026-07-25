"""Proc explorer tree widget helpers."""

from __future__ import annotations

from collections.abc import Callable

from textual.widgets import Tree
from textual.widgets._tree import TreeNode

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

    def collect_labels(self) -> list[str]:
        """Walk the current tree and collect all visible node labels."""
        labels: list[str] = []
        self._walk(self.root, labels)
        return labels

    def _walk(self, node: TreeNode[ProcNode], labels: list[str]) -> None:
        if node.label is not None:
            labels.append(str(node.label))
        for child in node.children:
            self._walk(child, labels)

    def jump_to_label(self, label: str) -> None:
        """Focus and select the tree node matching the given label."""
        target = self._find_by_label(self.root, label)
        if target is not None:
            # Expand path to target
            path: list[TreeNode[ProcNode]] = []
            node: TreeNode[ProcNode] | None = target
            while node is not None:
                path.append(node)
                node = node.parent
            for ancestor in reversed(path):
                ancestor.expand()
            # Scroll to and select the target
            self.select_node(target)
            self.scroll_to_node(target)
            # Fire selection handler
            data = target.data
            if data is not None and self.selection_handler is not None:
                self.selection_handler(data)

    def _find_by_label(self, node: TreeNode[ProcNode], label: str) -> TreeNode[ProcNode] | None:
        if str(node.label) == label:
            return node
        for child in node.children:
            found = self._find_by_label(child, label)
            if found is not None:
                return found
        return None
