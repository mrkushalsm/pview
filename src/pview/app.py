"""Textual application shell for pview."""

from __future__ import annotations

import asyncio
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Footer, Header, Static

from pview.core.proc_tree_model import ProcTreeModel
from pview.models.proc_node import NodeType, ProcNode
from pview.renderers.directory_renderer import DirectoryRenderer
from pview.renderers.registry import RendererRegistry
from pview.widgets.explorer_tree import ProcExplorerTree
from pview.widgets.password_modal import PasswordModal, PasswordSubmitted, PasswordCancelled
import logging

# Simple file logger for debugging UI flow
logging.basicConfig(filename='/tmp/pview.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')
from textual.message import Message


class ShowPasswordRequest(Message):
    """Message to request the password modal be shown from the event loop."""
    pass


class DetailPane(Static):
    """Context-aware rendering area placeholder."""


class StatusBar(Static):
    """Bottom status line placeholder."""


class PViewApp(App[None]):
    """pview terminal explorer."""

    CSS = """
    Screen {
        layout: vertical;
    }

    #main-area {
        height: 1fr;
    }

    #explorer-tree {
        width: 32%;
        min-width: 28;
        border: solid $panel;
    }

    #detail-pane {
        width: 1fr;
        border: solid $panel;
        padding: 1 2;
    }

    #status-bar {
        height: 1;
        dock: bottom;
        background: $boost;
        color: $text;
    }
    """

    TITLE = "pview"
    SUB_TITLE = "Linux /proc explorer"
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("ctrl+h", "toggle_help", "Help"),
        Binding("/", "search", "Search"),
        Binding("b", "bookmark", "Bookmark"),
        Binding("space", "toggle_live", "Live"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._tree_model = ProcTreeModel()
        self._renderers = RendererRegistry()
        self._dir_renderer = DirectoryRenderer(
            model=self._tree_model,
            reader=self._tree_model.reader,
            registry=self._renderers,
        )
        self._last_node: ProcNode | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main-area"):
            yield ProcExplorerTree()
            yield DetailPane("Select a /proc entry to inspect it.", id="detail-pane")
        yield StatusBar("Ready. Arrow keys, vim keys, Enter, Backspace. Esc: close modal", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        tree = self.query_one(ProcExplorerTree)
        tree.selection_handler = self._show_entry

    def _show_entry(self, node: ProcNode) -> None:
        detail = self.query_one(DetailPane)
        status = self.query_one(StatusBar)
        self._last_node = node

        if node.node_type in (NodeType.DIRECTORY, NodeType.PROCESS):
            renderable = self._dir_renderer.render(node.path, node.node_type)
            detail.update(renderable)
            status.update(f"{node.path}: directory")
        elif node.node_type == NodeType.SYMLINK:
            result = self._tree_model.reader.read_link(node.path)
            renderable = self._renderers.render(node.path, result.content)
            detail.update(renderable)
            if result.error is not None:
                # If permission denied, prompt password modal automatically
                if result.error == "permission denied" and not self._tree_model._reader.sudo._has_cached():
                    # Push the password modal as a screen so it floats centered
                    # Post a message so the async message handler can await push_screen
                    self.post_message(ShowPasswordRequest())
                    status.update(f"{node.path}: permission required")
                    return
                status.update(f"{node.path}: {result.error}")
            else:
                status.update(f"{node.path}: link -> {result.content}")
        else:
            result = self._tree_model.reader.read_text(node.path)
            renderable = self._renderers.render(node.path, result.content)
            detail.update(renderable)
            if result.error is not None:
                # If permission denied, prompt password modal automatically
                if result.error == "permission denied" and not self._tree_model._reader.sudo._has_cached():
                    self.post_message(ShowPasswordRequest())
                    status.update(f"{node.path}: permission required")
                    return
                status.update(f"{node.path}: {result.error}")
            else:
                status.update(f"{node.path}: loaded")

    async def on_password_submitted(self, message: PasswordSubmitted) -> None:
        status = self.query_one(StatusBar)
        password = message.password
        logging.debug('Password submitted received (start handler)')
        if not password:
            status.update("Sudo: no password entered")
            logging.debug('[pop-cancel] dismissing modal: no password')
            self.pop_screen()
            return
        try:
            # Run the blocking password verification in a thread to avoid freezing the event loop
            logging.debug('[1] Verifying sudo password...')
            ok = await asyncio.to_thread(self._tree_model._reader.sudo.cache_password, password)
            logging.debug('[2] cache_password returned: %s', ok)
            if not ok:
                status.update("Sudo: authentication failed")
                logging.debug('[pop-fail] dismissing modal: auth failed')
                self.pop_screen()
                return
            logging.debug('[3] About to call _perform_retry')
            status.update("Sudo: authenticated, retrying read...")
            await self._perform_retry()
            logging.debug('[4] perform_retry completed, handler returning')
            logging.debug('[pop-success] dismissing modal: retry complete')
            self.pop_screen()
        except Exception:
            logging.exception('Error in on_password_submitted')
            status.update('Sudo: unexpected error')
            logging.debug('[pop-error] dismissing modal: exception')
            self.pop_screen()

    async def on_password_cancelled(self, message: PasswordCancelled) -> None:
        status = self.query_one(StatusBar)
        logging.debug('Password cancelled')
        status.update("Sudo: cancelled")
        logging.debug('[pop-cancel-handler] dismissing modal')
        self.pop_screen()

    async def _perform_retry(self) -> None:
        """Async retry that runs blocking reads in a background thread, then updates UI."""
        logging.debug('[retry-start] _perform_retry called')
        node = self._last_node
        if node is None:
            logging.debug('[retry-skip] no last node')
            return
        detail = self.query_one(DetailPane)
        status = self.query_one(StatusBar)
        logging.debug('[retry-setup] queried widgets')

        if node.node_type in (NodeType.DIRECTORY, NodeType.PROCESS):
            renderable = self._dir_renderer.render(node.path, node.node_type)
            detail.update(renderable)
            status.update(f"{node.path}: directory")
            logging.debug('[retry-done-dir] directory rendered')
            return

        logging.debug('[retry-file] reading file: %s', node.path)

        def _do_read() -> tuple[object, object]:
            logging.debug('[retry-thread-start] in background thread')
            if node.node_type == NodeType.SYMLINK:
                result = self._tree_model.reader.read_link(node.path)
            else:
                result = self._tree_model.reader.read_text(node.path)
            logging.debug('[retry-thread-read] got result: error=%s', result.error)
            renderable = self._renderers.render(node.path, result.content)
            logging.debug('[retry-thread-render] rendered')
            return result, renderable

        logging.debug('[retry-before-thread] about to call to_thread')
        try:
            result, renderable = await asyncio.to_thread(_do_read)
            logging.debug('[retry-after-thread] got renderable')
            logging.debug('[retry-before-update] calling detail.update')
            detail.update(renderable)
            logging.debug('[retry-after-update] detail.update returned')
            if result.error is not None:
                status.update(f"{node.path}: {result.error}")
            else:
                status.update(f"{node.path}: loaded (sudo)")
            logging.debug('[retry-end-success] all updates done')
        except Exception:
            logging.exception('Error during _perform_retry')
            status.update(f"{node.path}: error during retry")

    async def on_show_password_request(self, message: ShowPasswordRequest) -> None:
        # Show the modal; ModalScreen push must be awaited from an async handler
        logging.debug('ShowPasswordRequest received, pushing modal')
        await self.push_screen(PasswordModal())
        logging.debug('Modal pushed')

    def action_toggle_help(self) -> None:
        self.notify("Help screen will be added in the next iteration.")

    def action_search(self) -> None:
        self.notify("Search palette will be added in the next iteration.")

    def action_bookmark(self) -> None:
        self.notify("Bookmark support will be added in the next iteration.")

    def action_toggle_live(self) -> None:
        self.notify("Live mode hook reserved for refresh engine integration.")


def main() -> None:
    """Run the application."""

    PViewApp().run()
