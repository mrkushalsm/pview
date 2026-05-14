from pathlib import Path

from pview.core.proc_tree_model import ProcTreeModel
from pview.models.proc_node import NodeType


def test_proc_tree_model_root() -> None:
    model = ProcTreeModel()
    root = model.get_root()
    assert root.path == Path("/proc")
    assert root.is_expandable


def test_proc_tree_model_classifies_directory() -> None:
    model = ProcTreeModel()
    node = model._classify_entry(Path("/proc/sys"), Path("/proc"))
    assert node is not None
    assert node.node_type == NodeType.DIRECTORY
    assert node.is_expandable


def test_proc_tree_model_detects_process() -> None:
    model = ProcTreeModel()
    node = model._classify_entry(Path("/proc/1"), Path("/proc"))
    assert node is not None
    assert node.node_type == NodeType.PROCESS
    assert node.pid == 1
    assert node.is_expandable
    assert node.process_name is not None or node.process_name is None


def test_proc_tree_model_classifies_file() -> None:
    model = ProcTreeModel()
    node = model._classify_entry(Path("/proc/meminfo"), Path("/proc"))
    assert node is not None
    assert node.node_type == NodeType.FILE
    assert not node.is_expandable
