import sys
from copy import deepcopy
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from fcf.sidecars.ai_evaluation_result_registry.registry_index import (
    REGISTRY_SCHEMA_VERSION,
    REGISTRY_STAGE_ID,
    build_evaluation_result_registry,
    validate_evaluation_result_registry,
    validate_registry_source_records,
)
from fcf.sidecars.ai_evaluation_result_registry.result_schema import (
    build_evaluation_result_record,
)


def make_record(
    result_id: str,
    sample_id: str,
    *,
    result_status: str = "REVIEW_REQUIRED",
) -> dict:
    return build_evaluation_result_record(
        result_id=result_id,
        result_version="1.0.0",
        sample_id=sample_id,
        sample_version="1.0.0",
        evaluation_dimension="evidence_grounding",
        imported_output_ref=(
            f"local://evaluation-results/{result_id}.json"
        ),
        imported_output_sha256="a" * 64,
        observed_outcome="PASS",
        result_summary="Imported evaluation result.",
        observed_reason_codes=("REASON_PRESENT",),
        observed_risk_flags=("REVIEW_REQUIRED",),
        evidence_refs=(f"evidence-{result_id}",),
        prompt_model_registry_entry_ids=(
            f"prompt-model-{result_id}",
        ),
        context_evidence_entry_ids=(
            f"context-evidence-{result_id}",
        ),
        imported_at_utc="2026-07-11T01:00:00Z",
        result_status=result_status,
    )


def make_registry() -> dict:
    return build_evaluation_result_registry(
        registry_id="evaluation-result-registry-001",
        records=(
            make_record("result-002", "sample-001"),
            make_record("result-001", "sample-001"),
            make_record(
                "result-003",
                "sample-002",
                result_status="RECORDED",
            ),
        ),
        created_at_utc="2026-07-11T02:00:00Z",
    )


def test_registry_identity() -> None:
    registry = make_registry()

    assert registry["stage_id"] == REGISTRY_STAGE_ID
    assert registry["schema_version"] == REGISTRY_SCHEMA_VERSION
    assert registry["registry_id"] == (
        "evaluation-result-registry-001"
    )


def test_registry_validation_passes() -> None:
    assert validate_evaluation_result_registry(
        make_registry()
    ) == []


def test_registry_entries_are_sorted() -> None:
    registry = make_registry()

    assert registry["result_keys"] == [
        "result-001@1.0.0",
        "result-002@1.0.0",
        "result-003@1.0.0",
    ]


def test_registry_tracks_unique_samples() -> None:
    registry = make_registry()

    assert registry["sample_count"] == 2
    assert registry["sample_keys"] == [
        "sample-001@1.0.0",
        "sample-002@1.0.0",
    ]


def test_registry_tracks_result_counts_per_sample() -> None:
    registry = make_registry()

    assert registry["sample_result_counts"] == {
        "sample-001@1.0.0": 2,
        "sample-002@1.0.0": 1,
    }


def test_registry_tracks_status_counts() -> None:
    registry = make_registry()

    assert registry["status_counts"]["REVIEW_REQUIRED"] == 2
    assert registry["status_counts"]["RECORDED"] == 1
    assert registry["status_counts"]["INVALID"] == 0


def test_registry_preserves_governance_references() -> None:
    registry = make_registry()
    first = registry["entries"][0]

    assert first["evidence_refs"] == [
        "evidence-result-001"
    ]
    assert first["prompt_model_registry_entry_ids"] == [
        "prompt-model-result-001"
    ]
    assert first["context_evidence_entry_ids"] == [
        "context-evidence-result-001"
    ]


def test_registry_blocks_automatic_capabilities() -> None:
    registry = make_registry()

    assert registry["operator_review_required"] is True
    assert registry["imported_artifacts_only"] is True
    assert registry["operator_review_bypass_allowed"] is False
    assert (
        registry["automatic_evaluation_acceptance_allowed"]
        is False
    )
    assert registry["model_invocation_allowed"] is False
    assert registry["prompt_execution_allowed"] is False
    assert registry["trade_action_allowed"] is False
    assert registry["real_execution_allowed"] is False


def test_validation_detects_duplicate_result_key() -> None:
    registry = build_evaluation_result_registry(
        registry_id="duplicate-registry",
        records=(
            make_record("result-001", "sample-001"),
            make_record("result-001", "sample-001"),
        ),
        created_at_utc="2026-07-11T02:00:00Z",
    )

    errors = validate_evaluation_result_registry(registry)

    assert "duplicate_result_key" in errors


def test_validation_detects_result_count_mismatch() -> None:
    registry = make_registry()
    registry["result_count"] = 999

    errors = validate_evaluation_result_registry(registry)

    assert "result_count_mismatch" in errors


def test_validation_detects_status_count_mismatch() -> None:
    registry = make_registry()
    registry["status_counts"]["RECORDED"] = 99

    errors = validate_evaluation_result_registry(registry)

    assert "status_counts_mismatch" in errors


def test_validation_detects_sample_count_mismatch() -> None:
    registry = make_registry()
    registry["sample_count"] = 999
    registry["sample_result_counts"] = {}

    errors = validate_evaluation_result_registry(registry)

    assert "sample_count_mismatch" in errors
    assert "sample_result_counts_mismatch" in errors


def test_validation_detects_boundary_bypass() -> None:
    registry = make_registry()
    registry["operator_review_bypass_allowed"] = True
    registry["model_invocation_allowed"] = True

    errors = validate_evaluation_result_registry(registry)

    assert (
        "operator_review_bypass_allowed_must_be_false"
        in errors
    )
    assert "model_invocation_allowed_must_be_false" in errors


def test_source_record_validation_passes() -> None:
    records = (
        make_record("result-001", "sample-001"),
        make_record("result-002", "sample-002"),
    )

    assert validate_registry_source_records(records) == []


def test_source_record_validation_reports_index() -> None:
    record = make_record("result-001", "sample-001")
    record["model_invocation_allowed"] = True

    errors = validate_registry_source_records((record,))

    assert (
        "source_record_0:"
        "model_invocation_allowed_must_be_false"
        in errors
    )


def test_registry_builder_returns_fresh_lists() -> None:
    first = make_registry()
    second = make_registry()
    changed = deepcopy(first)

    changed["entries"][0]["evidence_refs"].append(
        "unexpected-evidence"
    )
    changed["result_keys"].clear()

    assert (
        "unexpected-evidence"
        not in second["entries"][0]["evidence_refs"]
    )
    assert second["result_keys"]


def test_validation_rejects_non_mapping() -> None:
    assert validate_evaluation_result_registry([]) == [
        "registry_not_mapping"
    ]