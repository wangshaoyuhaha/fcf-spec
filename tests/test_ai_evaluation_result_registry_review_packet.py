import sys
from copy import deepcopy
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

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
    REVIEW_PACKET_SCHEMA_VERSION,
    REVIEW_PACKET_STAGE_ID,
    build_evaluation_result_review_packet,
    validate_evaluation_result_review_packet,
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


def make_sample_registry() -> dict:
    return build_evaluation_sample_registry(
        registry_id="sample-registry-review",
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


def make_result_registry(
    *,
    second_sample_id: str = "sample-002",
    second_status: str = "ARCHIVED",
) -> dict:
    return build_evaluation_result_registry(
        registry_id="result-registry-review",
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


def make_packet(
    *,
    second_sample_id: str = "sample-002",
    second_status: str = "ARCHIVED",
) -> dict:
    sample_registry = make_sample_registry()
    result_registry = make_result_registry(
        second_sample_id=second_sample_id,
        second_status=second_status,
    )

    linkage_report = build_sample_result_linkage_report(
        report_id="linkage-report-review",
        sample_registry=sample_registry,
        result_registry=result_registry,
        created_at_utc="2026-07-11T05:00:00Z",
    )

    return build_evaluation_result_review_packet(
        packet_id="result-review-packet-001",
        result_registry=result_registry,
        linkage_report=linkage_report,
        created_at_utc="2026-07-11T06:00:00Z",
        reviewer_note="Paper-only governance review.",
    )


def test_review_packet_identity() -> None:
    packet = make_packet()

    assert packet["stage_id"] == REVIEW_PACKET_STAGE_ID
    assert (
        packet["schema_version"]
        == REVIEW_PACKET_SCHEMA_VERSION
    )
    assert packet["packet_id"] == "result-review-packet-001"


def test_valid_linkage_is_ready_for_operator_review() -> None:
    packet = make_packet()

    assert packet["source_linkage_status"] == "PASS"
    assert packet["governance_status"] == (
        "READY_FOR_OPERATOR_REVIEW"
    )
    assert packet["operator_review_required"] is True


def test_pending_result_requires_review() -> None:
    packet = make_packet(
        second_status="REVIEW_REQUIRED"
    )

    assert packet["source_linkage_status"] == (
        "REVIEW_REQUIRED"
    )
    assert packet["governance_status"] == (
        "REVIEW_REQUIRED"
    )


def test_failed_linkage_blocks_packet() -> None:
    packet = make_packet(
        second_sample_id="sample-999"
    )

    assert packet["source_linkage_status"] == "FAIL"
    assert packet["governance_status"] == "BLOCKED"
    assert packet["unknown_sample_keys"] == [
        "sample-999@1.0.0"
    ]


def test_invalid_result_registry_blocks_packet() -> None:
    sample_registry = make_sample_registry()
    result_registry = make_result_registry()
    result_registry["result_count"] = 999

    linkage_report = build_sample_result_linkage_report(
        report_id="invalid-registry-linkage",
        sample_registry=sample_registry,
        result_registry=result_registry,
        created_at_utc="2026-07-11T05:00:00Z",
    )

    packet = build_evaluation_result_review_packet(
        packet_id="invalid-registry-packet",
        result_registry=result_registry,
        linkage_report=linkage_report,
        created_at_utc="2026-07-11T06:00:00Z",
    )

    assert packet["governance_status"] == "BLOCKED"
    assert (
        "result_registry:result_count_mismatch"
        in packet["source_validation_errors"]
    )


def test_packet_preserves_source_summary() -> None:
    packet = make_packet()

    assert packet["source_result_registry_id"] == (
        "result-registry-review"
    )
    assert packet["source_linkage_report_id"] == (
        "linkage-report-review"
    )
    assert packet["sample_count"] == 2
    assert packet["result_count"] == 2
    assert packet["linked_result_count"] == 2


def test_packet_blocks_automatic_capabilities() -> None:
    packet = make_packet()

    assert packet["imported_artifacts_only"] is True
    assert packet["operator_review_bypass_allowed"] is False
    assert (
        packet["automatic_evaluation_acceptance_allowed"]
        is False
    )
    assert packet["model_invocation_allowed"] is False
    assert packet["prompt_execution_allowed"] is False
    assert packet["orchestrator_execution_allowed"] is False
    assert packet["trade_action_allowed"] is False
    assert packet["real_execution_allowed"] is False


def test_review_packet_validation_passes() -> None:
    assert validate_evaluation_result_review_packet(
        make_packet()
    ) == []


def test_validation_detects_status_mismatch() -> None:
    packet = make_packet()
    packet["governance_status"] = "BLOCKED"

    errors = validate_evaluation_result_review_packet(
        packet
    )

    assert "governance_status_mismatch" in errors


def test_validation_detects_count_mismatches() -> None:
    packet = make_packet()
    packet["sample_count"] = 999
    packet["linked_result_count"] = 999

    errors = validate_evaluation_result_review_packet(
        packet
    )

    assert "sample_count_mismatch" in errors
    assert "linked_result_count_mismatch" in errors


def test_validation_detects_boundary_bypass() -> None:
    packet = make_packet()
    packet["operator_review_bypass_allowed"] = True
    packet["automatic_evaluation_acceptance_allowed"] = True
    packet["model_invocation_allowed"] = True

    errors = validate_evaluation_result_review_packet(
        packet
    )

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
    first = make_packet()
    second = make_packet()
    changed = deepcopy(first)

    changed["linked_result_keys"].append(
        "unexpected-result"
    )
    changed["known_sample_keys"].clear()

    assert (
        "unexpected-result"
        not in second["linked_result_keys"]
    )
    assert second["known_sample_keys"]


def test_validation_rejects_invalid_timestamp() -> None:
    packet = make_packet()
    packet["created_at_utc"] = "not-a-time"

    errors = validate_evaluation_result_review_packet(
        packet
    )

    assert "created_at_utc_invalid" in errors


def test_validation_rejects_non_mapping() -> None:
    assert validate_evaluation_result_review_packet(
        []
    ) == ["packet_not_mapping"]