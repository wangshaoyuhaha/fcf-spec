import sys
from copy import deepcopy
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from fcf.sidecars.ai_evaluation_comparison import (
    APP_ID,
    HANDOFF_VERSION,
    PROHIBITED_REVIEW_ACTIONS,
    build_comparison_operator_handoff,
    build_comparison_record,
    build_comparison_review_packet,
    build_registered_comparison_matrix,
)


def make_record(
    *,
    comparison_id: str,
    sample_id: str,
    comparison_status: str = "MATCHED",
    model_id: str = "model-alpha",
) -> dict:
    return build_comparison_record(
        comparison_id=comparison_id,
        comparison_mode="expected_vs_observed",
        evaluation_sample_id=sample_id,
        expected_result_reference=f"expected/{sample_id}.json",
        observed_result_reference=f"observed/{comparison_id}.json",
        model_id=model_id,
        model_version="1.0.0",
        prompt_id="prompt-alpha",
        prompt_version="1.0.0",
        context_evidence_reference=f"context/{comparison_id}.json",
        result_status="RECORDED",
        comparison_status=comparison_status,
        operator_review_status="REVIEW_REQUIRED",
        created_at_utc="2026-07-11T03:00:00+00:00",
    )


def make_review_packet(records: list[dict]) -> dict:
    matrix = build_registered_comparison_matrix(records)
    return build_comparison_review_packet(matrix)


def make_handoff(records: list[dict]) -> dict:
    return build_comparison_operator_handoff(
        make_review_packet(records)
    )


def test_handoff_builds_valid_operator_queue() -> None:
    handoff = make_handoff(
        [
            make_record(
                comparison_id="comparison-001",
                sample_id="sample-001",
            )
        ]
    )

    assert handoff["app_id"] == APP_ID
    assert handoff["handoff_version"] == HANDOFF_VERSION
    assert handoff["handoff_status"] == "REVIEW_REQUIRED"
    assert handoff["result_status"] == "RECORDED"
    assert handoff["operator_review_status"] == (
        "REVIEW_REQUIRED"
    )
    assert handoff["review_item_count"] == 1
    assert handoff["errors"] == []


def test_handoff_orders_high_before_medium_before_low() -> None:
    packet = make_review_packet(
        [
            make_record(
                comparison_id="comparison-low",
                sample_id="sample-low",
            ),
            make_record(
                comparison_id="comparison-high",
                sample_id="sample-high",
                comparison_status="MISMATCH",
            ),
            make_record(
                comparison_id="comparison-medium-a",
                sample_id="sample-medium",
                model_id="model-alpha",
            ),
            make_record(
                comparison_id="comparison-medium-b",
                sample_id="sample-medium",
                model_id="model-beta",
            ),
        ]
    )

    handoff = build_comparison_operator_handoff(packet)

    assert [
        item["priority"]
        for item in handoff["review_queue"]
    ] == ["HIGH", "MEDIUM", "LOW"]

    assert [
        item["queue_position"]
        for item in handoff["review_queue"]
    ] == [1, 2, 3]


