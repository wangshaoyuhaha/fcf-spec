import pytest

from scripts.control_center_completion_index_guard import (
    assert_completion_index_entry_pass,
    assert_completion_index_uniqueness_pass,
    validate_completion_index_entry,
    validate_completion_index_uniqueness,
)


def _complete_entry() -> dict[str, str]:
    return {
        "app_id": "CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1",
        "status": "completed",
        "branch": "sidecar-control-center-completion-index-guard-app-1",
        "main_merge_commit": "123abcd merge APP into main",
        "final_branch_commit": "456def0 add D6 final closeout",
        "final_current_state_commit": "789abcd add final current state",
        "final_current_state_file": "FCF_CURRENT_STATE_CONTROL_CENTER_COMPLETION_INDEX_GUARD_APP_1_FINAL.md",
        "validation": "1741 passed",
        "git_status": "clean",
        "origin_main": "synced",
        "tag": "none",
        "release": "none",
        "deploy": "none",
    }


def test_validate_completion_index_entry_passes_complete_record() -> None:
    result = validate_completion_index_entry(_complete_entry())

    assert result.status == "PASS"
    assert result.missing_keys == []
    assert result.invalid_values == []
    assert_completion_index_entry_pass(result)


def test_validate_completion_index_entry_blocks_missing_keys() -> None:
    result = validate_completion_index_entry({"app_id": "APP"})

    assert result.status == "BLOCK"
    assert "status" in result.missing_keys
    assert "main_merge_commit" in result.missing_keys
    assert "final_current_state_file" in result.missing_keys


def test_validate_completion_index_entry_blocks_bad_status() -> None:
    record = _complete_entry()
    record["status"] = "done"

    result = validate_completion_index_entry(record)

    assert result.status == "BLOCK"
    assert "status:INVALID" in result.invalid_values


def test_validate_completion_index_entry_blocks_bad_commit() -> None:
    record = _complete_entry()
    record["main_merge_commit"] = "not-a-commit"

    result = validate_completion_index_entry(record)

    assert result.status == "BLOCK"
    assert "main_merge_commit:INVALID_COMMIT" in result.invalid_values


def test_validate_completion_index_entry_blocks_bad_final_state_file() -> None:
    record = _complete_entry()
    record["final_current_state_file"] = "bad_file.txt"

    result = validate_completion_index_entry(record)

    assert result.status == "BLOCK"
    assert "final_current_state_file:INVALID_NAME" in result.invalid_values


def test_validate_completion_index_entry_blocks_dirty_or_unsynced() -> None:
    record = _complete_entry()
    record["git_status"] = "dirty"
    record["origin_main"] = "behind"

    result = validate_completion_index_entry(record)

    assert result.status == "BLOCK"
    assert "git_status:MUST_BE_CLEAN" in result.invalid_values
    assert "origin_main:MUST_BE_SYNCED" in result.invalid_values


def test_validate_completion_index_entry_blocks_tag_release_deploy() -> None:
    record = _complete_entry()
    record["tag"] = "v1"
    record["release"] = "v1"
    record["deploy"] = "prod"

    result = validate_completion_index_entry(record)

    assert result.status == "BLOCK"
    assert "tag:MUST_BE_NONE" in result.invalid_values
    assert "release:MUST_BE_NONE" in result.invalid_values
    assert "deploy:MUST_BE_NONE" in result.invalid_values


def test_assert_completion_index_entry_pass_raises_on_block() -> None:
    result = validate_completion_index_entry({"app_id": "APP"})

    with pytest.raises(ValueError, match="CONTROL_CENTER_COMPLETION_INDEX_ENTRY_FAILED"):
        assert_completion_index_entry_pass(result)


def test_validate_completion_index_uniqueness_passes_unique_records() -> None:
    first = _complete_entry()
    second = _complete_entry()
    second["app_id"] = "OTHER-APP-1"
    second["final_current_state_file"] = "FCF_CURRENT_STATE_OTHER_APP_1_FINAL.md"

    result = validate_completion_index_uniqueness([first, second])

    assert result.status == "PASS"
    assert result.duplicate_app_ids == []
    assert result.duplicate_final_state_files == []
    assert_completion_index_uniqueness_pass(result)


