import sys
from copy import deepcopy
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from fcf.sidecars.ai_contrarian_challenge import (
    APP_ID,
    RULE_ENGINE_VERSION,
    apply_challenge_rules,
    build_challenge_evidence_record,
)


def make_record(
    *,
    category: str = "UNSUPPORTED_CLAIM",
    severity: str = "LOW",
    status: str = "REVIEW_REQUIRED",
    evidence_references: list[str] | None = None,
    risk_flags: list[str] | None = None,
) -> dict:
    if evidence_references is None:
        evidence_references = [
            "evidence/context-001.json"
        ]

    if risk_flags is None:
        risk_flags = ["EVIDENCE_GAP"]

    if category == "MISSING_EVIDENCE":
        evidence_references = []

    return build_challenge_evidence_record(
        challenge_evidence_id="challenge-001",
        source_artifact_id="context-001",
        source_artifact_type="AI_CONTEXT",
        source_artifact_reference=(
            "artifacts/ai-context/context-001.json"
        ),
        claim_reference="claims/claim-001",
        source_conclusion="The signal is supported.",
        challenge_category=category,
        challenge_severity=severity,
        challenge_statement=(
            "The registered evidence requires challenge review."
        ),
        evidence_references=evidence_references,
        risk_flags=risk_flags,
        challenge_status=status,
        operator_review_status="REVIEW_REQUIRED",
        created_at_utc="2026-07-11T04:30:00+00:00",
    )


def test_rule_engine_builds_review_report() -> None:
    report = apply_challenge_rules(make_record())

    assert report["app_id"] == APP_ID
    assert (
        report["rule_engine_version"]
        == RULE_ENGINE_VERSION
    )
    assert report["challenge_status"] == "REVIEW_REQUIRED"
    assert report["result_status"] == "REVIEW_REQUIRED"
    assert report["finding_count"] == 1
    assert report["errors"] == []


def test_unsupported_claim_rule() -> None:
    report = apply_challenge_rules(make_record())
    finding = report["findings"][0]

    assert finding["rule_id"] == (
        "RULE_UNSUPPORTED_CLAIM"
    )
    assert finding["reason_code"] == (
        "CLAIM_SUPPORT_INCOMPLETE"
    )
    assert report["highest_severity"] == "MEDIUM"


def test_missing_evidence_rule_is_high() -> None:
    report = apply_challenge_rules(
        make_record(category="MISSING_EVIDENCE")
    )

    finding = report["findings"][0]

    assert finding["rule_id"] == (
        "RULE_MISSING_EVIDENCE"
    )
    assert finding["reason_code"] == (
        "REGISTERED_EVIDENCE_MISSING"
    )
    assert report["highest_severity"] == "HIGH"


def test_logical_gap_rule() -> None:
    report = apply_challenge_rules(
        make_record(category="LOGICAL_GAP")
    )

    assert report["findings"][0]["rule_id"] == (
        "RULE_LOGICAL_GAP"
    )


def test_hidden_risk_rule_is_high() -> None:
    report = apply_challenge_rules(
        make_record(category="HIDDEN_RISK")
    )

    assert report["highest_severity"] == "HIGH"
    assert report["findings"][0]["reason_code"] == (
        "RISK_NOT_REFLECTED_IN_CONCLUSION"
    )


def test_overconfidence_rule() -> None:
    report = apply_challenge_rules(
        make_record(category="OVERCONFIDENCE")
    )

    assert report["findings"][0]["rule_id"] == (
        "RULE_OVERCONFIDENCE"
    )


def test_contradiction_rule_is_high() -> None:
    report = apply_challenge_rules(
        make_record(
            category="CROSS_ARTIFACT_CONTRADICTION"
        )
    )

    assert report["highest_severity"] == "HIGH"
    assert report["findings"][0]["reason_code"] == (
        "REGISTERED_ARTIFACTS_CONTRADICT"
    )


def test_input_high_severity_is_preserved() -> None:
    report = apply_challenge_rules(
        make_record(severity="HIGH")
    )

    assert report["highest_severity"] == "HIGH"


