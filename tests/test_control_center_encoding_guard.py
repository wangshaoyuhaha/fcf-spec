from pathlib import Path

import pytest

from scripts.control_center_encoding_guard import (
    append_section_utf8_lf,
    assert_encoding_probe_no_block,
    assert_guard_registry_ok,
    assert_safe_write_result_ok,
    assert_utf8_readable,
    atomic_write_utf8_lf,
    build_encoding_probe_report,
    build_guard_registry,
    check_utf8_readable,
    classify_guarded_file,
    detect_newline_style,
    discover_guarded_files,
    normalize_lf,
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


def test_normalize_lf() -> None:
    assert normalize_lf("a\r\nb\rc\n") == "a\nb\nc\n"


def test_atomic_write_utf8_lf_creates_utf8_lf_file(tmp_path: Path) -> None:
    target = tmp_path / "safe.md"
    result = atomic_write_utf8_lf(target, "# Safe\r\n\r\nbody\r\n")
    assert_safe_write_result_ok(result)
    assert read_text_utf8_strict(target) == "# Safe\n\nbody\n"
    assert probe_encoding_file(target).newline_style == "LF"


def test_atomic_write_utf8_lf_creates_backup(tmp_path: Path) -> None:
    target = tmp_path / "safe.md"
    write_text_utf8(target, "old\n")
    result = atomic_write_utf8_lf(target, "new\n", create_backup=True)
    assert result.backup_created is True
    assert (tmp_path / "safe.md.bak").read_text(encoding="utf-8") == "old\n"


def test_append_section_utf8_lf_is_idempotent(tmp_path: Path) -> None:
    target = tmp_path / "control.md"
    write_text_utf8(target, "# Control\n")
    first = append_section_utf8_lf(target, "Encoding Guard", "status: ok")
    second = append_section_utf8_lf(target, "Encoding Guard", "status: ok")
    assert first.atomic_write is True
    assert second.atomic_write is False
    text = read_text_utf8_strict(target)
    assert text.count("## Encoding Guard") == 1


def test_assert_safe_write_result_ok_blocks_bad_result(tmp_path: Path) -> None:
    target = tmp_path / "safe.md"
    result = atomic_write_utf8_lf(target, "ok\n")
    assert_safe_write_result_ok(result)

def _write_complete_guard_fixture(tmp_path: Path) -> None:
    write_text_utf8(tmp_path / "docs" / "FCF_PROJECT_CONTROL_CENTER.md", "# Control\n")
    write_text_utf8(tmp_path / "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md", "# Handoff\n")
    write_text_utf8(tmp_path / "FCF_NEW_WINDOW_CHAT_PROMPT.md", "# Prompt\n")
    write_text_utf8(tmp_path / "FCF_FINAL_ARCHITECTURE_GAP_AUDIT_REPORT.md", "# Audit\n")
    write_text_utf8(tmp_path / "FCF_CURRENT_STATE_TEST_APP_1_FINAL.md", "# Final\n")


def test_build_encoding_guard_packet_counts(tmp_path: Path) -> None:
    from scripts.control_center_encoding_guard import (
        assert_encoding_guard_packet_ok,
        build_encoding_guard_packet,
    )

    _write_complete_guard_fixture(tmp_path)
    packet = build_encoding_guard_packet(tmp_path)

    assert packet.stage_id == "CONTROL-CENTER-ENCODING-GUARD-APP-1-D5"
    assert packet.registry_total == 5
    assert packet.probe_total == 5
    assert packet.ok_count == 5
    assert packet.warn_count == 0
    assert packet.block_count == 0
    assert packet.operator_review_required is True
    assert packet.real_execution_allowed is False
    assert packet.trade_action_enabled is False
    assert_encoding_guard_packet_ok(packet)


def test_write_encoding_guard_packet_json(tmp_path: Path) -> None:
    import json

    from scripts.control_center_encoding_guard import write_encoding_guard_packet

    _write_complete_guard_fixture(tmp_path)
    output = tmp_path / "encoding_guard_packet.json"
    result = write_encoding_guard_packet(tmp_path, output)

    assert result.guard_status == "PASS"
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["stage_id"] == "CONTROL-CENTER-ENCODING-GUARD-APP-1-D5"
    assert payload["real_execution_allowed"] is False
    assert payload["trade_action_enabled"] is False


def test_write_encoding_guard_packet_markdown(tmp_path: Path) -> None:
    from scripts.control_center_encoding_guard import write_encoding_guard_packet_md

    _write_complete_guard_fixture(tmp_path)
    output = tmp_path / "encoding_guard_packet.md"
    result = write_encoding_guard_packet_md(tmp_path, output)

    assert result.guard_status == "PASS"
    text = output.read_text(encoding="utf-8")
    assert "# CONTROL-CENTER-ENCODING-GUARD-APP-1 D5 Packet" in text
    assert "- operator_review_required: true" in text
    assert "- real_execution_allowed: false" in text
    assert "- trade_action_enabled: false" in text


def test_encoding_guard_packet_blocks_bad_file(tmp_path: Path) -> None:
    from scripts.control_center_encoding_guard import (
        assert_encoding_guard_packet_ok,
        build_encoding_guard_packet,
    )

    _write_complete_guard_fixture(tmp_path)
    (tmp_path / "FCF_CURRENT_STATE_TEST_APP_1_FINAL.md").write_bytes(b"\xff")
    packet = build_encoding_guard_packet(tmp_path)

    assert packet.block_count == 1
    with pytest.raises(ValueError, match="CONTROL_CENTER_ENCODING_GUARD_PACKET_BLOCKED"):
        assert_encoding_guard_packet_ok(packet)


def test_build_encoding_guard_closeout_safe() -> None:
    from scripts.control_center_encoding_guard import (
        assert_encoding_guard_closeout_safe,
        build_encoding_guard_closeout,
    )

    closeout = build_encoding_guard_closeout()

    assert closeout.app_id == "CONTROL-CENTER-ENCODING-GUARD-APP-1"
    assert closeout.final_status == "READY_FOR_MAIN_MERGE"
    assert closeout.merge_ready is True
    assert closeout.paper_only is True
    assert closeout.local_only is True
    assert closeout.read_only is True
    assert closeout.sidecar_only is True
    assert closeout.operator_review_required is True
    assert closeout.no_real_trading is True
    assert closeout.no_tag_release_deploy is True
    assert len(closeout.completed_stages) == 6
    assert_encoding_guard_closeout_safe(closeout)


def test_render_encoding_guard_closeout_md_contains_required_boundary() -> None:
    from scripts.control_center_encoding_guard import (
        build_encoding_guard_closeout,
        render_encoding_guard_closeout_md,
    )

    text = render_encoding_guard_closeout_md(build_encoding_guard_closeout())

    assert "# CONTROL-CENTER-ENCODING-GUARD-APP-1 D6 Final Closeout" in text
    assert "- paper_only: true" in text
    assert "- local_only: true" in text
    assert "- read_only: true" in text
    assert "- sidecar_only: true" in text
    assert "- operator_review_required: true" in text
    assert "- no_real_trading: true" in text
    assert "- no_tag_release_deploy: true" in text


def test_write_encoding_guard_closeout_md(tmp_path: Path) -> None:
    from scripts.control_center_encoding_guard import write_encoding_guard_closeout_md

    output = tmp_path / "closeout.md"
    result = write_encoding_guard_closeout_md(output)

    assert result.guard_status == "PASS"
    assert output.read_text(encoding="utf-8").startswith("# CONTROL-CENTER-ENCODING-GUARD-APP-1 D6 Final Closeout")


def test_encoding_guard_closeout_stage_names() -> None:
    from scripts.control_center_encoding_guard import build_encoding_guard_closeout

    closeout = build_encoding_guard_closeout()
    joined = "\n".join(closeout.completed_stages)

    assert "D1 strict UTF-8 guard contract" in joined
    assert "D2 guarded source registry" in joined
    assert "D3 read-only encoding probe" in joined
    assert "D4 UTF-8 LF safe writer" in joined
    assert "D5 encoding guard packet" in joined
    assert "D6 final workflow handoff and closeout" in joined