def test_validate_completion_index_uniqueness_blocks_duplicates() -> None:
    first = _complete_entry()
    second = _complete_entry()

    result = validate_completion_index_uniqueness([first, second])

    assert result.status == "BLOCK"
    assert "CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1" in result.duplicate_app_ids
    assert "FCF_CURRENT_STATE_CONTROL_CENTER_COMPLETION_INDEX_GUARD_APP_1_FINAL.md" in result.duplicate_final_state_files

    with pytest.raises(ValueError, match="CONTROL_CENTER_COMPLETION_INDEX_DUPLICATE_FAILED"):
        assert_completion_index_uniqueness_pass(result)

from pathlib import Path


def test_classify_completion_source() -> None:
    from scripts.control_center_completion_index_guard import classify_completion_source

    assert classify_completion_source("docs/FCF_PROJECT_CONTROL_CENTER.md") == "CONTROL_CENTER"
    assert classify_completion_source("FCF_CURRENT_STATE_TEST_APP_1_FINAL.md") == "FINAL_CURRENT_STATE"
    assert classify_completion_source("docs/OTHER.md") == "GOVERNANCE_DOCUMENT"


def test_classify_completion_source_absolute_control_center_path(tmp_path: Path) -> None:
    from scripts.control_center_completion_index_guard import classify_completion_source

    target = tmp_path / "docs" / "FCF_PROJECT_CONTROL_CENTER.md"

    assert classify_completion_source(target) == "CONTROL_CENTER"


def test_extract_completion_key_values() -> None:
    from scripts.control_center_completion_index_guard import extract_completion_key_values

    text = """
# Header

app_id: TEST-APP-1
- git status: clean
- origin/main: synced
Final Current-State File: FCF_CURRENT_STATE_TEST_APP_1_FINAL.md
"""

    fields = extract_completion_key_values(text)

    assert fields["app_id"] == "TEST-APP-1"
    assert fields["git_status"] == "clean"
    assert fields["origin_main"] == "synced"
    assert fields["final_current_state_file"] == "FCF_CURRENT_STATE_TEST_APP_1_FINAL.md"


def test_discover_completion_sources(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "FCF_PROJECT_CONTROL_CENTER.md").write_text("# Control\n", encoding="utf-8")
    (tmp_path / "FCF_CURRENT_STATE_TEST_APP_1_FINAL.md").write_text("# Final\n", encoding="utf-8")

    from scripts.control_center_completion_index_guard import discover_completion_sources

    sources = discover_completion_sources(tmp_path)

    assert "docs/FCF_PROJECT_CONTROL_CENTER.md" in sources
    assert "FCF_CURRENT_STATE_TEST_APP_1_FINAL.md" in sources


def test_load_completion_source_reads_utf8_and_fields(tmp_path: Path) -> None:
    target = tmp_path / "FCF_CURRENT_STATE_TEST_APP_1_FINAL.md"
    target.write_text("app_id: TEST\nstatus: completed\n", encoding="utf-8")

    from scripts.control_center_completion_index_guard import load_completion_source

    record = load_completion_source(target)

    assert record.exists is True
    assert record.utf8_status == "OK"
    assert record.source_kind == "FINAL_CURRENT_STATE"
    assert record.extracted_fields["app_id"] == "TEST"


def test_load_completion_source_reports_invalid_utf8(tmp_path: Path) -> None:
    target = tmp_path / "FCF_CURRENT_STATE_BAD.md"
    target.write_bytes(b"\xff")

    from scripts.control_center_completion_index_guard import load_completion_source

    record = load_completion_source(target)

    assert record.exists is True
    assert record.utf8_status == "UTF8_DECODE_ERROR"
    assert record.extracted_fields == {}


def test_load_and_summarize_completion_sources(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "FCF_PROJECT_CONTROL_CENTER.md").write_text("status: completed\n", encoding="utf-8")
    (tmp_path / "FCF_CURRENT_STATE_TEST_APP_1_FINAL.md").write_text("app_id: TEST\n", encoding="utf-8")

    from scripts.control_center_completion_index_guard import (
        assert_completion_sources_readable,
        load_completion_sources,
        summarize_completion_sources,
    )

    records = load_completion_sources(tmp_path)
    summary = summarize_completion_sources(records)

    assert len(records) == 2
    assert summary["CONTROL_CENTER:OK"] == 1
    assert summary["FINAL_CURRENT_STATE:OK"] == 1
    assert_completion_sources_readable(records)


