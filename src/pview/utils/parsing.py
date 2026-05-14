"""Shared parsing helpers."""

from __future__ import annotations


def parse_key_value_line(line: str) -> tuple[str, str] | None:
    """Parse a Linux-style key/value line separated by a colon."""

    if ":" not in line:
        return None
    key, value = line.split(":", 1)
    return key.strip(), value.strip()
