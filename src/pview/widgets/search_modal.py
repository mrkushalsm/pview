"""Search modal for fuzzy-finding proc entries by PID or process name."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import Input, Static, Button
from textual.screen import ModalScreen
from textual import events
from textual.widget import Widget


class JumpToNode(Message):
    """Emitted when the user confirms a jump target."""

    def __init__(self, label: str) -> None:
        super().__init__()
        self.label = label


class SearchCancelled(Message):
    """Emitted when the user cancels the search."""


class SearchModal(ModalScreen):
    """Modal with a text input to search the proc tree."""

    DEFAULT_CSS = """
    SearchModal {
        layer: overlay;
        align: center middle;
    }
    SearchModal > #search-container {
        width: 60%;
        max-width: 80;
        min-width: 40;
        border: heavy $panel;
        padding: 1 2;
        background: $panel;
        margin: 3 6;
    }
    SearchModal > #search-container > Static#search-title {
        text-style: bold;
        padding-bottom: 1;
        width: 100%;
    }
    SearchModal > #search-container > Static#search-results {
        height: auto;
        max-height: 12;
        margin-top: 1;
        padding: 0 1;
    }
    SearchModal > #search-container Input {
        width: 100%;
    }
    """

    def __init__(self, labels: list[str]) -> None:
        super().__init__()
        self._labels = labels
        self._filtered: list[str] = []

    def compose(self) -> ComposeResult:
        with Vertical(id="search-container"):
            yield Static("Search by PID or name (type to filter):", id="search-title")
            yield Input(placeholder="e.g. 1234, firefox, sshd...", id="search-input")
            yield Static("", id="search-results")

    def on_mount(self) -> None:
        inp = self.query_one("#search-input", Input)
        inp.focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter the candidate list as the user types."""
        query = event.value.strip().lower()
        results: list[str] = []
        if query:
            for label in self._labels:
                if query in label.lower():
                    results.append(label)
            self._filtered = results
        else:
            self._filtered = []

        status = self.query_one("#search-results", Static)
        if query:
            if self._filtered:
                status.update("\n".join(self._filtered[:8]))
            else:
                status.update("[dim]No matches[/dim]")
        else:
            status.update("")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Jump to the first match on Enter, or use exact input."""
        query = event.value.strip()
        if not query:
            # No input: post cancel
            self.post_message(SearchCancelled())
            return

        target: str = query

        # If filtered results are available, pick the first
        if self._filtered:
            target = self._filtered[0]
        else:
            # Check if the typed string matches anything exactly (PID number)
            for label in self._labels:
                if label.startswith(query) or query == label:
                    target = label
                    break

        self.post_message(JumpToNode(target))

    async def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.post_message(SearchCancelled())
            event.stop()