def test_assert_completion_sources_readable_blocks_missing(tmp_path: Path) -> None:
    import pytest

    from scripts.control_center_completion_index_guard import (
        assert_completion_sources_readable,
        load_completion_sources,
    )

    records = load_completion_sources(tmp_path)

    with pytest.raises(ValueError, match="CONTROL_CENTER_COMPLETION_INDEX_SOURCE_READ_FAILED"):
        assert_completion_sources_readable(records)


def test_canonical_completion_field_name_aliases() -> None:
    from scripts.control_center_completion_index_guard import canonical_completion_field_name

    assert canonical_completion_field_name("Latest main commit") == "final_current_state_commit"
    assert canonical_completion_field_name("main merge") == "main_merge_commit"
    assert canonical_completion_field_name("D6 commit") == "final_branch_commit"
    assert canonical_completion_field_name("origin/main") == "origin_main"


def test_extract_commit_hash() -> None:
    from scripts.control_center_completion_index_guard import extract_commit_hash

    assert extract_commit_hash("c3e6ae1 add final current state") == "c3e6ae1"
    assert extract_commit_hash("merge commit: 9abbca7 merge APP into main") == "9abbca7"


def test_infer_app_id_from_final_state_file() -> None:
    from scripts.control_center_completion_index_guard import infer_app_id_from_final_state_file

    app_id = infer_app_id_from_final_state_file("FCF_CURRENT_STATE_CONTROL_CENTER_COMPLETION_INDEX_GUARD_APP_1_FINAL.md")

    assert app_id == "CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1"


def test_build_completion_entry_from_source() -> None:
    from scripts.control_center_completion_index_guard import (
        CompletionIndexSourceRecord,
        build_completion_entry_from_source,
        validate_completion_index_entry,
    )

    record = CompletionIndexSourceRecord(
        path="FCF_CURRENT_STATE_CONTROL_CENTER_COMPLETION_INDEX_GUARD_APP_1_FINAL.md",
        source_kind="FINAL_CURRENT_STATE",
        exists=True,
        utf8_status="OK",
        extracted_fields={
            "status": "completed",
            "branch": "main",
            "main merge commit": "123abcd merge APP into main",
            "D6 commit": "456def0 add D6 final closeout",
            "latest main commit": "789abcd add final current state",
            "validation": "1741 passed",
            "git status": "clean",
            "origin/main": "synced",
            "tag": "none",
            "release": "none",
            "deploy": "none",
        },
    )

    entry = build_completion_entry_from_source(record)
    result = validate_completion_index_entry(entry)

    assert entry["app_id"] == "CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1"
    assert entry["main_merge_commit"] == "123abcd"
    assert entry["final_branch_commit"] == "456def0"
    assert entry["final_current_state_commit"] == "789abcd"
    assert result.status == "PASS"


def test_build_completion_entries_from_sources_filters_final_state_only() -> None:
    from scripts.control_center_completion_index_guard import (
        CompletionIndexSourceRecord,
        build_completion_entries_from_sources,
    )

    final_record = CompletionIndexSourceRecord(
        path="FCF_CURRENT_STATE_TEST_APP_1_FINAL.md",
        source_kind="FINAL_CURRENT_STATE",
        exists=True,
        utf8_status="OK",
        extracted_fields={
            "app_id": "TEST-APP-1",
            "status": "completed",
            "branch": "main",
            "main_merge_commit": "123abcd",
            "final_branch_commit": "456def0",
            "final_current_state_commit": "789abcd",
            "final_current_state_file": "FCF_CURRENT_STATE_TEST_APP_1_FINAL.md",
            "validation": "passed",
            "git_status": "clean",
            "origin_main": "synced",
            "tag": "none",
            "release": "none",
            "deploy": "none",
        },
    )

    control_record = CompletionIndexSourceRecord(
        path="docs/FCF_PROJECT_CONTROL_CENTER.md",
        source_kind="CONTROL_CENTER",
        exists=True,
        utf8_status="OK",
        extracted_fields={"app_id": "CONTROL"},
    )

    entries = build_completion_entries_from_sources([control_record, final_record])

    assert len(entries) == 1
    assert entries[0]["app_id"] == "TEST-APP-1"


