"""Parser and renderer registration for proc entries."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class ProcParser(Protocol):
    """Parse raw proc text into structured data."""

    def can_parse(self, path: Path) -> bool:
        """Return True when this parser applies."""

    def parse(self, content: str) -> object:
        """Parse text into a domain object."""


@dataclass
class ParserRegistry:
    """Simple ordered parser registry."""

    parsers: list[ProcParser]

    def select(self, path: Path) -> ProcParser | None:
        for parser in self.parsers:
            if parser.can_parse(path):
                return parser
        return None
