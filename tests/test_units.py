from pview.utils.units import kib_to_human


def test_kib_to_human_handles_none() -> None:
    assert kib_to_human(None) == "n/a"


def test_kib_to_human_formats_binary_units() -> None:
    assert kib_to_human(1536) == "1.5 MiB"
