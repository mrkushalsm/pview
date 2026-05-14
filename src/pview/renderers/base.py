"""Renderer interfaces and common helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from rich.console import RenderableType


class ProcRenderer(Protocol):
    """Render structured proc data or raw content into Rich output."""

    def can_render(self, path: Path) -> bool:
        """Return True if the renderer can handle the path."""

    def render(self, path: Path, content: str | None) -> RenderableType:
        """Return a Rich renderable for the given entry."""
