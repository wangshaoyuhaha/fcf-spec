import sys
from copy import deepcopy
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from fcf.sidecars.ai_evaluation_sample_library.coverage_checks import (
    build_evaluation_sample_coverage_report,
)
from fcf.sidecars.ai_evaluation_sample_library.registry_index import (
    build_evaluation_sample_registry,
)
from fcf.sidecars.ai_evaluation_sample_library.review_packet import (
    REVIEW_PACKET_SCHEMA_VERSION,
    REVIEW_PACKET_STAGE_ID,
    build_evaluation_sample_review_packet,
    validate_evaluation_sample_review_packet,
)
from fcf.sidecars.ai_evaluation_sample_library.sample_schema import (
    EVALUATION_DIMENSIONS,
    build_evaluation_sample_record,
)


def make_record(
    dimension: str,
    *,
    review_status: str = "APPROVED",
) -> dict:
    sample_id = f"sample-{dimension}"

    return build_evaluation_sample_record(
        sample_id=sample_id,
        sample_version="1.0.0",
        title=f"Evaluation sample for {dimension}",
        evaluation_dimension=dimension,
        input_payload_ref=f"local://samples/{sample_id}.json",
        expected_outcome="PASS",
        expected_summary="Expected governance result.",
        expected_reason_codes=("REASON_PRESENT",),
        expected_risk_flags=("REVIEW_REQUIRED",),
        evidence_refs=(f"evidence-{dimension}",),
        registry_entry_ids=(f"registry-{dimension}",),
        created_at_utc="2026-07-10T12:00:00Z",
        review_status=review_status,
    )


def make_registry(
    *,
    review_status: str = "APPROVED",
) -> dict:
    records = tuple(
        make_record(
            dimension,
            review_status=review_status,
        )
        for dimension in EVALUATION_DIMENSIONS
    )

    return build_evaluation_sample_registry(
        registry_id="evaluation-library-review",
        records=records,
        created_at_utc="2026-07-10T13:00:00Z",
    )


def make_packet(
    *,
    review_status: str = "APPROVED",
) -> dict:
    registry = make_registry(
        review_status=review_status
    )
    coverage = build_evaluation_sample_coverage_report(
        registry
    )

    return build_evaluation_sample_review_packet(
        packet_id="evaluation-review-packet-001",
        registry=registry,
        coverage_report=coverage,
        created_at_utc="2026-07-10T14:00:00Z",
        reviewer_note="Local paper-only review packet.",
    )


def test_review_packet_identity() -> None:
    packet = make_packet()

    assert packet["stage_id"] == REVIEW_PACKET_STAGE_ID
    assert (
        packet["schema_version"]
        == REVIEW_PACKET_SCHEMA_VERSION
    )
    assert packet["packet_id"] == (
        "evaluation-review-packet-001"
    )


def test_pass_coverage_is_ready_for_operator_review() -> None:
    packet = make_packet()

    assert packet["coverage_status"] == "PASS"
    assert packet["governance_status"] == (
        "READY_FOR_OPERATOR_REVIEW"
    )
    assert packet["operator_review_required"] is True


def test_pending_samples_require_review() -> None:
    packet = make_packet(
        review_status="REVIEW_REQUIRED"
    )

    assert packet["coverage_status"] == "REVIEW_REQUIRED"
    assert packet["governance_status"] == "REVIEW_REQUIRED"
    assert packet["pending_review_keys"]


def test_failed_coverage_blocks_packet() -> None:
    registry = make_registry()
    registry["entries"][0]["evidence_refs"] = []

    coverage = build_evaluation_sample_coverage_report(
        registry
    )

    packet = build_evaluation_sample_review_packet(
        packet_id="evaluation-review-packet-blocked",
        registry=registry,
        coverage_report=coverage,
        created_at_utc="2026-07-10T14:00:00Z",
    )

    assert packet["coverage_status"] == "FAIL"
    assert packet["governance_status"] == "BLOCKED"
    assert packet["evidence_missing_keys"]


def test_invalid_source_blocks_packet() -> None:
    registry = make_registry()
    registry["sample_count"] = 999

    coverage = build_evaluation_sample_coverage_report(
        registry
    )

    packet = build_evaluation_sample_review_packet(
        packet_id="evaluation-review-invalid-source",
        registry=registry,
        coverage_report=coverage,
        created_at_utc="2026-07-10T14:00:00Z",
    )

    assert packet["governance_status"] == "BLOCKED"
    assert (
        "registry:sample_count_mismatch"
        in packet["source_validation_errors"]
    )


def test_packet_preserves_source_summary() -> None:
    packet = make_packet()

    assert packet["source_registry_id"] == (
        "evaluation-library-review"
    )
    assert packet["sample_count"] == len(
        EVALUATION_DIMENSIONS
    )
    assert len(packet["sample_keys"]) == len(
        EVALUATION_DIMENSIONS
    )


def test_packet_blocks_automatic_actions() -> None:
    packet = make_packet()

    assert packet["automatic_approval_allowed"] is False
    assert packet["operator_review_bypass_allowed"] is False
    assert packet["model_invocation_allowed"] is False
    assert packet["prompt_execution_allowed"] is False
    assert packet["orchestrator_execution_allowed"] is False
    assert packet["trade_action_allowed"] is False
    assert packet["real_execution_allowed"] is False


def test_review_packet_validation_passes() -> None:
    assert validate_evaluation_sample_review_packet(
        make_packet()
    ) == []


def test_validation_detects_status_mismatch() -> None:
    packet = make_packet()
    packet["governance_status"] = "BLOCKED"

    errors = validate_evaluation_sample_review_packet(
        packet
    )

    assert "governance_status_mismatch" in errors


def test_validation_detects_count_mismatch() -> None:
    packet = make_packet()
    packet["sample_count"] = 999

    errors = validate_evaluation_sample_review_packet(
        packet
    )

    assert "sample_count_mismatch" in errors


def test_validation_detects_boundary_bypass() -> None:
    packet = make_packet()
    packet["operator_review_bypass_allowed"] = True
    packet["automatic_approval_allowed"] = True
    packet["model_invocation_allowed"] = True

    errors = validate_evaluation_sample_review_packet(
        packet
    )

    assert (
        "operator_review_bypass_allowed_must_be_false"
        in errors
    )
    assert "automatic_approval_allowed_must_be_false" in errors
    assert "model_invocation_allowed_must_be_false" in errors


def test_packet_builder_returns_fresh_lists() -> None:
    first = make_packet()
    second = make_packet()
    changed = deepcopy(first)

    changed["sample_keys"].append("unexpected-sample")
    changed["pending_review_keys"].append(
        "unexpected-review"
    )

    assert "unexpected-sample" not in second["sample_keys"]
    assert (
        "unexpected-review"
        not in second["pending_review_keys"]
    )


def test_validation_rejects_invalid_timestamp() -> None:
    packet = make_packet()
    packet["created_at_utc"] = "not-a-time"

    errors = validate_evaluation_sample_review_packet(
        packet
    )

    assert "created_at_utc_invalid" in errors


def test_validation_rejects_non_mapping() -> None:
    assert validate_evaluation_sample_review_packet(
        []
    ) == ["packet_not_mapping"]