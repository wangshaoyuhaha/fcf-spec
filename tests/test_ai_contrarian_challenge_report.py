import sys
from copy import deepcopy
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from fcf.sidecars.ai_contrarian_challenge import (
    APP_ID,
    REPORT_VERSION,
    build_challenge_evidence_record,
    build_contradiction_evidence_gap_report,
)


def make_record(
    *,
    evidence_id: str,
    artifact_id: str = "artifact-001",
    artifact_type: str = "AI_CONTEXT",
    claim_reference: str = "claims/claim-001",
    category: str = "UNSUPPORTED_CLAIM",
    severity: str = "LOW",
    status: str = "REVIEW_REQUIRED",
    risk_flags: list[str] | None = None,
) -> dict:
    if risk_flags is None:
        risk_flags = ["EVIDENCE_GAP"]

    references = (
        []
        if category == "MISSING_EVIDENCE"
        else [f"evidence/{evidence_id}.json"]
    )

    return build_challenge_evidence_record(
        challenge_evidence_id=evidence_id,
        source_artifact_id=artifact_id,
        source_artifact_type=artifact_type,
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
        risk_flags=risk_flags,
        challenge_status=status,
        operator_review_status="REVIEW_REQUIRED",
        created_at_utc="2026-07-11T04:45:00+00:00",
    )


def test_report_builds_valid_review_report() -> None:
    report = build_contradiction_evidence_gap_report(
        [make_record(evidence_id="challenge-001")]
    )

    assert report["app_id"] == APP_ID
    assert report["report_version"] == REPORT_VERSION
    assert report["report_status"] == "REVIEW_REQUIRED"
    assert report["source_record_count"] == 1
    assert report["finding_count"] == 1
    assert report["errors"] == []


def test_report_counts_evidence_gaps() -> None:
    report = build_contradiction_evidence_gap_report(
        [
            make_record(
                evidence_id="challenge-001",
                category="MISSING_EVIDENCE",
            )
        ]
    )

    assert report["evidence_gap_count"] == 1
    assert report["category_counts"] == {
        "MISSING_EVIDENCE": 1
    }


def test_report_counts_contradictions() -> None:
    report = build_contradiction_evidence_gap_report(
        [
            make_record(
                evidence_id="challenge-001",
                category=(
                    "CROSS_ARTIFACT_CONTRADICTION"
                ),
            )
        ]
    )

    assert report["contradiction_count"] == 1
    assert report["highest_severity"] == "HIGH"


def test_report_counts_multiple_categories() -> None:
    report = build_contradiction_evidence_gap_report(
        [
            make_record(
                evidence_id="challenge-001",
                category="UNSUPPORTED_CLAIM",
            ),
            make_record(
                evidence_id="challenge-002",
                category="HIDDEN_RISK",
                claim_reference="claims/claim-002",
            ),
        ]
    )

    assert report["category_counts"] == {
        "HIDDEN_RISK": 1,
        "UNSUPPORTED_CLAIM": 1,
    }


def test_report_counts_risk_flags() -> None:
    report = build_contradiction_evidence_gap_report(
        [
            make_record(
                evidence_id="challenge-001",
                risk_flags=["RISK_A", "RISK_B"],
            ),
            make_record(
                evidence_id="challenge-002",
                risk_flags=["RISK_A"],
                claim_reference="claims/claim-002",
            ),
        ]
    )

    assert report["risk_flag_counts"] == {
        "RISK_A": 2,
        "RISK_B": 1,
    }


def test_report_groups_artifacts() -> None:
    report = build_contradiction_evidence_gap_report(
        [
            make_record(
                evidence_id="challenge-001",
                artifact_id="artifact-001",
            ),
            make_record(
                evidence_id="challenge-002",
                artifact_id="artifact-001",
                claim_reference="claims/claim-002",
            ),
            make_record(
                evidence_id="challenge-003",
                artifact_id="artifact-002",
            ),
        ]
    )

    assert report["artifact_count"] == 2
    assert len(report["artifact_summaries"]) == 2
    assert report["artifact_summaries"][0][
        "source_artifact_id"
    ] == "artifact-001"


def test_report_counts_unique_claims() -> None:
    report = build_contradiction_evidence_gap_report(
        [
            make_record(
                evidence_id="challenge-001",
                claim_reference="claims/claim-001",
            ),
            make_record(
                evidence_id="challenge-002",
                claim_reference="claims/claim-002",
            ),
        ]
    )

    assert report["claim_count"] == 2


