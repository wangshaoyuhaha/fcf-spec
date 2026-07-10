import sys
from copy import deepcopy
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from fcf.sidecars.ai_evaluation_comparison import (
    APP_ID,
    PROHIBITED_REVIEW_ACTIONS,
    REVIEW_PACKET_VERSION,
    build_comparison_record,
    build_comparison_review_packet,
    build_registered_comparison_matrix,
)


def make_record(
    *,
    comparison_id: str,
    sample_id: str = "sample-001",
    model_id: str = "model-alpha",
    model_version: str = "1.0.0",
    prompt_id: str = "prompt-alpha",
    prompt_version: str = "1.0.0",
    comparison_status: str = "MATCHED",
    result_status: str = "RECORDED",
) -> dict:
    return build_comparison_record(
        comparison_id=comparison_id,
        comparison_mode="expected_vs_observed",
        evaluation_sample_id=sample_id,
        expected_result_reference=f"expected/{sample_id}.json",
        observed_result_reference=f"observed/{comparison_id}.json",
        model_id=model_id,
        model_version=model_version,
        prompt_id=prompt_id,
        prompt_version=prompt_version,
        context_evidence_reference=f"context/{comparison_id}.json",
        result_status=result_status,
        comparison_status=comparison_status,
        operator_review_status="REVIEW_REQUIRED",
        created_at_utc="2026-07-11T02:45:00+00:00",
    )


def make_packet(records: list[dict]) -> dict:
    matrix = build_registered_comparison_matrix(records)
    return build_comparison_review_packet(matrix)


def test_review_packet_builds_valid_packet() -> None:
    packet = make_packet(
        [make_record(comparison_id="comparison-001")]
    )

    assert packet["app_id"] == APP_ID
    assert (
        packet["review_packet_version"]
        == REVIEW_PACKET_VERSION
    )
    assert packet["packet_status"] == "REVIEW_REQUIRED"
    assert packet["operator_review_status"] == (
        "REVIEW_REQUIRED"
    )
    assert packet["errors"] == []


def test_matched_single_record_has_low_priority() -> None:
    packet = make_packet(
        [make_record(comparison_id="comparison-001")]
    )

    assert packet["priority_counts"] == {"LOW": 1}
    assert packet["review_items"][0]["priority"] == "LOW"


def test_mismatch_has_high_priority() -> None:
    packet = make_packet(
        [
            make_record(
                comparison_id="comparison-001",
                comparison_status="MISMATCH",
            )
        ]
    )

    item = packet["review_items"][0]

    assert item["priority"] == "HIGH"
    assert (
        "expected_observed_mismatch_detected"
        in item["review_reasons"]
    )


def test_partial_match_has_medium_priority() -> None:
    packet = make_packet(
        [
            make_record(
                comparison_id="comparison-001",
                comparison_status="PARTIAL_MATCH",
            )
        ]
    )

    item = packet["review_items"][0]

    assert item["priority"] == "MEDIUM"
    assert (
        "partial_expected_observed_match_detected"
        in item["review_reasons"]
    )


def test_cross_model_evidence_has_medium_priority() -> None:
    packet = make_packet(
        [
            make_record(
                comparison_id="comparison-001",
                model_id="model-alpha",
            ),
            make_record(
                comparison_id="comparison-002",
                model_id="model-beta",
            ),
        ]
    )

    item = packet["review_items"][0]

    assert item["priority"] == "MEDIUM"
    assert item["cross_model_available"] is True
    assert (
        "cross_model_evidence_available"
        in item["review_reasons"]
    )


def test_review_packet_counts_priorities() -> None:
    packet = make_packet(
        [
            make_record(
                comparison_id="comparison-001",
                sample_id="sample-001",
            ),
            make_record(
                comparison_id="comparison-002",
                sample_id="sample-002",
                comparison_status="MISMATCH",
            ),
        ]
    )

    assert packet["priority_counts"] == {
        "LOW": 1,
        "HIGH": 1,
    }


def test_review_packet_orders_samples() -> None:
    packet = make_packet(
        [
            make_record(
                comparison_id="comparison-002",
                sample_id="sample-002",
            ),
            make_record(
                comparison_id="comparison-001",
                sample_id="sample-001",
            ),
        ]
    )

    assert [
        item["evaluation_sample_id"]
        for item in packet["review_items"]
    ] == ["sample-001", "sample-002"]


def test_review_packet_blocks_blocked_matrix() -> None:
    matrix = build_registered_comparison_matrix([])

    packet = build_comparison_review_packet(matrix)

    assert packet["packet_status"] == "BLOCKED"
    assert packet["result_status"] == "BLOCKED"
    assert "source_matrix_blocked" in packet["errors"]


def test_review_packet_rejects_invalid_matrix() -> None:
    record = make_record(comparison_id="comparison-001")
    record["model_id"] = ""

    matrix = build_registered_comparison_matrix([record])
    packet = build_comparison_review_packet(matrix)

    assert packet["packet_status"] == "INVALID"
    assert packet["result_status"] == "INVALID"
    assert "source_matrix_invalid" in packet["errors"]


def test_review_packet_rejects_non_mapping() -> None:
    packet = build_comparison_review_packet([])

    assert packet["packet_status"] == "INVALID"
    assert packet["errors"] == [
        "source_matrix_not_mapping"
    ]


def test_review_packet_rejects_missing_matrix_field() -> None:
    matrix = build_registered_comparison_matrix(
        [make_record(comparison_id="comparison-001")]
    )
    matrix.pop("sample_groups")

    packet = build_comparison_review_packet(matrix)

    assert packet["packet_status"] == "INVALID"
    assert (
        "missing_matrix_field:sample_groups"
        in packet["errors"]
    )


def test_review_packet_is_deterministic() -> None:
    matrix = build_registered_comparison_matrix(
        [
            make_record(
                comparison_id="comparison-002",
                sample_id="sample-002",
            ),
            make_record(
                comparison_id="comparison-001",
                sample_id="sample-001",
            ),
        ]
    )

    first = build_comparison_review_packet(matrix)
    second = build_comparison_review_packet(matrix)

    assert first == second


def test_review_packet_does_not_mutate_matrix() -> None:
    matrix = build_registered_comparison_matrix(
        [make_record(comparison_id="comparison-001")]
    )
    before = deepcopy(matrix)

    build_comparison_review_packet(matrix)

    assert matrix == before


def test_review_packet_preserves_prohibited_actions() -> None:
    packet = make_packet(
        [make_record(comparison_id="comparison-001")]
    )

    assert packet["prohibited_actions"] == list(
        PROHIBITED_REVIEW_ACTIONS
    )
    assert "automatic_winner_selection" in (
        packet["prohibited_actions"]
    )
    assert "trade_action" in packet["prohibited_actions"]


def test_review_packet_preserves_safety_boundary() -> None:
    packet = make_packet(
        [make_record(comparison_id="comparison-001")]
    )

    assert packet["paper_only"] is True
    assert packet["local_only"] is True
    assert packet["read_only"] is True
    assert packet["sidecar_only"] is True
    assert packet["operator_review_required"] is True
    assert packet["automatic_acceptance_allowed"] is False
    assert packet["automatic_model_ranking_allowed"] is False
    assert packet["automatic_model_selection_allowed"] is False
    assert packet["automatic_prompt_selection_allowed"] is False
    assert packet["automatic_winner_selection_allowed"] is False
    assert packet["model_invocation_allowed"] is False
    assert packet["prompt_execution_allowed"] is False
    assert packet["trade_action_allowed"] is False
    assert packet["real_execution_allowed"] is False
    assert packet["core_mutation_allowed"] is False