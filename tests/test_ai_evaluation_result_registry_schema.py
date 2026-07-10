import sys
from copy import deepcopy
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from fcf.sidecars.ai_evaluation_result_registry.result_schema import (
    OBSERVED_OUTCOMES,
    RESULT_SCHEMA_VERSION,
    RESULT_STAGE_ID,
    build_evaluation_result_record,
    validate_evaluation_result_record,
)


def make_record() -> dict:
    return build_evaluation_result_record(
        result_id="evaluation-result-001",
        result_version="1.0.0",
        sample_id="evaluation-sample-001",
        sample_version="1.0.0",
        evaluation_dimension="risk_preservation",
        imported_output_ref=(
            "local://evaluation-results/result-001.json"
        ),
        imported_output_sha256="a" * 64,
        observed_outcome="PASS",
        result_summary=(
            "Imported result preserved all source risk flags."
        ),
        observed_reason_codes=(
            "SOURCE_REASON_PRESENT",
        ),
        observed_risk_flags=(
            "DATA_LIMITED",
        ),
        evidence_refs=(
            "evidence-entry-001",
        ),
        prompt_model_registry_entry_ids=(
            "prompt-model-entry-001",
        ),
        context_evidence_entry_ids=(
            "context-evidence-entry-001",
        ),
        imported_at_utc="2026-07-11T01:00:00Z",
    )


def test_result_record_identity() -> None:
    record = make_record()

    assert record["stage_id"] == RESULT_STAGE_ID
    assert record["schema_version"] == RESULT_SCHEMA_VERSION
    assert record["result_id"] == "evaluation-result-001"


def test_result_record_validation_passes() -> None:
    assert validate_evaluation_result_record(
        make_record()
    ) == []


def test_result_and_sample_keys_are_deterministic() -> None:
    record = make_record()

    assert record["result_key"] == (
        "evaluation-result-001@1.0.0"
    )
    assert record["sample_key"] == (
        "evaluation-sample-001@1.0.0"
    )


def test_result_record_defaults_to_review_required() -> None:
    record = make_record()

    assert record["result_status"] == "REVIEW_REQUIRED"
    assert record["operator_review_required"] is True
    assert record["operator_review_bypass_allowed"] is False


def test_result_record_preserves_observed_lists() -> None:
    record = make_record()

    assert record["observed_reason_codes"] == [
        "SOURCE_REASON_PRESENT"
    ]
    assert record["observed_risk_flags"] == [
        "DATA_LIMITED"
    ]
    assert record["evidence_refs"] == [
        "evidence-entry-001"
    ]


def test_result_record_blocks_execution_capabilities() -> None:
    record = make_record()

    assert record["imported_artifact"] is True
    assert record["model_invocation_allowed"] is False
    assert record["prompt_execution_allowed"] is False
    assert record["orchestrator_execution_allowed"] is False
    assert record["trade_action_allowed"] is False
    assert record["real_execution_allowed"] is False


def test_validation_detects_invalid_outcome_and_status() -> None:
    record = make_record()
    record["observed_outcome"] = "BUY"
    record["result_status"] = "AUTO_APPROVED"

    errors = validate_evaluation_result_record(record)

    assert "observed_outcome_invalid" in errors
    assert "result_status_invalid" in errors


def test_validation_detects_invalid_versions() -> None:
    record = make_record()
    record["result_version"] = "one"
    record["sample_version"] = "latest"

    errors = validate_evaluation_result_record(record)

    assert "result_version_invalid" in errors
    assert "sample_version_invalid" in errors


def test_validation_detects_invalid_checksum_and_time() -> None:
    record = make_record()
    record["imported_output_sha256"] = "invalid"
    record["imported_at_utc"] = "not-a-time"

    errors = validate_evaluation_result_record(record)

    assert "imported_output_sha256_invalid" in errors
    assert "imported_at_utc_invalid" in errors


def test_validation_requires_governance_references() -> None:
    record = make_record()
    record["evidence_refs"] = []
    record["prompt_model_registry_entry_ids"] = []
    record["context_evidence_entry_ids"] = []

    errors = validate_evaluation_result_record(record)

    assert "evidence_refs_invalid" in errors
    assert "prompt_model_registry_entry_ids_invalid" in errors
    assert "context_evidence_entry_ids_invalid" in errors


def test_validation_detects_key_mismatches() -> None:
    record = make_record()
    record["result_key"] = "wrong-result-key"
    record["sample_key"] = "wrong-sample-key"

    errors = validate_evaluation_result_record(record)

    assert "result_key_mismatch" in errors
    assert "sample_key_mismatch" in errors


def test_validation_detects_boundary_bypass() -> None:
    record = make_record()
    record["operator_review_bypass_allowed"] = True
    record["automatic_evaluation_acceptance_allowed"] = True
    record["model_invocation_allowed"] = True

    errors = validate_evaluation_result_record(record)

    assert (
        "operator_review_bypass_allowed_must_be_false"
        in errors
    )
    assert (
        "automatic_evaluation_acceptance_allowed_must_be_false"
        in errors
    )
    assert "model_invocation_allowed_must_be_false" in errors


def test_builder_returns_fresh_lists() -> None:
    first = make_record()
    second = make_record()
    changed = deepcopy(first)

    changed["observed_reason_codes"].append(
        "UNEXPECTED_REASON"
    )
    changed["evidence_refs"].clear()

    assert (
        "UNEXPECTED_REASON"
        not in second["observed_reason_codes"]
    )
    assert second["evidence_refs"] == [
        "evidence-entry-001"
    ]


def test_observed_outcomes_are_governance_only() -> None:
    assert OBSERVED_OUTCOMES == (
        "PASS",
        "FAIL",
        "REVIEW_REQUIRED",
        "INDETERMINATE",
    )


def test_validation_rejects_non_mapping() -> None:
    assert validate_evaluation_result_record([]) == [
        "record_not_mapping"
    ]