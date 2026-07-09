import pytest

from scripts.control_center_schema_consistency_guard import (
    REQUIRED_SAFETY_FLAGS,
    assert_schema_result_pass,
    validate_final_state_record,
    validate_safety_boundary,
    validate_stage_record,
)


def _safe_boundary() -> dict[str, bool]:
    return dict(REQUIRED_SAFETY_FLAGS)


def test_validate_stage_record_passes_complete_record() -> None:
    record = {
        "app_id": "CONTROL-CENTER-SCHEMA-CONSISTENCY-GUARD-APP-1",
        "stage_id": "D1",
        "status": "completed",
        "branch": "sidecar-control-center-schema-consistency-guard-app-1",
        "commit": "abc1234",
        "validation": "passed",
        "git_status": "clean",
        "safety_boundary": _safe_boundary(),
    }

    result = validate_stage_record(record)

    assert result.status == "PASS"
    assert result.missing_keys == []
    assert result.invalid_values == []


def test_validate_stage_record_blocks_missing_keys() -> None:
    result = validate_stage_record({"stage_id": "D1", "status": "completed"})

    assert result.status == "BLOCK"
    assert "app_id" in result.missing_keys
    assert "safety_boundary" in result.missing_keys


def test_validate_stage_record_blocks_invalid_status() -> None:
    record = {
        "app_id": "APP",
        "stage_id": "D1",
        "status": "done",
        "branch": "branch",
        "commit": "commit",
        "validation": "passed",
        "git_status": "clean",
        "safety_boundary": _safe_boundary(),
    }

    result = validate_stage_record(record)

    assert result.status == "BLOCK"
    assert "status:INVALID" in result.invalid_values


def test_validate_safety_boundary_blocks_trade_flags() -> None:
    boundary = _safe_boundary()
    boundary["real_trading_allowed"] = True
    boundary["buy_button_allowed"] = True

    invalid = validate_safety_boundary(boundary)

    assert "real_trading_allowed:EXPECTED_FALSE" in invalid
    assert "buy_button_allowed:EXPECTED_FALSE" in invalid


def test_validate_final_state_record_passes_complete_record() -> None:
    record = {
        "app_id": "CONTROL-CENTER-SCHEMA-CONSISTENCY-GUARD-APP-1",
        "latest_main_commit": "abc1234",
        "main_merge_commit": "def5678",
        "final_branch_commit": "fed9876",
        "validation": "passed",
        "git_status": "clean",
        "origin_main": "synced",
        "tag": "none",
        "release": "none",
        "deploy": "none",
    }

    result = validate_final_state_record(record)

    assert result.status == "PASS"


def test_validate_final_state_record_blocks_release_or_deploy() -> None:
    record = {
        "app_id": "APP",
        "latest_main_commit": "abc1234",
        "main_merge_commit": "def5678",
        "final_branch_commit": "fed9876",
        "validation": "passed",
        "git_status": "clean",
        "origin_main": "synced",
        "tag": "none",
        "release": "v1",
        "deploy": "none",
    }

    result = validate_final_state_record(record)

    assert result.status == "BLOCK"
    assert "release:MUST_BE_NONE" in result.invalid_values


def test_assert_schema_result_pass_raises_on_block() -> None:
    result = validate_final_state_record({"app_id": "APP"})

    with pytest.raises(ValueError, match="CONTROL_CENTER_SCHEMA_CONSISTENCY_FAILED"):
        assert_schema_result_pass(result)