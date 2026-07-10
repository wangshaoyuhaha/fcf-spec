import sys
from copy import deepcopy
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from fcf.sidecars.ai_evaluation_result_registry.handoff import (
    COMPLETED_STAGES,
    HANDOFF_SCHEMA_VERSION,
    HANDOFF_STAGE_ID,
    build_evaluation_result_final_handoff,
    validate_evaluation_result_final_handoff,
)
from fcf.sidecars.ai_evaluation_result_registry.linkage_checks import (
    build_sample_result_linkage_report,
)
from fcf.sidecars.ai_evaluation_result_registry.registry_index import (
    build_evaluation_result_registry,
)
from fcf.sidecars.ai_evaluation_result_registry.result_schema import (
    build_evaluation_result_record,
)
from fcf.sidecars.ai_evaluation_result_registry.review_packet import (
    build_evaluation_result_review_packet,
)
from fcf.sidecars.ai_evaluation_sample_library.registry_index import (
    build_evaluation_sample_registry,
)
from fcf.sidecars.ai_evaluation_sample_library.sample_schema import (
    build_evaluation_sample_record,
)


def make_sample(
    sample_id: str,
    dimension: str,
) -> dict:
    return build_evaluation_sample_record(
        sample_id=sample_id,
        sample_version="1.0.0",
        title=f"Sample {sample_id}",
        evaluation_dimension=dimension,
        input_payload_ref=f"local://samples/{sample_id}.json",
        expected_outcome="PASS",
        expected_summary="Expected governance result.",
        expected_reason_codes=("REASON_PRESENT",),
        expected_risk_flags=("REVIEW_REQUIRED",),
        evidence_refs=(f"evidence-{sample_id}",),
        registry_entry_ids=(f"registry-{sample_id}",),
        created_at_utc="2026-07-11T01:00:00Z",
        review_status="APPROVED",
    )


def make_result(
    result_id: str,
    sample_id: str,
    dimension: str,
    checksum_character: str,
    *,
    result_status: str = "ARCHIVED",
) -> dict:
    return build_evaluation_result_record(
        result_id=result_id,
        result_version="1.0.0",
        sample_id=sample_id,
        sample_version="1.0.0",
        evaluation_dimension=dimension,
        imported_output_ref=(
            f"local://evaluation-results/{result_id}.json"
        ),
        imported_output_sha256=checksum_character * 64,
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
        imported_at_utc="2026-07-11T03:00:00Z",
        result_status=result_status,
    )


def make_review_packet(
    *,
    second_sample_id: str = "sample-002",
    second_status: str = "ARCHIVED",
) -> dict:
    sample_registry = build_evaluation_sample_registry(
        registry_id="sample-registry-handoff",
        records=(
            make_sample(
                "sample-001",
                "risk_preservation",
            ),
            make_sample(
                "sample-002",
                "evidence_grounding",
            ),
        ),
        created_at_utc="2026-07-11T02:00:00Z",
    )

    result_registry = build_evaluation_result_registry(
        registry_id="result-registry-handoff",
        records=(
            make_result(
                "result-001",
                "sample-001",
                "risk_preservation",
                "a",
            ),
            make_result(
                "result-002",
                second_sample_id,
                "evidence_grounding",
                "b",
                result_status=second_status,
            ),
        ),
        created_at_utc="2026-07-11T04:00:00Z",
    )

    linkage_report = build_sample_result_linkage_report(
        report_id="linkage-report-handoff",
        sample_registry=sample_registry,
        result_registry=result_registry,
        created_at_utc="2026-07-11T05:00:00Z",
    )

    return build_evaluation_result_review_packet(
        packet_id="result-review-handoff",
        result_registry=result_registry,
        linkage_report=linkage_report,
        created_at_utc="2026-07-11T06:00:00Z",
    )


def make_handoff(
    *,
    second_sample_id: str = "sample-002",
    second_status: str = "ARCHIVED",
) -> dict:
    return build_evaluation_result_final_handoff(
        handoff_id="result-registry-handoff-001",
        review_packet=make_review_packet(
            second_sample_id=second_sample_id,
            second_status=second_status,
        ),
        created_at_utc="2026-07-11T07:00:00Z",
    )


def test_handoff_identity() -> None:
    handoff = make_handoff()

    assert handoff["stage_id"] == HANDOFF_STAGE_ID
    assert handoff["schema_version"] == (
        HANDOFF_SCHEMA_VERSION
    )
    assert handoff["handoff_id"] == (
        "result-registry-handoff-001"
    )


