import sys
from copy import deepcopy
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from fcf.sidecars.ai_evaluation_drift_review import (
    APP_ID,
    PROHIBITED_REVIEW_ACTIONS,
    REVIEW_PACKET_VERSION,
    build_drift_comparison_window,
    build_drift_evidence_record,
    build_drift_review_packet,
)


def make_record(
    *,
    evidence_id: str,
    sample_id: str = "sample-001",
    baseline_status: str = "MATCHED",
    candidate_status: str = "MATCHED",
    candidate_model_version: str = "1.0.0",
    candidate_prompt_version: str = "2.0.0",
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
        candidate_prompt_version=candidate_prompt_version,
        baseline_comparison_status=baseline_status,
        candidate_comparison_status=candidate_status,
        drift_status="REVIEW_REQUIRED",
        operator_review_status="REVIEW_REQUIRED",
        created_at_utc="2026-07-11T00:00:00+00:00",
    )


def make_packet(records: list[dict]) -> dict:
    window = build_drift_comparison_window(records)
    return build_drift_review_packet(window)


def test_review_packet_builds_valid_packet() -> None:
    packet = make_packet(
        [make_record(evidence_id="evidence-001")]
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


def test_no_drift_item_has_low_priority() -> None:
    packet = make_packet(
        [make_record(evidence_id="evidence-001")]
    )

    assert packet["priority_counts"] == {"LOW": 1}
    assert packet["review_items"][0]["priority"] == "LOW"


def test_confirmed_high_drift_has_high_priority() -> None:
    packet = make_packet(
        [
            make_record(
                evidence_id="evidence-001",
                candidate_status="MISMATCH",
            )
        ]
    )

    item = packet["review_items"][0]

    assert item["priority"] == "HIGH"
    assert "confirmed_drift_high_severity" in (
        item["review_reasons"]
    )


def test_confirmed_medium_drift_has_medium_priority() -> None:
    packet = make_packet(
        [
            make_record(
                evidence_id="evidence-001",
                candidate_status="PARTIAL_MATCH",
            )
        ]
    )

    assert packet["review_items"][0]["priority"] == (
        "MEDIUM"
    )


def test_insufficient_evidence_has_high_priority() -> None:
    packet = make_packet(
        [
            make_record(
                evidence_id="evidence-001",
                baseline_status="INVALID",
            )
        ]
    )

    item = packet["review_items"][0]

    assert item["priority"] == "HIGH"
    assert (
        "insufficient_evidence_requires_review"
        in item["review_reasons"]
    )


def test_potential_single_version_drift_is_low() -> None:
    packet = make_packet(
        [
            make_record(
                evidence_id="evidence-001",
                candidate_model_version="1.1.0",
            )
        ]
    )

    item = packet["review_items"][0]

    assert item["priority"] == "LOW"
    assert "model_version_change_registered" in (
        item["review_reasons"]
    )


def test_potential_multi_version_drift_is_medium() -> None:
    packet = make_packet(
        [
            make_record(
                evidence_id="evidence-001",
                candidate_model_version="1.1.0",
                candidate_prompt_version="2.1.0",
            )
        ]
    )

    assert packet["review_items"][0]["priority"] == (
        "MEDIUM"
    )


def test_review_packet_counts_priorities() -> None:
    packet = make_packet(
        [
            make_record(
                evidence_id="evidence-low",
                sample_id="sample-low",
            ),
            make_record(
                evidence_id="evidence-medium",
                sample_id="sample-medium",
                candidate_status="PARTIAL_MATCH",
            ),
            make_record(
                evidence_id="evidence-high",
                sample_id="sample-high",
                candidate_status="MISMATCH",
            ),
        ]
    )

    assert packet["priority_counts"] == {
        "LOW": 1,
        "MEDIUM": 1,
        "HIGH": 1,
    }


def test_review_packet_orders_items_deterministically() -> None:
    packet = make_packet(
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

    assert [
        item["drift_evidence_id"]
        for item in packet["review_items"]
    ] == ["evidence-001", "evidence-002"]


def test_review_packet_blocks_blocked_window() -> None:
    window = build_drift_comparison_window([])

    packet = build_drift_review_packet(window)

    assert packet["packet_status"] == "BLOCKED"
    assert packet["result_status"] == "BLOCKED"
    assert "source_window_blocked" in packet["errors"]


def test_review_packet_rejects_invalid_window() -> None:
    record = make_record(evidence_id="evidence-001")
    record["model_id"] = ""

    window = build_drift_comparison_window([record])
    packet = build_drift_review_packet(window)

    assert packet["packet_status"] == "INVALID"
    assert "source_window_invalid" in packet["errors"]


def test_review_packet_rejects_non_mapping() -> None:
    packet = build_drift_review_packet([])

    assert packet["packet_status"] == "INVALID"
    assert packet["errors"] == [
        "source_window_not_mapping"
    ]


def test_review_packet_rejects_missing_window_field() -> None:
    window = build_drift_comparison_window(
        [make_record(evidence_id="evidence-001")]
    )
    window.pop("items")

    packet = build_drift_review_packet(window)

    assert packet["packet_status"] == "INVALID"
    assert "missing_window_field:items" in packet["errors"]


def test_review_packet_rejects_invalid_window_item() -> None:
    window = build_drift_comparison_window(
        [make_record(evidence_id="evidence-001")]
    )
    window["items"][0]["drift_severity"] = "CRITICAL"

    packet = build_drift_review_packet(window)

    assert packet["packet_status"] == "INVALID"
    assert (
        "window_item[0]:drift_severity_invalid"
        in packet["errors"]
    )


def test_review_packet_preserves_prohibited_actions() -> None:
    packet = make_packet(
        [make_record(evidence_id="evidence-001")]
    )

    assert packet["prohibited_actions"] == list(
        PROHIBITED_REVIEW_ACTIONS
    )
    assert "automatic_model_switch" in (
        packet["prohibited_actions"]
    )
    assert "automatic_rollback" in (
        packet["prohibited_actions"]
    )


def test_review_packet_does_not_mutate_window() -> None:
    window = build_drift_comparison_window(
        [make_record(evidence_id="evidence-001")]
    )
    before = deepcopy(window)

    build_drift_review_packet(window)

    assert window == before


def test_review_packet_is_deterministic() -> None:
    window = build_drift_comparison_window(
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

    first = build_drift_review_packet(window)
    second = build_drift_review_packet(window)

    assert first == second


def test_review_packet_preserves_safety_boundary() -> None:
    packet = make_packet(
        [make_record(evidence_id="evidence-001")]
    )

    assert packet["paper_only"] is True
    assert packet["local_only"] is True
    assert packet["read_only"] is True
    assert packet["sidecar_only"] is True
    assert packet["operator_review_required"] is True
    assert packet["deterministic_only"] is True
    assert packet["registered_artifacts_only"] is True
    assert packet["core_mutation_allowed"] is False
    assert packet["model_invocation_allowed"] is False
    assert packet["prompt_execution_allowed"] is False
    assert packet["orchestrator_execution_allowed"] is False
    assert packet["automatic_approval_allowed"] is False
    assert packet["automatic_rejection_allowed"] is False
    assert packet["automatic_rollback_allowed"] is False
    assert packet["automatic_model_ranking_allowed"] is False
    assert packet["automatic_model_selection_allowed"] is False
    assert packet["automatic_prompt_selection_allowed"] is False
    assert packet["automatic_model_switch_allowed"] is False
    assert packet["automatic_prompt_switch_allowed"] is False
    assert packet["trade_action_allowed"] is False
    assert packet["real_execution_allowed"] is False