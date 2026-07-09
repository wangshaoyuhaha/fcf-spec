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