def test_assert_completion_entries_from_sources_pass_blocks_duplicate() -> None:
    import pytest

    from scripts.control_center_completion_index_guard import (
        CompletionIndexSourceRecord,
        assert_completion_entries_from_sources_pass,
    )

    first = CompletionIndexSourceRecord(
        path="FCF_CURRENT_STATE_TEST_APP_1_FINAL.md",
        source_kind="FINAL_CURRENT_STATE",
        exists=True,
        utf8_status="OK",
        extracted_fields={
            "app_id": "TEST-APP-1",
            "status": "completed",
            "branch": "main",
            "main_merge_commit": "123abcd",
            "final_branch_commit": "456def0",
            "final_current_state_commit": "789abcd",
            "final_current_state_file": "FCF_CURRENT_STATE_TEST_APP_1_FINAL.md",
            "validation": "passed",
            "git_status": "clean",
            "origin_main": "synced",
            "tag": "none",
            "release": "none",
            "deploy": "none",
        },
    )

    second = CompletionIndexSourceRecord(
        path="FCF_CURRENT_STATE_TEST_APP_1_FINAL_COPY.md",
        source_kind="FINAL_CURRENT_STATE",
        exists=True,
        utf8_status="OK",
        extracted_fields=first.extracted_fields,
    )

    with pytest.raises(ValueError, match="CONTROL_CENTER_COMPLETION_INDEX_DUPLICATE_FAILED"):
        assert_completion_entries_from_sources_pass([first, second])


def test_derive_expected_app_ids_from_final_state_files() -> None:
    from scripts.control_center_completion_index_guard import derive_expected_app_ids_from_final_state_files

    app_ids = derive_expected_app_ids_from_final_state_files(
        [
            "FCF_CURRENT_STATE_TEST_APP_1_FINAL.md",
            "FCF_CURRENT_STATE_OTHER_APP_1_FINAL.md",
        ]
    )

    assert app_ids == ["OTHER-APP-1", "TEST-APP-1"]


def test_build_completion_index_matrix_pass() -> None:
    from scripts.control_center_completion_index_guard import (
        assert_completion_index_matrix_pass,
        build_completion_index_matrix,
    )

    entries = [
        {
            "app_id": "TEST-APP-1",
            "status": "completed",
            "branch": "main",
            "main_merge_commit": "123abcd",
            "final_branch_commit": "456def0",
            "final_current_state_commit": "789abcd",
            "final_current_state_file": "FCF_CURRENT_STATE_TEST_APP_1_FINAL.md",
            "validation": "passed",
            "git_status": "clean",
            "origin_main": "synced",
            "tag": "none",
            "release": "none",
            "deploy": "none",
        }
    ]

    report = build_completion_index_matrix(entries, ["TEST-APP-1"])

    assert report.status == "PASS"
    assert report.expected_count == 1
    assert report.actual_count == 1
    assert report.row_count == 1
    assert report.rows[0].validation_status == "PASS"
    assert_completion_index_matrix_pass(report)


def test_build_completion_index_matrix_blocks_missing_app() -> None:
    from scripts.control_center_completion_index_guard import build_completion_index_matrix

    report = build_completion_index_matrix([], ["TEST-APP-1"])

    assert report.status == "BLOCK"
    assert report.missing_app_ids == ["TEST-APP-1"]


