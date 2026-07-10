import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fcf.sidecars.validation_baseline_registry import (
    ALLOWED_BASELINE_STATUSES,
    build_validation_baseline_contract,
    build_validation_baseline_index,
    validate_baseline_record,
)


def _record(status="REGISTERED", result="PASS", pass_count=2040):
    return {
        "validation_id": "validation-1",
        "command": "python -m pytest -q",
        "result": result,
        "pass_count": pass_count,
        "git_branch": "main",
        "git_head": "bf9eb31",
        "git_status": "clean",
        "origin_status": "synced",
        "baseline_status": status,
    }


def test_contract_is_read_only_sidecar_only_index_only():
    contract = build_validation_baseline_contract()

    assert contract["stage"] == "D1"
    assert contract["paper_only"] is True
    assert contract["local_only"] is True
    assert contract["read_only"] is True
    assert contract["sidecar_only"] is True
    assert contract["index_only"] is True
    assert contract["operator_review_required"] is True
    assert contract["validation_result_fabrication_allowed"] is False
    assert contract["pass_count_fabrication_allowed"] is False
    assert contract["source_artifact_mutation_allowed"] is False
    assert contract["evidence_backfill_allowed"] is False
    assert contract["auto_pass_allowed"] is False
    assert contract["core_mutation_allowed"] is False
    assert contract["p48_core_expansion_allowed"] is False


def test_contract_forbids_release_execution_and_credentials():
    contract = build_validation_baseline_contract()

    assert contract["tag_allowed"] is False
    assert contract["release_allowed"] is False
    assert contract["deploy_allowed"] is False
    assert contract["real_trade_allowed"] is False
    assert contract["real_execution_allowed"] is False
    assert contract["broker_connection_allowed"] is False
    assert contract["exchange_connection_allowed"] is False
    assert contract["api_key_allowed"] is False
    assert contract["wallet_private_key_allowed"] is False
    assert contract["real_account_allowed"] is False
    assert contract["real_position_allowed"] is False
    assert contract["buy_sell_order_allowed"] is False
    assert contract["auto_position_allowed"] is False
    assert contract["auto_portfolio_action_allowed"] is False


def test_allowed_status_vocabulary_is_explicit():
    assert "REGISTERED" in ALLOWED_BASELINE_STATUSES
    assert "VERIFIED" in ALLOWED_BASELINE_STATUSES
    assert "INCOMPLETE" in ALLOWED_BASELINE_STATUSES
    assert "STALE" in ALLOWED_BASELINE_STATUSES
    assert "UNRESOLVED" in ALLOWED_BASELINE_STATUSES


def test_validate_record_marks_pass_as_verified_without_fabrication():
    result = validate_baseline_record(_record())

    assert result["valid"] is True
    assert result["result_status"] == "VERIFIED"
    assert result["validation_result_fabrication_allowed"] is False
    assert result["pass_count_fabrication_allowed"] is False
    assert result["auto_pass_allowed"] is False
    assert result["operator_review_required"] is True


def test_validate_record_marks_missing_field_unresolved():
    record = _record()
    del record["git_head"]

    result = validate_baseline_record(record)

    assert result["valid"] is False
    assert result["result_status"] == "UNRESOLVED"
    assert "MISSING_GIT_HEAD" in result["issues"]
    assert result["source_artifact_mutation_allowed"] is False


def test_validate_record_rejects_pass_count_fabrication():
    record = _record()
    record["pass_count_fabrication_allowed"] = True

    result = validate_baseline_record(record)

    assert result["valid"] is False
    assert result["result_status"] == "UNRESOLVED"
    assert "PASS_COUNT_FABRICATION_NOT_ALLOWED" in result["issues"]


def test_validate_record_rejects_non_integer_pass_count():
    result = validate_baseline_record(_record(pass_count="2040"))

    assert result["valid"] is False
    assert result["result_status"] == "UNRESOLVED"
    assert "PASS_COUNT_NOT_INTEGER" in result["issues"]


def test_baseline_index_marks_stale_and_incomplete():
    packet = build_validation_baseline_index(
        [
            _record(status="VERIFIED"),
            _record(status="STALE"),
            _record(status="INCOMPLETE"),
        ]
    )

    assert packet["stage"] == "D1"
    assert packet["index_status"] == "STALE"
    assert packet["record_count"] == 3
    assert packet["status_counts"]["VERIFIED"] == 1
    assert packet["status_counts"]["STALE"] == 1
    assert packet["status_counts"]["INCOMPLETE"] == 1
    assert packet["read_only"] is True
    assert packet["index_only"] is True
    assert packet["sidecar_only"] is True
    assert packet["auto_pass_allowed"] is False


def test_baseline_index_unresolved_has_highest_priority():
    bad = _record()
    bad["validation_id"] = ""

    packet = build_validation_baseline_index([_record(), bad])

    assert packet["index_status"] == "UNRESOLVED"
    assert packet["status_counts"]["UNRESOLVED"] == 1
    assert packet["validation_result_fabrication_allowed"] is False
    assert packet["pass_count_fabrication_allowed"] is False
