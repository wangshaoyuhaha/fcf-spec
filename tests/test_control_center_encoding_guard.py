from pathlib import Path

import pytest

from scripts.control_center_encoding_guard import (
    assert_encoding_probe_no_block,
    assert_guard_registry_ok,
    assert_utf8_readable,
    build_encoding_probe_report,
    build_guard_registry,
    check_utf8_readable,
    classify_guarded_file,
    detect_newline_style,
    discover_guarded_files,
    probe_encoding_file,
    read_text_utf8_strict,
    summarize_guard_registry,
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


def test_classify_guarded_files() -> None:
    assert classify_guarded_file("docs/FCF_PROJECT_CONTROL_CENTER.md") == "CONTROL_CENTER"
    assert classify_guarded_file("FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md") == "BACKEND_HANDOFF"
    assert classify_guarded_file("FCF_NEW_WINDOW_CHAT_PROMPT.md") == "NEW_WINDOW_PROMPT"
    assert classify_guarded_file("FCF_FINAL_ARCHITECTURE_GAP_AUDIT_REPORT.md") == "FINAL_AUDIT"
    assert classify_guarded_file("FCF_CURRENT_STATE_TEST_APP_1_FINAL.md") == "FINAL_CURRENT_STATE"


def test_discover_guarded_files_includes_defaults_audit_and_final_state(tmp_path: Path) -> None:
    write_text_utf8(tmp_path / "FCF_CURRENT_STATE_TEST_APP_1_FINAL.md", "# Final State\n")
    guarded = discover_guarded_files(tmp_path)
    assert "docs/FCF_PROJECT_CONTROL_CENTER.md" in guarded
    assert "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md" in guarded
    assert "FCF_NEW_WINDOW_CHAT_PROMPT.md" in guarded
    assert "FCF_FINAL_ARCHITECTURE_GAP_AUDIT_REPORT.md" in guarded
    assert "FCF_CURRENT_STATE_TEST_APP_1_FINAL.md" in guarded


def test_build_guard_registry_marks_status_and_policy(tmp_path: Path) -> None:
    write_text_utf8(tmp_path / "docs" / "FCF_PROJECT_CONTROL_CENTER.md", "# Control\n")
    write_text_utf8(tmp_path / "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md", "# Handoff\n")
    write_text_utf8(tmp_path / "FCF_NEW_WINDOW_CHAT_PROMPT.md", "# Prompt\n")
    write_text_utf8(tmp_path / "FCF_FINAL_ARCHITECTURE_GAP_AUDIT_REPORT.md", "# Audit\n")
    write_text_utf8(tmp_path / "FCF_CURRENT_STATE_TEST_APP_1_FINAL.md", "# Final\n")

    records = build_guard_registry(tmp_path)
    status_by_path = {record.path: record.encoding_status for record in records}
    assert status_by_path["docs/FCF_PROJECT_CONTROL_CENTER.md"] == "OK"
    assert status_by_path["FCF_CURRENT_STATE_TEST_APP_1_FINAL.md"] == "OK"
    assert {record.write_policy for record in records} == {"UTF8_LF_ONLY"}
    assert {record.safety_scope for record in records} == {"PAPER_ONLY_LOCAL_ONLY_READ_ONLY_SIDECAR_ONLY"}


def test_guard_registry_summary_counts_missing_and_ok(tmp_path: Path) -> None:
    write_text_utf8(tmp_path / "docs" / "FCF_PROJECT_CONTROL_CENTER.md", "# Control\n")
    records = build_guard_registry(tmp_path)
    summary = summarize_guard_registry(records)
    assert summary["OK"] == 1
    assert summary["MISSING"] >= 3


def test_assert_guard_registry_ok_blocks_invalid_utf8(tmp_path: Path) -> None:
    write_text_utf8(tmp_path / "docs" / "FCF_PROJECT_CONTROL_CENTER.md", "# Control\n")
    write_text_utf8(tmp_path / "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md", "# Handoff\n")
    write_text_utf8(tmp_path / "FCF_NEW_WINDOW_CHAT_PROMPT.md", "# Prompt\n")
    write_text_utf8(tmp_path / "FCF_FINAL_ARCHITECTURE_GAP_AUDIT_REPORT.md", "# Audit\n")
    (tmp_path / "FCF_CURRENT_STATE_TEST_APP_1_FINAL.md").write_bytes(b"\xff")

    records = build_guard_registry(tmp_path)
    with pytest.raises(ValueError, match="CONTROL_CENTER_ENCODING_REGISTRY_FAILED"):
        assert_guard_registry_ok(records)


def test_detect_newline_style() -> None:
    assert detect_newline_style(b"") == "EMPTY"
    assert detect_newline_style(b"a\nb\n") == "LF"
    assert detect_newline_style(b"a\r\nb\r\n") == "CRLF"
    assert detect_newline_style(b"a\r\nb\n") == "MIXED"
    assert detect_newline_style(b"abc") == "NO_NEWLINE"


def test_probe_encoding_file_detects_lf_utf8(tmp_path: Path) -> None:
    target = tmp_path / "ok.md"
    write_text_utf8(target, "# OK\n")
    record = probe_encoding_file(target)
    assert record.exists is True
    assert record.strict_utf8_status == "OK"
    assert record.has_utf8_bom is False
    assert record.newline_style == "LF"
    assert record.guard_status == "PASS"


def test_probe_encoding_file_warns_bom(tmp_path: Path) -> None:
    target = tmp_path / "bom.md"
    target.write_bytes(b"\xef\xbb\xbf# BOM\n")
    record = probe_encoding_file(target)
    assert record.strict_utf8_status == "OK"
    assert record.has_utf8_bom is True
    assert record.guard_status == "WARN_BOM"


def test_probe_encoding_file_blocks_invalid_utf8(tmp_path: Path) -> None:
    target = tmp_path / "broken.md"
    target.write_bytes(b"\xff")
    record = probe_encoding_file(target)
    assert record.strict_utf8_status.startswith("UTF8_DECODE_ERROR")
    assert record.guard_status == "BLOCK"


def test_build_encoding_probe_report_and_assert(tmp_path: Path) -> None:
    write_text_utf8(tmp_path / "docs" / "FCF_PROJECT_CONTROL_CENTER.md", "# Control\n")
    write_text_utf8(tmp_path / "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md", "# Handoff\n")
    write_text_utf8(tmp_path / "FCF_NEW_WINDOW_CHAT_PROMPT.md", "# Prompt\n")
    write_text_utf8(tmp_path / "FCF_FINAL_ARCHITECTURE_GAP_AUDIT_REPORT.md", "# Audit\n")
    write_text_utf8(tmp_path / "FCF_CURRENT_STATE_TEST_APP_1_FINAL.md", "# Final\n")

    records = build_encoding_probe_report(tmp_path)
    assert {record.guard_status for record in records} == {"PASS"}
    assert_encoding_probe_no_block(records)


def test_assert_encoding_probe_no_block_raises(tmp_path: Path) -> None:
    write_text_utf8(tmp_path / "docs" / "FCF_PROJECT_CONTROL_CENTER.md", "# Control\n")
    write_text_utf8(tmp_path / "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md", "# Handoff\n")
    write_text_utf8(tmp_path / "FCF_NEW_WINDOW_CHAT_PROMPT.md", "# Prompt\n")
    write_text_utf8(tmp_path / "FCF_FINAL_ARCHITECTURE_GAP_AUDIT_REPORT.md", "# Audit\n")
    (tmp_path / "FCF_CURRENT_STATE_TEST_APP_1_FINAL.md").write_bytes(b"\xff")

    records = build_encoding_probe_report(tmp_path)
    with pytest.raises(ValueError, match="CONTROL_CENTER_ENCODING_PROBE_BLOCKED"):
        assert_encoding_probe_no_block(records)