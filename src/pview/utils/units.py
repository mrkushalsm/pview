"""Human-readable unit helpers."""

from __future__ import annotations


def kib_to_human(value: int | None) -> str:
    """Format kibibytes using binary units."""

    if value is None:
        return "n/a"
    suffixes = ["KiB", "MiB", "GiB", "TiB"]
    amount = float(value)
    index = 0
    while amount >= 1024 and index < len(suffixes) - 1:
        amount /= 1024
        index += 1
    return f"{amount:.1f} {suffixes[index]}"
