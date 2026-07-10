import sys
from copy import deepcopy
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from fcf.sidecars.ai_evaluation_drift_review import (
    APP_ID,
    HANDOFF_VERSION,
    PROHIBITED_REVIEW_ACTIONS,
    build_drift_comparison_window,
    build_drift_evidence_record,
    build_drift_operator_handoff,
    build_drift_review_packet,
)


def make_record(
    *,
    evidence_id: str,
    sample_id: str,
    candidate_status: str = "MATCHED",
    candidate_model_version: str = "1.0.0",
) -> dict:
    return build_drift_evidence_record(
        drift_evidence_id=evidence_id,
        evaluation_sample_id=sample_id,
        baseline_reference=f"baseline/{evidence_id}.json",
        candidate_reference=f"candidate/{evidence_id}.json",
        baseline_created_at_utc=(
            "2026-07-01T00:00:00+00:00"
        ),
        candidate_created_at_utc=(
            "2026-07-10T00:00:00+00:00"
        ),
        model_id="model-alpha",
        baseline_model_version="1.0.0",
        candidate_model_version=candidate_model_version,
        prompt_id="prompt-alpha",
        baseline_prompt_version="2.0.0",
        candidate_prompt_version="2.0.0",
        baseline_comparison_status="MATCHED",
        candidate_comparison_status=candidate_status,
        drift_status="REVIEW_REQUIRED",
        operator_review_status="REVIEW_REQUIRED",
        created_at_utc="2026-07-11T00:00:00+00:00",
    )


def make_review_packet(records: list[dict]) -> dict:
    window = build_drift_comparison_window(records)
    return build_drift_review_packet(window)


def make_handoff(records: list[dict]) -> dict:
    return build_drift_operator_handoff(
        make_review_packet(records)
    )


def test_handoff_builds_valid_queue() -> None:
    handoff = make_handoff(
        [
            make_record(
                evidence_id="evidence-001",
                sample_id="sample-001",
            )
        ]
    )

    assert handoff["app_id"] == APP_ID
    assert handoff["handoff_version"] == HANDOFF_VERSION
    assert handoff["handoff_status"] == "REVIEW_REQUIRED"
    assert handoff["result_status"] == "RECORDED"
    assert handoff["review_item_count"] == 1
    assert handoff["errors"] == []


def test_handoff_orders_high_medium_low() -> None:
    handoff = make_handoff(
        [
            make_record(
                evidence_id="evidence-low",
                sample_id="sample-low",
            ),
            make_record(
                evidence_id="evidence-high",
                sample_id="sample-high",
                candidate_status="MISMATCH",
            ),
            make_record(
                evidence_id="evidence-medium",
                sample_id="sample-medium",
                candidate_status="PARTIAL_MATCH",
            ),
        ]
    )

    assert [
        item["priority"]
        for item in handoff["review_queue"]
    ] == ["HIGH", "MEDIUM", "LOW"]


def test_handoff_assigns_queue_positions() -> None:
    handoff = make_handoff(
        [
            make_record(
                evidence_id="evidence-001",
                sample_id="sample-001",
            ),
            make_record(
                evidence_id="evidence-002",
                sample_id="sample-002",
            ),
        ]
    )

    assert [
        item["queue_position"]
        for item in handoff["review_queue"]
    ] == [1, 2]


def test_handoff_preserves_priority_counts() -> None:
    handoff = make_handoff(
        [
            make_record(
                evidence_id="evidence-low",
                sample_id="sample-low",
            ),
            make_record(
                evidence_id="evidence-high",
                sample_id="sample-high",
                candidate_status="MISMATCH",
            ),
        ]
    )

    assert handoff["priority_counts"] == {
        "LOW": 1,
        "HIGH": 1,
    }


def test_handoff_preserves_references_and_reasons() -> None:
    handoff = make_handoff(
        [
            make_record(
                evidence_id="evidence-001",
                sample_id="sample-001",
                candidate_model_version="1.1.0",
            )
        ]
    )

    item = handoff["review_queue"][0]

    assert item["baseline_reference"] == (
        "baseline/evidence-001.json"
    )
    assert item["candidate_reference"] == (
        "candidate/evidence-001.json"
    )
    assert "MODEL_VERSION_CHANGED" in item[
        "reason_codes"
    ]


def test_no_drift_still_requires_operator_review() -> None:
    handoff = make_handoff(
        [
            make_record(
                evidence_id="evidence-001",
                sample_id="sample-001",
            )
        ]
    )

    item = handoff["review_queue"][0]

    assert item["drift_status"] == "NO_DRIFT"
    assert item["operator_review_status"] == (
        "REVIEW_REQUIRED"
    )


def test_handoff_blocks_blocked_packet() -> None:
    packet = build_drift_review_packet(
        build_drift_comparison_window([])
    )

    handoff = build_drift_operator_handoff(packet)

    assert handoff["handoff_status"] == "BLOCKED"
    assert handoff["result_status"] == "BLOCKED"
    assert (
        "source_review_packet_blocked"
        in handoff["errors"]
    )


