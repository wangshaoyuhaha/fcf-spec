import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fcf.sidecars.artifact_lifecycle_registry import (
    ALLOWED_LIFECYCLE_STATUSES,
    build_lifecycle_registry_contract,
    build_lifecycle_registry_index,
    validate_lifecycle_record,
)


def _record(status="REGISTERED"):
    return {
        "artifact_id": "artifact-1",
        "artifact_type": "archive_packet",
        "artifact_path": "runtime/archive/artifact-1.json",
        "lifecycle_status": status,
    }


def test_contract_is_read_only_sidecar_only_index_only():
    contract = build_lifecycle_registry_contract()

    assert contract["stage"] == "D1"
    assert contract["paper_only"] is True
    assert contract["local_only"] is True
    assert contract["read_only"] is True
    assert contract["sidecar_only"] is True
    assert contract["index_only"] is True
    assert contract["operator_review_required"] is True
    assert contract["source_artifact_mutation_allowed"] is False
    assert contract["artifact_status_auto_repair_allowed"] is False
    assert contract["evidence_backfill_allowed"] is False
    assert contract["correlation_id_auto_fill_allowed"] is False
    assert contract["placeholder_review_allowed"] is False
    assert contract["auto_pass_allowed"] is False
    assert contract["ui_dashboard_panel_allowed"] is False
    assert contract["core_mutation_allowed"] is False
    assert contract["p48_core_expansion_allowed"] is False


def test_contract_forbids_execution_release_and_credentials():
    contract = build_lifecycle_registry_contract()

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
    assert "REGISTERED" in ALLOWED_LIFECYCLE_STATUSES
    assert "OBSERVED" in ALLOWED_LIFECYCLE_STATUSES
    assert "INCOMPLETE" in ALLOWED_LIFECYCLE_STATUSES
    assert "STALE" in ALLOWED_LIFECYCLE_STATUSES
    assert "UNRESOLVED" in ALLOWED_LIFECYCLE_STATUSES


def test_validate_record_marks_missing_field_unresolved_without_repair():
    record = _record()
    del record["artifact_path"]

    result = validate_lifecycle_record(record)

    assert result["valid"] is False
    assert result["result_status"] == "UNRESOLVED"
    assert "MISSING_ARTIFACT_PATH" in result["issues"]
    assert result["auto_pass_allowed"] is False
    assert result["auto_repair_allowed"] is False
    assert result["source_artifact_mutation_allowed"] is False
    assert result["evidence_backfill_allowed"] is False


def test_validate_record_rejects_unsupported_status():
    record = _record(status="AUTO_FIXED")

    result = validate_lifecycle_record(record)

    assert result["valid"] is False
    assert result["result_status"] == "UNRESOLVED"
    assert "UNSUPPORTED_LIFECYCLE_STATUS" in result["issues"]


def test_registry_index_marks_stale_and_incomplete_without_mutation():
    records = [
        _record(status="REGISTERED"),
        _record(status="STALE"),
        _record(status="INCOMPLETE"),
    ]

    packet = build_lifecycle_registry_index(records)

    assert packet["registry_status"] == "STALE"
    assert packet["record_count"] == 3
    assert packet["stale_count"] == 1
    assert packet["incomplete_count"] == 1
    assert packet["read_only"] is True
    assert packet["index_only"] is True
    assert packet["sidecar_only"] is True
    assert packet["operator_review_required"] is True
    assert packet["source_artifact_mutation_allowed"] is False
    assert packet["artifact_status_auto_repair_allowed"] is False
    assert packet["evidence_backfill_allowed"] is False
    assert packet["auto_pass_allowed"] is False


def test_registry_index_marks_unresolved_first():
    bad = _record(status="REGISTERED")
    bad["artifact_id"] = ""

    packet = build_lifecycle_registry_index([_record(), bad])

    assert packet["registry_status"] == "UNRESOLVED"
    assert packet["unresolved_count"] == 1