def test_handoff_preserves_priority_counts() -> None:
    handoff = make_handoff(
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

    assert handoff["priority_counts"] == {
        "LOW": 1,
        "HIGH": 1,
    }


def test_handoff_preserves_comparison_ids() -> None:
    handoff = make_handoff(
        [
            make_record(
                comparison_id="comparison-001",
                sample_id="sample-001",
            )
        ]
    )

    assert handoff["review_queue"][0][
        "comparison_ids"
    ] == ["comparison-001"]


def test_handoff_blocks_blocked_review_packet() -> None:
    packet = build_comparison_review_packet(
        build_registered_comparison_matrix([])
    )

    handoff = build_comparison_operator_handoff(packet)

    assert handoff["handoff_status"] == "BLOCKED"
    assert handoff["result_status"] == "BLOCKED"
    assert (
        "source_review_packet_blocked"
        in handoff["errors"]
    )


def test_handoff_rejects_invalid_review_packet() -> None:
    record = make_record(
        comparison_id="comparison-001",
        sample_id="sample-001",
    )
    record["model_id"] = ""

    packet = build_comparison_review_packet(
        build_registered_comparison_matrix([record])
    )

    handoff = build_comparison_operator_handoff(packet)

    assert handoff["handoff_status"] == "INVALID"
    assert handoff["result_status"] == "INVALID"
    assert (
        "source_review_packet_invalid"
        in handoff["errors"]
    )


def test_handoff_rejects_non_mapping() -> None:
    handoff = build_comparison_operator_handoff([])

    assert handoff["handoff_status"] == "INVALID"
    assert handoff["errors"] == [
        "source_review_packet_not_mapping"
    ]


def test_handoff_rejects_missing_packet_field() -> None:
    packet = make_review_packet(
        [
            make_record(
                comparison_id="comparison-001",
                sample_id="sample-001",
            )
        ]
    )
    packet.pop("review_items")

    handoff = build_comparison_operator_handoff(packet)

    assert handoff["handoff_status"] == "INVALID"
    assert (
        "missing_packet_field:review_items"
        in handoff["errors"]
    )


def test_handoff_rejects_item_count_mismatch() -> None:
    packet = make_review_packet(
        [
            make_record(
                comparison_id="comparison-001",
                sample_id="sample-001",
            )
        ]
    )
    packet["review_item_count"] = 2

    handoff = build_comparison_operator_handoff(packet)

    assert handoff["handoff_status"] == "INVALID"
    assert "review_item_count_mismatch" in (
        handoff["errors"]
    )


def test_handoff_rejects_invalid_review_item() -> None:
    packet = make_review_packet(
        [
            make_record(
                comparison_id="comparison-001",
                sample_id="sample-001",
            )
        ]
    )
    packet["review_items"][0]["priority"] = "URGENT"

    handoff = build_comparison_operator_handoff(packet)

    assert handoff["handoff_status"] == "INVALID"
    assert (
        "review_item[0]:priority_invalid"
        in handoff["errors"]
    )


def test_handoff_requires_all_prohibited_actions() -> None:
    packet = make_review_packet(
        [
            make_record(
                comparison_id="comparison-001",
                sample_id="sample-001",
            )
        ]
    )
    packet["prohibited_actions"].remove(
        "automatic_winner_selection"
    )

    handoff = build_comparison_operator_handoff(packet)

    assert handoff["handoff_status"] == "INVALID"
    assert (
        "missing_prohibited_action:"
        "automatic_winner_selection"
        in handoff["errors"]
    )


def test_handoff_is_deterministic() -> None:
    packet = make_review_packet(
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

    first = build_comparison_operator_handoff(packet)
    second = build_comparison_operator_handoff(packet)

    assert first == second


def test_handoff_does_not_mutate_review_packet() -> None:
    packet = make_review_packet(
        [
            make_record(
                comparison_id="comparison-001",
                sample_id="sample-001",
            )
        ]
    )
    before = deepcopy(packet)

    build_comparison_operator_handoff(packet)

    assert packet == before


def test_handoff_keeps_drift_review_deferred() -> None:
    handoff = make_handoff(
        [
            make_record(
                comparison_id="comparison-001",
                sample_id="sample-001",
            )
        ]
    )

    assert handoff["deferred_next_candidate"] == (
        "AI-EVALUATION-DRIFT-REVIEW-APP-1"
    )
    assert handoff[
        "drift_review_auto_start_allowed"
    ] is False
    assert handoff["next_controlled_step"] == (
        "operator_review_comparison_evidence"
    )


def test_handoff_preserves_safety_boundary() -> None:
    handoff = make_handoff(
        [
            make_record(
                comparison_id="comparison-001",
                sample_id="sample-001",
            )
        ]
    )

    assert handoff["paper_only"] is True
    assert handoff["local_only"] is True
    assert handoff["read_only"] is True
    assert handoff["sidecar_only"] is True
    assert handoff["operator_review_required"] is True
    assert handoff["automatic_acceptance_allowed"] is False
    assert handoff["automatic_model_ranking_allowed"] is False
    assert handoff["automatic_model_selection_allowed"] is False
    assert handoff["automatic_prompt_selection_allowed"] is False
    assert handoff["automatic_winner_selection_allowed"] is False
    assert handoff["model_invocation_allowed"] is False
    assert handoff["prompt_execution_allowed"] is False
    assert handoff["orchestrator_execution_allowed"] is False
    assert handoff["trade_action_allowed"] is False
    assert handoff["real_execution_allowed"] is False
    assert handoff["core_mutation_allowed"] is False

    assert handoff["prohibited_actions"] == list(
        PROHIBITED_REVIEW_ACTIONS
    )