import sys
from copy import deepcopy
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from fcf.sidecars.ai_contrarian_challenge import (
    APP_ID,
    HANDOFF_VERSION,
    PROHIBITED_REVIEW_ACTIONS,
    build_challenge_evidence_record,
    build_challenge_operator_handoff,
    build_challenge_review_packet,
    build_contradiction_evidence_gap_report,
)


def make_record(
    *,
    evidence_id: str,
    artifact_id: str,
    claim_reference: str,
    category: str = "UNSUPPORTED_CLAIM",
    severity: str = "LOW",
    status: str = "REVIEW_REQUIRED",
) -> dict:
    references = (
        []
        if category == "MISSING_EVIDENCE"
        else [f"evidence/{evidence_id}.json"]
    )

    return build_challenge_evidence_record(
        challenge_evidence_id=evidence_id,
        source_artifact_id=artifact_id,
        source_artifact_type="AI_CONTEXT",
        source_artifact_reference=(
            f"artifacts/{artifact_id}.json"
        ),
        claim_reference=claim_reference,
        source_conclusion="The signal is supported.",
        challenge_category=category,
        challenge_severity=severity,
        challenge_statement=(
            "The registered conclusion requires review."
        ),
        evidence_references=references,
        risk_flags=["EVIDENCE_GAP"],
        challenge_status=status,
        operator_review_status="REVIEW_REQUIRED",
        created_at_utc="2026-07-11T05:15:00+00:00",
    )


def make_review_packet(records: list[dict]) -> dict:
    report = build_contradiction_evidence_gap_report(
        records
    )
    return build_challenge_review_packet(report)


def make_handoff(records: list[dict]) -> dict:
    return build_challenge_operator_handoff(
        make_review_packet(records)
    )


def test_handoff_builds_valid_queue() -> None:
    handoff = make_handoff(
        [
            make_record(
                evidence_id="challenge-001",
                artifact_id="artifact-001",
                claim_reference="claims/claim-001",
            )
        ]
    )

    assert handoff["app_id"] == APP_ID
    assert handoff["handoff_version"] == HANDOFF_VERSION
    assert handoff["handoff_status"] == "REVIEW_REQUIRED"
    assert handoff["result_status"] == "RECORDED"
    assert handoff["review_item_count"] == 1
    assert handoff["errors"] == []


def test_handoff_orders_high_before_medium() -> None:
    handoff = make_handoff(
        [
            make_record(
                evidence_id="challenge-medium",
                artifact_id="artifact-medium",
                claim_reference="claims/medium",
            ),
            make_record(
                evidence_id="challenge-high",
                artifact_id="artifact-high",
                claim_reference="claims/high",
                category="HIDDEN_RISK",
            ),
        ]
    )

    assert [
        item["priority"]
        for item in handoff["review_queue"]
    ] == ["HIGH", "MEDIUM"]


def test_handoff_assigns_queue_positions() -> None:
    handoff = make_handoff(
        [
            make_record(
                evidence_id="challenge-002",
                artifact_id="artifact-002",
                claim_reference="claims/claim-002",
            ),
            make_record(
                evidence_id="challenge-001",
                artifact_id="artifact-001",
                claim_reference="claims/claim-001",
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
                evidence_id="challenge-medium",
                artifact_id="artifact-medium",
                claim_reference="claims/medium",
            ),
            make_record(
                evidence_id="challenge-high",
                artifact_id="artifact-high",
                claim_reference="claims/high",
                category="MISSING_EVIDENCE",
            ),
        ]
    )

    assert handoff["priority_counts"] == {
        "MEDIUM": 1,
        "HIGH": 1,
    }


def test_handoff_preserves_source_conclusion() -> None:
    handoff = make_handoff(
        [
            make_record(
                evidence_id="challenge-001",
                artifact_id="artifact-001",
                claim_reference="claims/claim-001",
            )
        ]
    )

    item = handoff["review_queue"][0]

    assert item["source_conclusion"] == (
        "The signal is supported."
    )
    assert item["original_conclusion_preserved"] is True
    assert item[
        "automatic_conclusion_replacement_allowed"
    ] is False


def test_no_challenge_produces_empty_queue() -> None:
    handoff = make_handoff(
        [
            make_record(
                evidence_id="challenge-001",
                artifact_id="artifact-001",
                claim_reference="claims/claim-001",
                status="NO_CHALLENGE",
            )
        ]
    )

    assert handoff["handoff_status"] == "REVIEW_REQUIRED"
    assert handoff["source_report_status"] == "NO_CHALLENGE"
    assert handoff["review_item_count"] == 0
    assert handoff["review_queue"] == []


def test_handoff_blocks_blocked_packet() -> None:
    packet = build_challenge_review_packet(
        build_contradiction_evidence_gap_report([])
    )

    handoff = build_challenge_operator_handoff(packet)

    assert handoff["handoff_status"] == "BLOCKED"
    assert handoff["result_status"] == "BLOCKED"
    assert (
        "source_review_packet_blocked"
        in handoff["errors"]
    )


def test_handoff_rejects_invalid_packet() -> None:
    record = make_record(
        evidence_id="challenge-001",
        artifact_id="artifact-001",
        claim_reference="claims/claim-001",
    )
    record["source_artifact_id"] = ""

    packet = build_challenge_review_packet(
        build_contradiction_evidence_gap_report(
            [record]
        )
    )

    handoff = build_challenge_operator_handoff(packet)

    assert handoff["handoff_status"] == "INVALID"
    assert (
        "source_review_packet_invalid"
        in handoff["errors"]
    )


