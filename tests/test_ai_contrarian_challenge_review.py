import sys
from copy import deepcopy
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from fcf.sidecars.ai_contrarian_challenge import (
    APP_ID,
    PROHIBITED_REVIEW_ACTIONS,
    REVIEW_PACKET_VERSION,
    build_challenge_evidence_record,
    build_challenge_review_packet,
    build_contradiction_evidence_gap_report,
)


def make_record(
    *,
    evidence_id: str,
    category: str = "UNSUPPORTED_CLAIM",
    severity: str = "LOW",
    status: str = "REVIEW_REQUIRED",
    artifact_id: str = "artifact-001",
    claim_reference: str = "claims/claim-001",
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
        created_at_utc="2026-07-11T05:00:00+00:00",
    )


def make_packet(records: list[dict]) -> dict:
    report = build_contradiction_evidence_gap_report(
        records
    )
    return build_challenge_review_packet(report)


def test_review_packet_is_valid() -> None:
    packet = make_packet(
        [make_record(evidence_id="challenge-001")]
    )

    assert packet["app_id"] == APP_ID
    assert (
        packet["review_packet_version"]
        == REVIEW_PACKET_VERSION
    )
    assert packet["packet_status"] == "REVIEW_REQUIRED"
    assert packet["review_item_count"] == 1
    assert packet["errors"] == []


def test_missing_evidence_has_high_priority() -> None:
    packet = make_packet(
        [
            make_record(
                evidence_id="challenge-001",
                category="MISSING_EVIDENCE",
            )
        ]
    )

    item = packet["review_items"][0]

    assert item["priority"] == "HIGH"
    assert "evidence_gap_requires_review" in (
        item["review_reasons"]
    )


def test_hidden_risk_has_high_priority() -> None:
    packet = make_packet(
        [
            make_record(
                evidence_id="challenge-001",
                category="HIDDEN_RISK",
            )
        ]
    )

    assert packet["review_items"][0]["priority"] == (
        "HIGH"
    )


def test_contradiction_has_high_priority() -> None:
    packet = make_packet(
        [
            make_record(
                evidence_id="challenge-001",
                category=(
                    "CROSS_ARTIFACT_CONTRADICTION"
                ),
            )
        ]
    )

    item = packet["review_items"][0]

    assert item["priority"] == "HIGH"
    assert (
        "cross_artifact_contradiction_requires_review"
        in item["review_reasons"]
    )


def test_unsupported_claim_has_medium_priority() -> None:
    packet = make_packet(
        [make_record(evidence_id="challenge-001")]
    )

    assert packet["review_items"][0]["priority"] == (
        "MEDIUM"
    )


def test_high_input_severity_has_high_priority() -> None:
    packet = make_packet(
        [
            make_record(
                evidence_id="challenge-001",
                severity="HIGH",
            )
        ]
    )

    assert packet["review_items"][0]["priority"] == (
        "HIGH"
    )


def test_packet_counts_priorities() -> None:
    packet = make_packet(
        [
            make_record(
                evidence_id="challenge-medium",
            ),
            make_record(
                evidence_id="challenge-high",
                category="HIDDEN_RISK",
                claim_reference="claims/claim-002",
            ),
        ]
    )

    assert packet["priority_counts"] == {
        "MEDIUM": 1,
        "HIGH": 1,
    }


def test_packet_orders_items_deterministically() -> None:
    packet = make_packet(
        [
            make_record(
                evidence_id="challenge-002",
                artifact_id="artifact-002",
            ),
            make_record(
                evidence_id="challenge-001",
                artifact_id="artifact-001",
            ),
        ]
    )

    assert [
        item["challenge_evidence_id"]
        for item in packet["review_items"]
    ] == ["challenge-001", "challenge-002"]


def test_no_challenge_report_has_empty_review_items() -> None:
    packet = make_packet(
        [
            make_record(
                evidence_id="challenge-001",
                status="NO_CHALLENGE",
            )
        ]
    )

    assert packet["packet_status"] == "REVIEW_REQUIRED"
    assert packet["source_report_status"] == "NO_CHALLENGE"
    assert packet["review_item_count"] == 0
    assert packet["review_items"] == []


