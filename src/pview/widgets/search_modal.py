"""Search modal for fuzzy-finding proc entries by PID or process name.

Keyboard-driven UX: type to filter, arrows to navigate results, Enter to jump.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import Input, Static
from textual.screen import ModalScreen
from textual import events


class JumpToNode(Message):
    """Emitted when the user confirms a jump target."""

    def __init__(self, label: str) -> None:
        super().__init__()
        self.label = label


class SearchCancelled(Message):
    """Emitted when the user cancels the search."""


class SearchModal(ModalScreen):
    """Modal with input + selectable result list for proc tree navigation."""

    DEFAULT_CSS = """
    SearchModal {
        layer: overlay;
        align: center middle;
    }
    SearchModal > #search-container {
        width: 60%;
        max-width: 80;
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
    SearchModal > #search-container Input {
        width: 100%;
        margin-bottom: 1;
    }
    #search-results {
        height: auto;
        max-height: 12;
        padding: 0 1;
    }
    .result-line {
        padding: 0 1;
    }
    .result-line.highlighted {
        background: $accent;
        color: $text;
    }
    """

    def __init__(self, labels: list[str]) -> None:
        super().__init__()
        self._labels = labels
        self._filtered: list[str] = []
        self._cursor: int = 0

    def compose(self) -> ComposeResult:
        with Vertical(id="search-container"):
            yield Static("Search: type PID or name, arrows to pick, Enter to jump, Esc to cancel", id="search-title")
            yield Input(placeholder="e.g. 1234, firefox, sshd...", id="search-input")
            yield Static("", id="search-results")

    def on_mount(self) -> None:
        inp = self.query_one("#search-input", Input)
        inp.focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Filter candidates and reset cursor."""
        query = event.value.strip().lower()
        if query:
            self._filtered = [lbl for lbl in self._labels if query in lbl.lower()]
        else:
            self._filtered = list(self._labels)
        self._cursor = 0
        self._render_results()

    def _render_results(self) -> None:
        """Render the filtered list with cursor highlight."""
        status = self.query_one("#search-results", Static)
        if not self._filtered:
            status.update("[dim]No matches[/dim]")
            return

        lines: list[str] = []
        for idx, label in enumerate(self._filtered):
            if idx >= 12:
                break
            if idx == self._cursor:
                lines.append(f"[reverse] {label} [/reverse]")
            else:
                lines.append(f"  {label}")
        status.update("\n".join(lines))

    def _clamp_cursor(self) -> None:
        if self._filtered:
            self._cursor = max(0, min(self._cursor, len(self._filtered) - 1))
        else:
            self._cursor = 0

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Enter pressed: jump to the cursor-selected match."""
        query = event.value.strip()
        if not query:
            self.post_message(SearchCancelled())
            return

        if self._filtered:
            target = self._filtered[self._cursor]
            self.post_message(JumpToNode(target))
            return

        # No results: try matching raw input against labels as fallback
        for label in self._labels:
            if label.lower().startswith(query.lower()):
                self.post_message(JumpToNode(label))
                return

        self.post_message(SearchCancelled())

    async def on_key(self, event: events.Key) -> None:
        if event.key == "down":
            self._cursor += 1
            self._clamp_cursor()
            self._render_results()
            event.stop()
        elif event.key == "up":
            self._cursor -= 1
            self._clamp_cursor()
            self._render_results()
            event.stop()
        elif event.key == "escape":
            self.post_message(SearchCancelled())
            event.stop()