def test_handoff_rejects_invalid_packet() -> None:
    record = make_record(
        evidence_id="evidence-001",
        sample_id="sample-001",
    )
    record["model_id"] = ""

    packet = build_drift_review_packet(
        build_drift_comparison_window([record])
    )

    handoff = build_drift_operator_handoff(packet)

    assert handoff["handoff_status"] == "INVALID"
    assert (
        "source_review_packet_invalid"
        in handoff["errors"]
    )


def test_handoff_rejects_non_mapping() -> None:
    handoff = build_drift_operator_handoff([])

    assert handoff["handoff_status"] == "INVALID"
    assert handoff["errors"] == [
        "source_review_packet_not_mapping"
    ]


def test_handoff_rejects_missing_packet_field() -> None:
    packet = make_review_packet(
        [
            make_record(
                evidence_id="evidence-001",
                sample_id="sample-001",
            )
        ]
    )
    packet.pop("review_items")

    handoff = build_drift_operator_handoff(packet)

    assert handoff["handoff_status"] == "INVALID"
    assert "missing_packet_field:review_items" in (
        handoff["errors"]
    )


def test_handoff_rejects_item_count_mismatch() -> None:
    packet = make_review_packet(
        [
            make_record(
                evidence_id="evidence-001",
                sample_id="sample-001",
            )
        ]
    )
    packet["review_item_count"] = 2

    handoff = build_drift_operator_handoff(packet)

    assert handoff["handoff_status"] == "INVALID"
    assert "review_item_count_mismatch" in (
        handoff["errors"]
    )


def test_handoff_rejects_invalid_priority() -> None:
    packet = make_review_packet(
        [
            make_record(
                evidence_id="evidence-001",
                sample_id="sample-001",
            )
        ]
    )
    packet["review_items"][0]["priority"] = "URGENT"

    handoff = build_drift_operator_handoff(packet)

    assert handoff["handoff_status"] == "INVALID"
    assert "review_item[0]:priority_invalid" in (
        handoff["errors"]
    )


def test_handoff_requires_prohibited_actions() -> None:
    packet = make_review_packet(
        [
            make_record(
                evidence_id="evidence-001",
                sample_id="sample-001",
            )
        ]
    )
    packet["prohibited_actions"].remove(
        "automatic_rollback"
    )

    handoff = build_drift_operator_handoff(packet)

    assert handoff["handoff_status"] == "INVALID"
    assert (
        "missing_prohibited_action:automatic_rollback"
        in handoff["errors"]
    )


def test_handoff_is_deterministic() -> None:
    packet = make_review_packet(
        [
            make_record(
                evidence_id="evidence-002",
                sample_id="sample-002",
            ),
            make_record(
                evidence_id="evidence-001",
                sample_id="sample-001",
            ),
        ]
    )

    first = build_drift_operator_handoff(packet)
    second = build_drift_operator_handoff(packet)

    assert first == second


def test_handoff_does_not_mutate_packet() -> None:
    packet = make_review_packet(
        [
            make_record(
                evidence_id="evidence-001",
                sample_id="sample-001",
            )
        ]
    )
    before = deepcopy(packet)

    build_drift_operator_handoff(packet)

    assert packet == before


def test_handoff_blocks_automatic_transition() -> None:
    handoff = make_handoff(
        [
            make_record(
                evidence_id="evidence-001",
                sample_id="sample-001",
            )
        ]
    )

    assert handoff["automatic_next_phase_allowed"] is False
    assert handoff["next_controlled_step"] == (
        "operator_review_registered_drift_evidence"
    )


def test_handoff_preserves_safety_boundary() -> None:
    handoff = make_handoff(
        [
            make_record(
                evidence_id="evidence-001",
                sample_id="sample-001",
            )
        ]
    )

    assert handoff["paper_only"] is True
    assert handoff["local_only"] is True
    assert handoff["read_only"] is True
    assert handoff["sidecar_only"] is True
    assert handoff["operator_review_required"] is True
    assert handoff["deterministic_only"] is True
    assert handoff["registered_artifacts_only"] is True
    assert handoff["core_mutation_allowed"] is False
    assert handoff["model_invocation_allowed"] is False
    assert handoff["prompt_execution_allowed"] is False
    assert handoff["orchestrator_execution_allowed"] is False
    assert handoff["automatic_approval_allowed"] is False
    assert handoff["automatic_rejection_allowed"] is False
    assert handoff["automatic_rollback_allowed"] is False
    assert handoff["automatic_model_ranking_allowed"] is False
    assert handoff["automatic_model_selection_allowed"] is False
    assert handoff["automatic_prompt_selection_allowed"] is False
    assert handoff["automatic_model_switch_allowed"] is False
    assert handoff["automatic_prompt_switch_allowed"] is False
    assert handoff["trade_action_allowed"] is False
    assert handoff["real_execution_allowed"] is False
    assert handoff["prohibited_actions"] == list(
        PROHIBITED_REVIEW_ACTIONS
    )