def test_packet_blocks_blocked_report() -> None:
    report = build_contradiction_evidence_gap_report([])

    packet = build_challenge_review_packet(report)

    assert packet["packet_status"] == "BLOCKED"
    assert packet["result_status"] == "BLOCKED"
    assert "source_report_blocked" in packet["errors"]


def test_packet_rejects_invalid_report() -> None:
    record = make_record(evidence_id="challenge-001")
    record["source_artifact_id"] = ""

    report = build_contradiction_evidence_gap_report(
        [record]
    )
    packet = build_challenge_review_packet(report)

    assert packet["packet_status"] == "INVALID"
    assert "source_report_invalid" in packet["errors"]


def test_packet_rejects_non_mapping() -> None:
    packet = build_challenge_review_packet([])

    assert packet["packet_status"] == "INVALID"
    assert packet["errors"] == [
        "source_report_not_mapping"
    ]


def test_packet_rejects_missing_report_field() -> None:
    report = build_contradiction_evidence_gap_report(
        [make_record(evidence_id="challenge-001")]
    )
    report.pop("findings")

    packet = build_challenge_review_packet(report)

    assert packet["packet_status"] == "INVALID"
    assert "missing_report_field:findings" in (
        packet["errors"]
    )


def test_packet_rejects_finding_count_mismatch() -> None:
    report = build_contradiction_evidence_gap_report(
        [make_record(evidence_id="challenge-001")]
    )
    report["finding_count"] = 2

    packet = build_challenge_review_packet(report)

    assert packet["packet_status"] == "INVALID"
    assert "finding_count_mismatch" in packet["errors"]


def test_packet_preserves_source_conclusion() -> None:
    packet = make_packet(
        [make_record(evidence_id="challenge-001")]
    )

    item = packet["review_items"][0]

    assert item["source_conclusion"] == (
        "The signal is supported."
    )
    assert item["original_conclusion_preserved"] is True
    assert item[
        "automatic_conclusion_replacement_allowed"
    ] is False


def test_packet_preserves_prohibited_actions() -> None:
    packet = make_packet(
        [make_record(evidence_id="challenge-001")]
    )

    assert packet["prohibited_actions"] == list(
        PROHIBITED_REVIEW_ACTIONS
    )
    assert "automatic_truth_decision" in (
        packet["prohibited_actions"]
    )
    assert "operator_review_bypass" in (
        packet["prohibited_actions"]
    )


def test_packet_is_deterministic_and_non_mutating() -> None:
    report = build_contradiction_evidence_gap_report(
        [make_record(evidence_id="challenge-001")]
    )
    before = deepcopy(report)

    first = build_challenge_review_packet(report)
    second = build_challenge_review_packet(report)

    assert first == second
    assert report == before


def test_packet_preserves_safety_boundary() -> None:
    packet = make_packet(
        [make_record(evidence_id="challenge-001")]
    )

    assert packet["paper_only"] is True
    assert packet["local_only"] is True
    assert packet["read_only"] is True
    assert packet["sidecar_only"] is True
    assert packet["deterministic_only"] is True
    assert packet["registered_artifacts_only"] is True
    assert packet["operator_review_required"] is True
    assert packet["original_conclusion_preserved"] is True
    assert packet["core_mutation_allowed"] is False
    assert packet["source_artifact_mutation_allowed"] is False
    assert packet["model_invocation_allowed"] is False
    assert packet["prompt_execution_allowed"] is False
    assert packet["orchestrator_execution_allowed"] is False
    assert packet["automatic_truth_decision_allowed"] is False
    assert packet["automatic_winner_selection_allowed"] is False
    assert packet[
        "automatic_conclusion_replacement_allowed"
    ] is False
    assert packet["operator_review_bypass_allowed"] is False
    assert packet["trade_action_allowed"] is False
    assert packet["real_execution_allowed"] is False