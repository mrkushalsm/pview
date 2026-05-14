"""Password prompt modal for sudo authentication.

Displays a centered modal with a masked input and OK/Cancel buttons.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
import logging
from textual.widgets import Button, Input, Static
from textual.widget import Widget
from textual import events
from textual.screen import ModalScreen


class PasswordSubmitted(Message):
    def __init__(self, password: str) -> None:
        super().__init__()
        self.password = password


class PasswordCancelled(Message):
    pass


class PasswordModal(ModalScreen):
    DEFAULT_CSS = """
    PasswordModal {
        layer: overlay;
        align: center middle;
    }

    PasswordModal > #pm-container {
        width: 70%;
        max-width: 100;
        min-width: 50;
        height: auto;
        border: heavy $panel;
        padding: 1 2;
        background: $panel;
        margin: 3 6; /* ensure gap from screen edges */
    }

    PasswordModal > #pm-container > Static#pm-title {
        text-style: bold;
        padding-bottom: 1;
        width: 100%;
    }

    PasswordModal > #pm-container Input {
        width: 100%;
        margin-bottom: 1;
    }

    PasswordModal > #pm-container Horizontal {
        width: 100%;
    }

    PasswordModal > #pm-container Button {
        margin-right: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="pm-container"):
            yield Static("Enter sudo password:", id="pm-title")
            yield Input(placeholder="password", password=True, id="pm-input")
            with Horizontal():
                yield Button("OK", id="pm-ok")
                yield Button("Cancel", id="pm-cancel")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Submit password when Enter is pressed."""
        try:
            pw = self.query_one("#pm-input", Input).value or ""
            logging.debug('PasswordModal: input submitted (enter)')
            self.app.post_message(PasswordSubmitted(pw))
            logging.debug('PasswordModal: posted PasswordSubmitted, returning (modal will be popped by handler)')
        except Exception:
            logging.exception('PasswordModal: error posting PasswordSubmitted')

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        try:
            if event.button.id == "pm-ok":
                pw = self.query_one("#pm-input", Input).value or ""
                logging.debug('PasswordModal: OK button pressed')
                self.app.post_message(PasswordSubmitted(pw))
                logging.debug('PasswordModal: posted PasswordSubmitted')
            else:
                logging.debug('PasswordModal: Cancel button pressed')
                self.app.post_message(PasswordCancelled())
                logging.debug('PasswordModal: posted PasswordCancelled')
        except Exception:
            logging.exception('PasswordModal: error posting button message')

    async def on_mount(self) -> None:
        # focus the input when mounted
        self.query_one("#pm-input", Input).focus()

    async def on_key(self, event: events.Key) -> None:
        # Close modal on Escape
        if event.key == "escape":
            try:
                logging.debug('PasswordModal: Escape pressed')
                self.app.post_message(PasswordCancelled())
                logging.debug('PasswordModal: posted PasswordCancelled (escape)')
            except Exception:
                logging.exception('PasswordModal: error posting escape cancel')
            event.stop()
