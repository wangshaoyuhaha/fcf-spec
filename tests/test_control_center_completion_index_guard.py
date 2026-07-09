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