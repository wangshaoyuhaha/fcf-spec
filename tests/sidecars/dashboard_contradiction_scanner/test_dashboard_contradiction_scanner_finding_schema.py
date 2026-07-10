"""Tests for dashboard contradiction finding schema."""

import pytest

from fcf.sidecars.dashboard_contradiction_scanner import (
    build_contradiction_finding,
    validate_contradiction_finding,
)


def _finding() -> dict[str, object]:
    return build_contradiction_finding(
        contradiction_class="RISK_FLAG_MISSING",
        severity="HIGH",
        correlation_id="corr-001",
        research_run_id="run-001",
        validation_baseline_id="baseline-001",
        source_artifact_ids=[
            "dashboard-001",
            "governance-001",
        ],
        evidence={
            "expected_risk_flag": "HIGH_VOLATILITY",
            "dashboard_risk_flags": [],
        },
        summary="Dashboard omitted a governed risk flag.",
    )


def test_build_finding_is_valid() -> None:
    finding = _finding()

    assert validate_contradiction_finding(finding) == []
    assert finding["finding_id"].startswith("contradiction-")
    assert finding["contradiction_class"] == "RISK_FLAG_MISSING"
    assert finding["severity"] == "HIGH"
    assert finding["status"] == "OPEN"
    assert len(finding["finding_hash"]) == 64


def test_finding_requires_review_and_archive() -> None:
    finding = _finding()

    assert finding["human_review_required"] is True
    assert finding["archive_required"] is True
    assert finding["execution_allowed"] is False


def test_finding_preserves_traceability() -> None:
    finding = _finding()

    assert finding["correlation_id"] == "corr-001"
    assert finding["research_run_id"] == "run-001"
    assert finding["validation_baseline_id"] == "baseline-001"
    assert finding["source_artifact_ids"] == [
        "dashboard-001",
        "governance-001",
    ]


def test_finding_identifier_is_deterministic() -> None:
    first = _finding()
    second = _finding()

    assert first["finding_id"] == second["finding_id"]
    assert first["finding_hash"] == second["finding_hash"]


def test_unsupported_contradiction_class_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="unsupported_contradiction_class",
    ):
        build_contradiction_finding(
            contradiction_class="TRADE_SIGNAL",
            severity="HIGH",
            correlation_id="corr-001",
            research_run_id="run-001",
            validation_baseline_id="baseline-001",
            source_artifact_ids=["artifact-001"],
            evidence={"state": "invalid"},
            summary="Invalid class.",
        )


def test_invalid_severity_is_rejected() -> None:
    with pytest.raises(ValueError, match="unsupported_severity"):
        build_contradiction_finding(
            contradiction_class="SUMMARY_RAW_CONFLICT",
            severity="EXTREME",
            correlation_id="corr-001",
            research_run_id="run-001",
            validation_baseline_id="baseline-001",
            source_artifact_ids=["artifact-001"],
            evidence={"state": "invalid"},
            summary="Invalid severity.",
        )


def test_empty_evidence_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="missing_or_invalid_evidence",
    ):
        build_contradiction_finding(
            contradiction_class="SUMMARY_RAW_CONFLICT",
            severity="MEDIUM",
            correlation_id="corr-001",
            research_run_id="run-001",
            validation_baseline_id="baseline-001",
            source_artifact_ids=["artifact-001"],
            evidence={},
            summary="Missing evidence.",
        )


def test_forbidden_action_field_is_detected() -> None:
    finding = _finding()
    finding["order"] = True

    assert "forbidden_action_field:order" in (
        validate_contradiction_finding(finding)
    )


def test_risk_flag_downgrade_cannot_be_enabled() -> None:
    finding = _finding()
    finding["risk_flag_downgrade_allowed"] = True

    assert "risk_flag_downgrade_not_blocked" in (
        validate_contradiction_finding(finding)
    )