def test_build_completion_index_matrix_blocks_unexpected_app() -> None:
    from scripts.control_center_completion_index_guard import build_completion_index_matrix

    entries = [
        {
            "app_id": "UNEXPECTED-APP-1",
            "status": "completed",
            "branch": "main",
            "main_merge_commit": "123abcd",
            "final_branch_commit": "456def0",
            "final_current_state_commit": "789abcd",
            "final_current_state_file": "FCF_CURRENT_STATE_UNEXPECTED_APP_1_FINAL.md",
            "validation": "passed",
            "git_status": "clean",
            "origin_main": "synced",
            "tag": "none",
            "release": "none",
            "deploy": "none",
        }
    ]

    report = build_completion_index_matrix(entries, ["TEST-APP-1"])

    assert report.status == "BLOCK"
    assert report.missing_app_ids == ["TEST-APP-1"]
    assert report.unexpected_app_ids == ["UNEXPECTED-APP-1"]


def test_build_completion_index_matrix_blocks_duplicate_app() -> None:
    from scripts.control_center_completion_index_guard import build_completion_index_matrix

    entry = {
        "app_id": "TEST-APP-1",
        "status": "completed",
        "branch": "main",
        "main_merge_commit": "123abcd",
        "final_branch_commit": "456def0",
        "final_current_state_commit": "789abcd",
        "final_current_state_file": "FCF_CURRENT_STATE_TEST_APP_1_FINAL.md",
        "validation": "passed",
        "git_status": "clean",
        "origin_main": "synced",
        "tag": "none",
        "release": "none",
        "deploy": "none",
    }

    report = build_completion_index_matrix([entry, dict(entry)], ["TEST-APP-1"])

    assert report.status == "BLOCK"
    assert "TEST-APP-1" in report.duplicate_app_ids


def test_render_completion_index_matrix_md() -> None:
    from scripts.control_center_completion_index_guard import (
        build_completion_index_matrix,
        render_completion_index_matrix_md,
    )

    entries = [
        {
            "app_id": "TEST-APP-1",
            "status": "completed",
            "branch": "main",
            "main_merge_commit": "123abcd",
            "final_branch_commit": "456def0",
            "final_current_state_commit": "789abcd",
            "final_current_state_file": "FCF_CURRENT_STATE_TEST_APP_1_FINAL.md",
            "validation": "passed",
            "git_status": "clean",
            "origin_main": "synced",
            "tag": "none",
            "release": "none",
            "deploy": "none",
        }
    ]

    report = build_completion_index_matrix(entries, ["TEST-APP-1"])
    text = render_completion_index_matrix_md(report)

    assert "# CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1 D4 Completion Matrix" in text
    assert "- status: PASS" in text
    assert "TEST-APP-1" in text


def test_build_completion_index_matrix_from_sources() -> None:
    from scripts.control_center_completion_index_guard import (
        CompletionIndexSourceRecord,
        build_completion_index_matrix_from_sources,
    )

    source = CompletionIndexSourceRecord(
        path="FCF_CURRENT_STATE_TEST_APP_1_FINAL.md",
        source_kind="FINAL_CURRENT_STATE",
        exists=True,
        utf8_status="OK",
        extracted_fields={
            "app_id": "TEST-APP-1",
            "status": "completed",
            "branch": "main",
            "main_merge_commit": "123abcd",
            "final_branch_commit": "456def0",
            "final_current_state_commit": "789abcd",
            "final_current_state_file": "FCF_CURRENT_STATE_TEST_APP_1_FINAL.md",
            "validation": "passed",
            "git_status": "clean",
            "origin_main": "synced",
            "tag": "none",
            "release": "none",
            "deploy": "none",
        },
    )

    report = build_completion_index_matrix_from_sources([source])

    assert report.status == "PASS"
    assert report.expected_count == 1
    assert report.actual_count == 1