def test_handoff_rejects_non_mapping() -> None:
    handoff = build_challenge_operator_handoff([])

    assert handoff["handoff_status"] == "INVALID"
    assert handoff["errors"] == [
        "source_review_packet_not_mapping"
    ]


def test_handoff_rejects_missing_packet_field() -> None:
    packet = make_review_packet(
        [
            make_record(
                evidence_id="challenge-001",
                artifact_id="artifact-001",
                claim_reference="claims/claim-001",
            )
        ]
    )
    packet.pop("review_items")

    handoff = build_challenge_operator_handoff(packet)

    assert handoff["handoff_status"] == "INVALID"
    assert "missing_packet_field:review_items" in (
        handoff["errors"]
    )


def test_handoff_rejects_item_count_mismatch() -> None:
    packet = make_review_packet(
        [
            make_record(
                evidence_id="challenge-001",
                artifact_id="artifact-001",
                claim_reference="claims/claim-001",
            )
        ]
    )
    packet["review_item_count"] = 2

    handoff = build_challenge_operator_handoff(packet)

    assert handoff["handoff_status"] == "INVALID"
    assert "review_item_count_mismatch" in (
        handoff["errors"]
    )


def test_handoff_rejects_priority_count_mismatch() -> None:
    packet = make_review_packet(
        [
            make_record(
                evidence_id="challenge-001",
                artifact_id="artifact-001",
                claim_reference="claims/claim-001",
            )
        ]
    )
    packet["priority_counts"] = {"MEDIUM": 2}

    handoff = build_challenge_operator_handoff(packet)

    assert handoff["handoff_status"] == "INVALID"
    assert "priority_count_total_mismatch" in (
        handoff["errors"]
    )


def test_handoff_rejects_invalid_priority() -> None:
    packet = make_review_packet(
        [
            make_record(
                evidence_id="challenge-001",
                artifact_id="artifact-001",
                claim_reference="claims/claim-001",
            )
        ]
    )
    packet["review_items"][0]["priority"] = "URGENT"

    handoff = build_challenge_operator_handoff(packet)

    assert handoff["handoff_status"] == "INVALID"
    assert "review_item[0]:priority_invalid" in (
        handoff["errors"]
    )


def test_handoff_requires_prohibited_actions() -> None:
    packet = make_review_packet(
        [
            make_record(
                evidence_id="challenge-001",
                artifact_id="artifact-001",
                claim_reference="claims/claim-001",
            )
        ]
    )
    packet["prohibited_actions"].remove(
        "automatic_truth_decision"
    )

    handoff = build_challenge_operator_handoff(packet)

    assert handoff["handoff_status"] == "INVALID"
    assert (
        "missing_prohibited_action:"
        "automatic_truth_decision"
        in handoff["errors"]
    )


def test_handoff_is_deterministic() -> None:
    packet = make_review_packet(
        [
            make_record(
                evidence_id="challenge-002",
                artifact_id="artifact-002",
                claim_reference="claims/claim-002",
            ),
            make_record(
                evidence_id="challenge-001",
                artifact_id="artifact-001",
                claim_reference="claims/claim-001",
            ),
        ]
    )

    first = build_challenge_operator_handoff(packet)
    second = build_challenge_operator_handoff(packet)

    assert first == second


def test_handoff_does_not_mutate_packet() -> None:
    packet = make_review_packet(
        [
            make_record(
                evidence_id="challenge-001",
                artifact_id="artifact-001",
                claim_reference="claims/claim-001",
            )
        ]
    )
    before = deepcopy(packet)

    build_challenge_operator_handoff(packet)

    assert packet == before


def test_handoff_blocks_automatic_next_phase() -> None:
    handoff = make_handoff(
        [
            make_record(
                evidence_id="challenge-001",
                artifact_id="artifact-001",
                claim_reference="claims/claim-001",
            )
        ]
    )

    assert handoff["automatic_next_phase_allowed"] is False
    assert handoff["next_controlled_step"] == (
        "operator_review_contrarian_challenge_findings"
    )


def test_handoff_preserves_safety_boundary() -> None:
    handoff = make_handoff(
        [
            make_record(
                evidence_id="challenge-001",
                artifact_id="artifact-001",
                claim_reference="claims/claim-001",
            )
        ]
    )

    assert handoff["paper_only"] is True
    assert handoff["local_only"] is True
    assert handoff["read_only"] is True
    assert handoff["sidecar_only"] is True
    assert handoff["deterministic_only"] is True
    assert handoff["registered_artifacts_only"] is True
    assert handoff["operator_review_required"] is True
    assert handoff["original_conclusion_preserved"] is True
    assert handoff["core_mutation_allowed"] is False
    assert handoff["source_artifact_mutation_allowed"] is False
    assert handoff["model_invocation_allowed"] is False
    assert handoff["prompt_execution_allowed"] is False
    assert handoff["orchestrator_execution_allowed"] is False
    assert handoff["automatic_truth_decision_allowed"] is False
    assert handoff["automatic_winner_selection_allowed"] is False
    assert handoff[
        "automatic_conclusion_replacement_allowed"
    ] is False
    assert handoff["operator_review_bypass_allowed"] is False
    assert handoff["automatic_next_phase_allowed"] is False
    assert handoff["trade_action_allowed"] is False
    assert handoff["real_execution_allowed"] is False
    assert handoff["prohibited_actions"] == list(
        PROHIBITED_REVIEW_ACTIONS
    )