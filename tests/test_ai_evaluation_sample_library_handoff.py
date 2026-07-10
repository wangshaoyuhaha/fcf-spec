import sys
from copy import deepcopy
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from fcf.sidecars.ai_evaluation_sample_library.coverage_checks import (
    build_evaluation_sample_coverage_report,
)
from fcf.sidecars.ai_evaluation_sample_library.handoff import (
    COMPLETED_STAGES,
    HANDOFF_SCHEMA_VERSION,
    HANDOFF_STAGE_ID,
    build_evaluation_sample_final_handoff,
    validate_evaluation_sample_final_handoff,
)
from fcf.sidecars.ai_evaluation_sample_library.registry_index import (
    build_evaluation_sample_registry,
)
from fcf.sidecars.ai_evaluation_sample_library.review_packet import (
    build_evaluation_sample_review_packet,
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


def make_review_packet(
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

    registry = build_evaluation_sample_registry(
        registry_id="evaluation-library-final",
        records=records,
        created_at_utc="2026-07-10T13:00:00Z",
    )

    coverage = build_evaluation_sample_coverage_report(
        registry
    )

    return build_evaluation_sample_review_packet(
        packet_id="evaluation-review-final",
        registry=registry,
        coverage_report=coverage,
        created_at_utc="2026-07-10T14:00:00Z",
    )


def make_handoff(
    *,
    review_status: str = "APPROVED",
) -> dict:
    return build_evaluation_sample_final_handoff(
        handoff_id="evaluation-library-handoff-001",
        review_packet=make_review_packet(
            review_status=review_status
        ),
        created_at_utc="2026-07-10T15:00:00Z",
    )


def test_handoff_identity() -> None:
    handoff = make_handoff()

    assert handoff["stage_id"] == HANDOFF_STAGE_ID
    assert handoff["schema_version"] == (
        HANDOFF_SCHEMA_VERSION
    )
    assert handoff["handoff_id"] == (
        "evaluation-library-handoff-001"
    )


def test_ready_handoff_still_requires_operator_review() -> None:
    handoff = make_handoff()

    assert handoff["handoff_status"] == (
        "READY_FOR_OPERATOR_REVIEW"
    )
    assert handoff["next_review_state"] == (
        "OPERATOR_REVIEW_REQUIRED"
    )
    assert handoff["operator_review_required"] is True


def test_pending_source_requires_review() -> None:
    handoff = make_handoff(
        review_status="REVIEW_REQUIRED"
    )

    assert handoff["source_governance_status"] == (
        "REVIEW_REQUIRED"
    )
    assert handoff["handoff_status"] == "REVIEW_REQUIRED"
    assert handoff["next_review_state"] == (
        "OPERATOR_REVIEW_REQUIRED"
    )


def test_blocked_source_blocks_handoff() -> None:
    packet = make_review_packet()
    packet["governance_status"] = "BLOCKED"
    packet["coverage_status"] = "FAIL"

    handoff = build_evaluation_sample_final_handoff(
        handoff_id="evaluation-library-blocked",
        review_packet=packet,
        created_at_utc="2026-07-10T15:00:00Z",
    )

    assert handoff["handoff_status"] == "BLOCKED"
    assert handoff["next_review_state"] == (
        "SOURCE_REPAIR_REQUIRED"
    )


def test_invalid_review_packet_blocks_handoff() -> None:
    packet = make_review_packet()
    packet["sample_count"] = 999

    handoff = build_evaluation_sample_final_handoff(
        handoff_id="evaluation-library-invalid",
        review_packet=packet,
        created_at_utc="2026-07-10T15:00:00Z",
    )

    assert handoff["handoff_status"] == "BLOCKED"
    assert (
        "review_packet:sample_count_mismatch"
        in handoff["source_validation_errors"]
    )


def test_handoff_records_all_completed_stages() -> None:
    handoff = make_handoff()

    assert handoff["completed_stages"] == list(
        COMPLETED_STAGES
    )
    assert len(handoff["completed_stages"]) == 6


def test_handoff_preserves_source_summary() -> None:
    handoff = make_handoff()

    assert handoff["source_packet_id"] == (
        "evaluation-review-final"
    )
    assert handoff["source_registry_id"] == (
        "evaluation-library-final"
    )
    assert handoff["sample_count"] == len(
        EVALUATION_DIMENSIONS
    )


def test_handoff_blocks_automatic_capabilities() -> None:
    handoff = make_handoff()

    assert handoff["operator_review_bypass_allowed"] is False
    assert handoff["automatic_approval_allowed"] is False
    assert handoff["model_invocation_allowed"] is False
    assert handoff["prompt_execution_allowed"] is False
    assert handoff["orchestrator_execution_allowed"] is False
    assert handoff["news_feed_connection_allowed"] is False
    assert handoff["trade_action_allowed"] is False
    assert handoff["real_execution_allowed"] is False
    assert handoff["broker_connection_allowed"] is False
    assert handoff["exchange_connection_allowed"] is False


def test_handoff_validation_passes() -> None:
    assert validate_evaluation_sample_final_handoff(
        make_handoff()
    ) == []


def test_validation_detects_status_mismatch() -> None:
    handoff = make_handoff()
    handoff["handoff_status"] = "BLOCKED"

    errors = validate_evaluation_sample_final_handoff(
        handoff
    )

    assert "handoff_status_mismatch" in errors
    assert "next_review_state_mismatch" in errors


def test_validation_detects_count_mismatch() -> None:
    handoff = make_handoff()
    handoff["sample_count"] = 999

    errors = validate_evaluation_sample_final_handoff(
        handoff
    )

    assert "sample_count_mismatch" in errors


def test_validation_detects_boundary_bypass() -> None:
    handoff = make_handoff()
    handoff["operator_review_bypass_allowed"] = True
    handoff["model_invocation_allowed"] = True
    handoff["trade_action_allowed"] = True

    errors = validate_evaluation_sample_final_handoff(
        handoff
    )

    assert (
        "operator_review_bypass_allowed_must_be_false"
        in errors
    )
    assert "model_invocation_allowed_must_be_false" in errors
    assert "trade_action_allowed_must_be_false" in errors


def test_handoff_builder_returns_fresh_lists() -> None:
    first = make_handoff()
    second = make_handoff()
    changed = deepcopy(first)

    changed["sample_keys"].append("unexpected-sample")
    changed["completed_stages"].clear()

    assert "unexpected-sample" not in second["sample_keys"]
    assert second["completed_stages"] == list(
        COMPLETED_STAGES
    )


def test_validation_rejects_invalid_timestamp() -> None:
    handoff = make_handoff()
    handoff["created_at_utc"] = "not-a-time"

    errors = validate_evaluation_sample_final_handoff(
        handoff
    )

    assert "created_at_utc_invalid" in errors


def test_validation_rejects_non_mapping() -> None:
    assert validate_evaluation_sample_final_handoff(
        []
    ) == ["handoff_not_mapping"]