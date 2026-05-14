from pathlib import Path

from pview.core.parser_registry import ParserRegistry
from pview.utils.parsing import parse_key_value_line


def test_parse_key_value_line_handles_proc_format() -> None:
    assert parse_key_value_line("MemTotal:       16384256 kB") == ("MemTotal", "16384256 kB")


def test_parser_registry_selects_first_match() -> None:
    class MatchAll:
        def can_parse(self, path: Path) -> bool:
            return True

        def parse(self, content: str) -> object:
            return content

    registry = ParserRegistry([MatchAll()])
    assert registry.select(Path("/proc/meminfo")) is not None