def test_ready_handoff_requires_operator_review() -> None:
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
        second_status="REVIEW_REQUIRED"
    )

    assert handoff["source_governance_status"] == (
        "REVIEW_REQUIRED"
    )
    assert handoff["handoff_status"] == "REVIEW_REQUIRED"


def test_failed_source_blocks_handoff() -> None:
    handoff = make_handoff(
        second_sample_id="sample-999"
    )

    assert handoff["source_governance_status"] == "BLOCKED"
    assert handoff["handoff_status"] == "BLOCKED"
    assert handoff["next_review_state"] == (
        "SOURCE_REPAIR_REQUIRED"
    )


def test_invalid_review_packet_blocks_handoff() -> None:
    packet = make_review_packet()
    packet["sample_count"] = 999

    handoff = build_evaluation_result_final_handoff(
        handoff_id="invalid-review-handoff",
        review_packet=packet,
        created_at_utc="2026-07-11T07:00:00Z",
    )

    assert handoff["handoff_status"] == "BLOCKED"
    assert (
        "review_packet:sample_count_mismatch"
        in handoff["source_validation_errors"]
    )


def test_handoff_records_all_stages() -> None:
    handoff = make_handoff()

    assert handoff["completed_stages"] == list(
        COMPLETED_STAGES
    )
    assert len(handoff["completed_stages"]) == 6


def test_handoff_preserves_source_summary() -> None:
    handoff = make_handoff()

    assert handoff["source_packet_id"] == (
        "result-review-handoff"
    )
    assert handoff["source_result_registry_id"] == (
        "result-registry-handoff"
    )
    assert handoff["sample_count"] == 2
    assert handoff["result_count"] == 2
    assert handoff["linked_result_count"] == 2


def test_handoff_blocks_automatic_capabilities() -> None:
    handoff = make_handoff()

    assert handoff["imported_artifacts_only"] is True
    assert handoff["operator_review_bypass_allowed"] is False
    assert (
        handoff["automatic_evaluation_acceptance_allowed"]
        is False
    )
    assert handoff["model_invocation_allowed"] is False
    assert handoff["prompt_execution_allowed"] is False
    assert handoff["orchestrator_execution_allowed"] is False
    assert handoff["trade_action_allowed"] is False
    assert handoff["real_execution_allowed"] is False
    assert handoff["broker_connection_allowed"] is False
    assert handoff["exchange_connection_allowed"] is False


def test_handoff_validation_passes() -> None:
    assert validate_evaluation_result_final_handoff(
        make_handoff()
    ) == []


def test_validation_detects_status_mismatch() -> None:
    handoff = make_handoff()
    handoff["handoff_status"] = "BLOCKED"

    errors = validate_evaluation_result_final_handoff(
        handoff
    )

    assert "handoff_status_mismatch" in errors
    assert "next_review_state_mismatch" in errors


def test_validation_detects_count_mismatch() -> None:
    handoff = make_handoff()
    handoff["sample_count"] = 999
    handoff["linked_result_count"] = 999

    errors = validate_evaluation_result_final_handoff(
        handoff
    )

    assert "sample_count_mismatch" in errors
    assert "linked_result_count_mismatch" in errors


def test_validation_detects_boundary_bypass() -> None:
    handoff = make_handoff()
    handoff["operator_review_bypass_allowed"] = True
    handoff["model_invocation_allowed"] = True
    handoff["trade_action_allowed"] = True

    errors = validate_evaluation_result_final_handoff(
        handoff
    )

    assert (
        "operator_review_bypass_allowed_must_be_false"
        in errors
    )
    assert "model_invocation_allowed_must_be_false" in errors
    assert "trade_action_allowed_must_be_false" in errors


def test_builder_returns_fresh_lists() -> None:
    first = make_handoff()
    second = make_handoff()
    changed = deepcopy(first)

    changed["linked_result_keys"].append(
        "unexpected-result"
    )
    changed["completed_stages"].clear()

    assert (
        "unexpected-result"
        not in second["linked_result_keys"]
    )
    assert second["completed_stages"] == list(
        COMPLETED_STAGES
    )


def test_validation_rejects_invalid_timestamp() -> None:
    handoff = make_handoff()
    handoff["created_at_utc"] = "not-a-time"

    errors = validate_evaluation_result_final_handoff(
        handoff
    )

    assert "created_at_utc_invalid" in errors


def test_validation_rejects_non_mapping() -> None:
    assert validate_evaluation_result_final_handoff(
        []
    ) == ["handoff_not_mapping"]