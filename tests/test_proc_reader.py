from pathlib import Path

from pview.core.proc_reader import ProcReader


def test_proc_reader_reports_missing_entry(tmp_path: Path) -> None:
    reader = ProcReader()
    result = reader.read_text(tmp_path / "does-not-exist")

    assert result.content is None
    assert result.error == "entry disappeared"