def test_no_challenge_has_no_findings() -> None:
    report = apply_challenge_rules(
        make_record(status="NO_CHALLENGE")
    )

    assert report["challenge_status"] == "NO_CHALLENGE"
    assert report["result_status"] == "RECORDED"
    assert report["finding_count"] == 0
    assert report["findings"] == []


def test_insufficient_evidence_status_is_preserved() -> None:
    report = apply_challenge_rules(
        make_record(
            category="MISSING_EVIDENCE",
            status="INSUFFICIENT_EVIDENCE",
        )
    )

    assert report["challenge_status"] == "REVIEW_REQUIRED"
    assert report["result_status"] == (
        "INSUFFICIENT_EVIDENCE"
    )


def test_blocked_status_is_terminal() -> None:
    report = apply_challenge_rules(
        make_record(status="BLOCKED")
    )

    assert report["challenge_status"] == "BLOCKED"
    assert report["result_status"] == "BLOCKED"
    assert report["finding_count"] == 0


def test_archived_status_is_terminal() -> None:
    report = apply_challenge_rules(
        make_record(status="ARCHIVED")
    )

    assert report["challenge_status"] == "ARCHIVED"
    assert report["result_status"] == "ARCHIVED"


def test_invalid_record_returns_errors() -> None:
    record = make_record()
    record["source_artifact_id"] = ""

    report = apply_challenge_rules(record)

    assert report["challenge_status"] == "INVALID"
    assert report["result_status"] == "INVALID"
    assert "source_artifact_id_invalid" in report["errors"]


def test_non_mapping_is_invalid() -> None:
    report = apply_challenge_rules([])

    assert report["challenge_status"] == "INVALID"
    assert report["errors"] == ["record_not_mapping"]


def test_rule_engine_preserves_original_conclusion() -> None:
    record = make_record()
    report = apply_challenge_rules(record)

    assert report["source_conclusion"] == (
        record["source_conclusion"]
    )
    assert report["original_conclusion_preserved"] is True
    assert report[
        "automatic_conclusion_replacement_allowed"
    ] is False
    assert report["findings"][0][
        "original_conclusion_preserved"
    ] is True


def test_rule_engine_sorts_registered_lists() -> None:
    record = make_record(
        evidence_references=[
            "evidence/z.json",
            "evidence/a.json",
        ],
        risk_flags=["RISK_Z", "RISK_A"],
    )

    finding = apply_challenge_rules(record)["findings"][0]

    assert finding["evidence_references"] == [
        "evidence/a.json",
        "evidence/z.json",
    ]
    assert finding["risk_flags"] == [
        "RISK_A",
        "RISK_Z",
    ]


def test_rule_engine_is_deterministic_and_non_mutating() -> None:
    record = make_record(
        category="CROSS_ARTIFACT_CONTRADICTION",
        severity="MEDIUM",
    )
    before = deepcopy(record)

    first = apply_challenge_rules(record)
    second = apply_challenge_rules(record)

    assert first == second
    assert record == before


def test_rule_engine_preserves_safety_boundary() -> None:
    report = apply_challenge_rules(make_record())

    assert report["paper_only"] is True
    assert report["local_only"] is True
    assert report["read_only"] is True
    assert report["sidecar_only"] is True
    assert report["deterministic_only"] is True
    assert report["registered_artifacts_only"] is True
    assert report["operator_review_required"] is True
    assert report["core_mutation_allowed"] is False
    assert report["source_artifact_mutation_allowed"] is False
    assert report["model_invocation_allowed"] is False
    assert report["prompt_execution_allowed"] is False
    assert report["orchestrator_execution_allowed"] is False
    assert report["automatic_truth_decision_allowed"] is False
    assert report["automatic_winner_selection_allowed"] is False
    assert report["automatic_model_switch_allowed"] is False
    assert report["automatic_prompt_switch_allowed"] is False
    assert report["operator_review_bypass_allowed"] is False
    assert report["trade_action_allowed"] is False
    assert report["real_execution_allowed"] is False