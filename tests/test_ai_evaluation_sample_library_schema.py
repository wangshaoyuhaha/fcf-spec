import sys
from copy import deepcopy
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from fcf.sidecars.ai_evaluation_sample_library.sample_schema import (
    SAMPLE_SCHEMA_VERSION,
    SAMPLE_STAGE_ID,
    build_evaluation_sample_record,
    validate_evaluation_sample_record,
)


def make_record() -> dict:
    return build_evaluation_sample_record(
        sample_id="eval-sample-001",
        sample_version="1.0.0",
        title="Risk flag preservation sample",
        evaluation_dimension="risk_preservation",
        input_payload_ref="local://samples/input-001.json",
        expected_outcome="PASS",
        expected_summary="All source risk flags remain visible.",
        expected_reason_codes=("SOURCE_REASON_PRESENT",),
        expected_risk_flags=("DATA_LIMITED",),
        evidence_refs=("evidence-entry-001",),
        registry_entry_ids=("registry-entry-001",),
        created_at_utc="2026-07-10T12:00:00Z",
    )


def test_sample_record_identity() -> None:
    record = make_record()

    assert record["stage_id"] == SAMPLE_STAGE_ID
    assert record["schema_version"] == SAMPLE_SCHEMA_VERSION
    assert record["sample_id"] == "eval-sample-001"


def test_sample_record_validation_passes() -> None:
    assert validate_evaluation_sample_record(make_record()) == []


def test_sample_record_defaults_to_operator_review() -> None:
    record = make_record()

    assert record["review_status"] == "REVIEW_REQUIRED"
    assert record["operator_review_required"] is True
    assert record["operator_review_bypass_allowed"] is False


def test_sample_record_preserves_expected_lists() -> None:
    record = make_record()

    assert record["expected_reason_codes"] == [
        "SOURCE_REASON_PRESENT"
    ]
    assert record["expected_risk_flags"] == ["DATA_LIMITED"]
    assert record["evidence_refs"] == ["evidence-entry-001"]
    assert record["registry_entry_ids"] == [
        "registry-entry-001"
    ]


def test_sample_record_blocks_execution_capabilities() -> None:
    record = make_record()

    assert record["model_invocation_allowed"] is False
    assert record["prompt_execution_allowed"] is False
    assert record["orchestrator_execution_allowed"] is False
    assert record["trade_action_allowed"] is False
    assert record["real_execution_allowed"] is False


def test_validation_detects_invalid_dimension() -> None:
    record = make_record()
    record["evaluation_dimension"] = "trade_execution"

    errors = validate_evaluation_sample_record(record)

    assert "evaluation_dimension_invalid" in errors


def test_validation_detects_invalid_outcome_and_status() -> None:
    record = make_record()
    record["expected_outcome"] = "BUY"
    record["review_status"] = "AUTO_APPROVED"

    errors = validate_evaluation_sample_record(record)

    assert "expected_outcome_invalid" in errors
    assert "review_status_invalid" in errors


def test_validation_requires_evidence_and_registry_refs() -> None:
    record = make_record()
    record["evidence_refs"] = []
    record["registry_entry_ids"] = []

    errors = validate_evaluation_sample_record(record)

    assert "evidence_refs_invalid" in errors
    assert "registry_entry_ids_invalid" in errors


def test_validation_detects_invalid_version_and_time() -> None:
    record = make_record()
    record["sample_version"] = "version-one"
    record["created_at_utc"] = "not-a-timestamp"

    errors = validate_evaluation_sample_record(record)

    assert "sample_version_invalid" in errors
    assert "created_at_utc_invalid" in errors


def test_validation_detects_boundary_bypass() -> None:
    record = make_record()
    record["operator_review_bypass_allowed"] = True
    record["model_invocation_allowed"] = True

    errors = validate_evaluation_sample_record(record)

    assert (
        "operator_review_bypass_allowed_must_be_false"
        in errors
    )
    assert "model_invocation_allowed_must_be_false" in errors


def test_builder_returns_fresh_lists() -> None:
    first = make_record()
    second = make_record()
    changed = deepcopy(first)

    changed["evidence_refs"].append("unexpected-evidence")
    changed["expected_risk_flags"].clear()

    assert "unexpected-evidence" not in second["evidence_refs"]
    assert second["expected_risk_flags"] == ["DATA_LIMITED"]


def test_validation_rejects_non_mapping() -> None:
    assert validate_evaluation_sample_record([]) == [
        "record_not_mapping"
    ]