def test_build_completion_index_guard_packet_pass() -> None:
    from scripts.control_center_completion_index_guard import (
        assert_completion_index_guard_packet_safe,
        build_completion_index_guard_packet,
        build_completion_index_matrix,
    )

    entries = [
        {
            "app_id": "TEST-APP-1",
            "status": "completed",
            "branch": "main",
            "main_merge_commit": "123abcd",
            "final_branch_commit": "456def0",
            "final_current_state_commit": "789abcd",
            "final_current_state_file": "FCF_CURRENT_STATE_TEST_APP_1_FINAL.md",
            "validation": "passed",
            "git_status": "clean",
            "origin_main": "synced",
            "tag": "none",
            "release": "none",
            "deploy": "none",
        }
    ]

    matrix = build_completion_index_matrix(entries, ["TEST-APP-1"])
    packet = build_completion_index_guard_packet(matrix)

    assert packet.stage_id == "CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1-D5"
    assert packet.status == "PASS"
    assert packet.expected_count == 1
    assert packet.actual_count == 1
    assert packet.missing_count == 0
    assert packet.unexpected_count == 0
    assert packet.duplicate_app_count == 0
    assert packet.duplicate_file_count == 0
    assert packet.invalid_row_count == 0
    assert packet.operator_review_required is True
    assert packet.real_execution_allowed is False
    assert packet.trade_action_enabled is False
    assert packet.tag_allowed is False
    assert packet.release_allowed is False
    assert packet.deploy_allowed is False
    assert_completion_index_guard_packet_safe(packet)


def test_completion_index_guard_packet_blocks_missing() -> None:
    from scripts.control_center_completion_index_guard import (
        assert_completion_index_guard_packet_safe,
        build_completion_index_guard_packet,
        build_completion_index_matrix,
    )

    matrix = build_completion_index_matrix([], ["TEST-APP-1"])
    packet = build_completion_index_guard_packet(matrix)

    assert packet.status == "BLOCK"
    assert packet.missing_count == 1

    with pytest.raises(ValueError, match="CONTROL_CENTER_COMPLETION_INDEX_GUARD_PACKET_BLOCKED"):
        assert_completion_index_guard_packet_safe(packet)


def test_completion_index_guard_packet_blocks_duplicate() -> None:
    from scripts.control_center_completion_index_guard import (
        build_completion_index_guard_packet,
        build_completion_index_matrix,
    )

    entry = {
        "app_id": "TEST-APP-1",
        "status": "completed",
        "branch": "main",
        "main_merge_commit": "123abcd",
        "final_branch_commit": "456def0",
        "final_current_state_commit": "789abcd",
        "final_current_state_file": "FCF_CURRENT_STATE_TEST_APP_1_FINAL.md",
        "validation": "passed",
        "git_status": "clean",
        "origin_main": "synced",
        "tag": "none",
        "release": "none",
        "deploy": "none",
    }

    matrix = build_completion_index_matrix([entry, dict(entry)], ["TEST-APP-1"])
    packet = build_completion_index_guard_packet(matrix)

    assert packet.status == "BLOCK"
    assert packet.duplicate_app_count == 1
    assert packet.duplicate_file_count == 1


def test_render_completion_index_guard_packet_md() -> None:
    from scripts.control_center_completion_index_guard import (
        build_completion_index_guard_packet,
        build_completion_index_matrix,
        render_completion_index_guard_packet_md,
    )

    entries = [
        {
            "app_id": "TEST-APP-1",
            "status": "completed",
            "branch": "main",
            "main_merge_commit": "123abcd",
            "final_branch_commit": "456def0",
            "final_current_state_commit": "789abcd",
            "final_current_state_file": "FCF_CURRENT_STATE_TEST_APP_1_FINAL.md",
            "validation": "passed",
            "git_status": "clean",
            "origin_main": "synced",
            "tag": "none",
            "release": "none",
            "deploy": "none",
        }
    ]

    packet = build_completion_index_guard_packet(build_completion_index_matrix(entries, ["TEST-APP-1"]))
    text = render_completion_index_guard_packet_md(packet)

    assert "# CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1 D5 Guard Packet" in text
    assert "- status: PASS" in text
    assert "- operator_review_required: true" in text
    assert "- real_execution_allowed: false" in text
    assert "- trade_action_enabled: false" in text
    assert "- tag_allowed: false" in text
    assert "- release_allowed: false" in text
    assert "- deploy_allowed: false" in text