def test_no_challenge_records_produce_no_findings() -> None:
    report = build_contradiction_evidence_gap_report(
        [
            make_record(
                evidence_id="challenge-001",
                status="NO_CHALLENGE",
            )
        ]
    )

    assert report["report_status"] == "NO_CHALLENGE"
    assert report["finding_count"] == 0
    assert report["findings"] == []


def test_report_orders_findings_deterministically() -> None:
    report = build_contradiction_evidence_gap_report(
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
        for item in report["findings"]
    ] == ["challenge-001", "challenge-002"]


def test_report_rejects_duplicate_evidence_ids() -> None:
    record = make_record(evidence_id="challenge-001")

    report = build_contradiction_evidence_gap_report(
        [record, deepcopy(record)]
    )

    assert report["report_status"] == "INVALID"
    assert (
        "duplicate_challenge_evidence_id:challenge-001"
        in report["errors"]
    )


def test_report_rejects_invalid_record() -> None:
    record = make_record(evidence_id="challenge-001")
    record["source_artifact_id"] = ""

    report = build_contradiction_evidence_gap_report(
        [record]
    )

    assert report["report_status"] == "INVALID"
    assert (
        "record[0]:source_artifact_id_invalid"
        in report["errors"]
    )


def test_report_rejects_non_mapping_record() -> None:
    report = build_contradiction_evidence_gap_report([[]])

    assert report["report_status"] == "INVALID"
    assert report["errors"] == ["record_not_mapping:0"]


def test_report_blocks_empty_collection() -> None:
    report = build_contradiction_evidence_gap_report([])

    assert report["report_status"] == "BLOCKED"
    assert report["result_status"] == "BLOCKED"
    assert report["errors"] == [
        "no_challenge_evidence_records"
    ]


def test_report_rejects_invalid_collection_type() -> None:
    report = build_contradiction_evidence_gap_report(
        "not-a-record-list"
    )

    assert report["report_status"] == "INVALID"
    assert report["errors"] == ["records_invalid"]


def test_report_preserves_original_conclusions() -> None:
    report = build_contradiction_evidence_gap_report(
        [make_record(evidence_id="challenge-001")]
    )

    finding = report["findings"][0]

    assert finding["source_conclusion"] == (
        "The signal is supported."
    )
    assert finding["original_conclusion_preserved"] is True
    assert finding[
        "automatic_conclusion_replacement_allowed"
    ] is False


def test_report_does_not_mutate_records() -> None:
    records = [
        make_record(evidence_id="challenge-001"),
        make_record(
            evidence_id="challenge-002",
            category="HIDDEN_RISK",
        ),
    ]
    before = deepcopy(records)

    build_contradiction_evidence_gap_report(records)

    assert records == before


def test_report_is_deterministic() -> None:
    records = [
        make_record(
            evidence_id="challenge-002",
            artifact_id="artifact-002",
        ),
        make_record(
            evidence_id="challenge-001",
            artifact_id="artifact-001",
        ),
    ]

    first = build_contradiction_evidence_gap_report(
        records
    )
    second = build_contradiction_evidence_gap_report(
        records
    )

    assert first == second


def test_report_preserves_safety_boundary() -> None:
    report = build_contradiction_evidence_gap_report(
        [make_record(evidence_id="challenge-001")]
    )

    assert report["paper_only"] is True
    assert report["local_only"] is True
    assert report["read_only"] is True
    assert report["sidecar_only"] is True
    assert report["deterministic_only"] is True
    assert report["registered_artifacts_only"] is True
    assert report["operator_review_required"] is True
    assert report["original_conclusion_preserved"] is True
    assert report["core_mutation_allowed"] is False
    assert report["source_artifact_mutation_allowed"] is False
    assert report["model_invocation_allowed"] is False
    assert report["prompt_execution_allowed"] is False
    assert report["orchestrator_execution_allowed"] is False
    assert report["automatic_truth_decision_allowed"] is False
    assert report["automatic_winner_selection_allowed"] is False
    assert report[
        "automatic_conclusion_replacement_allowed"
    ] is False
    assert report["automatic_model_switch_allowed"] is False
    assert report["automatic_prompt_switch_allowed"] is False
    assert report["operator_review_bypass_allowed"] is False
    assert report["trade_action_allowed"] is False
    assert report["real_execution_allowed"] is False