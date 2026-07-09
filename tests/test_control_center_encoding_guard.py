from pathlib import Path

import pytest

from scripts.control_center_encoding_guard import (
    assert_utf8_readable,
    check_utf8_readable,
    read_text_utf8_strict,
    write_text_utf8,
)


def test_encoding_guard_reads_utf8_file(tmp_path: Path) -> None:
    target = tmp_path / "control_center.md"
    write_text_utf8(target, "# Control Center\n\nencoding: utf-8\n")
    assert read_text_utf8_strict(target).startswith("# Control Center")


def test_encoding_guard_reports_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.md"
    assert check_utf8_readable([missing])[str(missing)] == "MISSING"


def test_encoding_guard_blocks_invalid_utf8(tmp_path: Path) -> None:
    target = tmp_path / "broken.md"
    target.write_bytes(b"\xff\xfe\x00")
    result = check_utf8_readable([target])[str(target)]
    assert result.startswith("UTF8_DECODE_ERROR")


def test_encoding_guard_assert_raises_on_bad_file(tmp_path: Path) -> None:
    target = tmp_path / "broken.md"
    target.write_bytes(b"\xff")
    with pytest.raises(ValueError, match="CONTROL_CENTER_ENCODING_GUARD_FAILED"):
        assert_utf8_readable([target])