def test_write_completion_index_guard_packet_md(tmp_path: Path) -> None:
    from scripts.control_center_completion_index_guard import (
        build_completion_index_guard_packet,
        build_completion_index_matrix,
        write_completion_index_guard_packet_md,
    )

    entries = [
        {
            "app_id": "TEST-APP-1",
            "status": "completed",
            "branch": "main",
            "main_merge_commit": "123abcd",
            "final_branch_commit": "456def0",
            "final_current_state_commit": "789abcd",
            "final_current_state_file": "FCF_CURRENT_STATE_TEST_APP_1_FINAL.md",
            "validation": "passed",
            "git_status": "clean",
            "origin_main": "synced",
            "tag": "none",
            "release": "none",
            "deploy": "none",
        }
    ]

    packet = build_completion_index_guard_packet(build_completion_index_matrix(entries, ["TEST-APP-1"]))
    output = tmp_path / "packet.md"
    write_completion_index_guard_packet_md(packet, output)

    text = output.read_text(encoding="utf-8")
    assert text.startswith("# CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1 D5 Guard Packet")
    assert "- expected_count: 1" in text


def test_build_completion_index_guard_packet_from_sources() -> None:
    from scripts.control_center_completion_index_guard import (
        CompletionIndexSourceRecord,
        build_completion_index_guard_packet_from_sources,
    )

    source = CompletionIndexSourceRecord(
        path="FCF_CURRENT_STATE_TEST_APP_1_FINAL.md",
        source_kind="FINAL_CURRENT_STATE",
        exists=True,
        utf8_status="OK",
        extracted_fields={
            "app_id": "TEST-APP-1",
            "status": "completed",
            "branch": "main",
            "main_merge_commit": "123abcd",
            "final_branch_commit": "456def0",
            "final_current_state_commit": "789abcd",
            "final_current_state_file": "FCF_CURRENT_STATE_TEST_APP_1_FINAL.md",
            "validation": "passed",
            "git_status": "clean",
            "origin_main": "synced",
            "tag": "none",
            "release": "none",
            "deploy": "none",
        },
    )

    packet = build_completion_index_guard_packet_from_sources([source])

    assert packet.status == "PASS"
    assert packet.expected_count == 1
    assert packet.actual_count == 1


def test_build_completion_index_closeout_safe() -> None:
    from scripts.control_center_completion_index_guard import (
        assert_completion_index_closeout_safe,
        build_completion_index_closeout,
    )

    closeout = build_completion_index_closeout()

    assert closeout.app_id == "CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1"
    assert closeout.final_status == "READY_FOR_MAIN_MERGE"
    assert closeout.validation_required is True
    assert closeout.merge_ready is True
    assert closeout.paper_only is True
    assert closeout.local_only is True
    assert closeout.read_only is True
    assert closeout.sidecar_only is True
    assert closeout.operator_review_required is True
    assert closeout.no_real_trading is True
    assert closeout.no_tag_release_deploy is True
    assert_completion_index_closeout_safe(closeout)


def test_render_completion_index_closeout_md_contains_boundary() -> None:
    from scripts.control_center_completion_index_guard import (
        build_completion_index_closeout,
        render_completion_index_closeout_md,
    )

    text = render_completion_index_closeout_md(build_completion_index_closeout())

    assert "# CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1 D6 Final Closeout" in text
    assert "- paper_only: true" in text
    assert "- local_only: true" in text
    assert "- read_only: true" in text
    assert "- sidecar_only: true" in text
    assert "- operator_review_required: true" in text
    assert "- no_real_trading: true" in text
    assert "- no_tag_release_deploy: true" in text


def test_completion_index_closeout_stage_names() -> None:
    from scripts.control_center_completion_index_guard import build_completion_index_closeout

    closeout = build_completion_index_closeout()
    joined = "\n".join(closeout.completed_stages)

    assert "D1 completion index contract" in joined
    assert "D2 completion source loader" in joined
    assert "D3 completion entry builder" in joined
    assert "D4 completion index matrix" in joined
    assert "D5 completion index guard packet" in joined
    assert "D6 final workflow handoff and closeout" in joined


def test_write_completion_index_closeout_md(tmp_path: Path) -> None:
    from scripts.control_center_completion_index_guard import write_completion_index_closeout_md

    output = tmp_path / "closeout.md"
    write_completion_index_closeout_md(output)

    text = output.read_text(encoding="utf-8")
    assert text.startswith("# CONTROL-CENTER-COMPLETION-INDEX-GUARD-APP-1 D6 Final Closeout")
    assert "READY_FOR_MAIN_MERGE" in text
