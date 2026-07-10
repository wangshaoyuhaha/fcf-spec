"""Tests for contradiction review packet generation."""

from copy import deepcopy

import pytest

from fcf.sidecars.dashboard_contradiction_scanner import (
    build_contradiction_review_packet,
    scan_dashboard_contradictions,
    validate_contradiction_review_packet,
)


def _record(
    *,
    artifact_id: str,
    artifact_type: str,
    risk_flags: list[str],
    source_artifact_ids: list[str],
) -> dict[str, object]:
    return {
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "correlation_id": "corr-001",
        "research_run_id": "run-001",
        "validation_baseline_id": "baseline-001",
        "source_artifact_ids": source_artifact_ids,
        "risk_flags": risk_flags,
        "reason_codes": ["REASON-001"],
        "validation_state": "PASS",
        "review_state": "REVIEW_REQUIRED",
        "lifecycle_state": "ACTIVE",
        "archive_state": "PENDING",
        "summary": "Paper-only summary.",
    }


def _scan_report() -> dict[str, object]:
    dashboard = _record(
        artifact_id="dashboard-001",
        artifact_type="DASHBOARD_STATUS_PACKET",
        risk_flags=[],
        source_artifact_ids=["governance-001"],
    )
    reference = _record(
        artifact_id="governance-001",
        artifact_type="MODEL_GOVERNANCE_PACKET",
        risk_flags=["HIGH_VOLATILITY"],
        source_artifact_ids=["source-001"],
    )
    return scan_dashboard_contradictions(
        [dashboard, reference]
    )


def test_build_review_packet_is_valid() -> None:
    packet = build_contradiction_review_packet(_scan_report())

    assert validate_contradiction_review_packet(packet) == []
    assert packet["packet_id"].startswith(
        "contradiction-packet-"
    )
    assert packet["packet_status"] == "REVIEW_REQUIRED"
    assert packet["finding_count"] >= 1
    assert len(packet["packet_hash"]) == 64


def test_packet_preserves_findings() -> None:
    report = _scan_report()
    packet = build_contradiction_review_packet(report)

    assert packet["findings"] == report["findings"]
    assert packet["source_scan_report_id"] == report[
        "scan_report_id"
    ]
    assert packet["source_scan_report_hash"] == report[
        "scan_report_hash"
    ]


def test_packet_does_not_mutate_scan_report() -> None:
    report = _scan_report()
    before = deepcopy(report)

    build_contradiction_review_packet(report)

    assert report == before


def test_packet_contains_governance_summaries() -> None:
    packet = build_contradiction_review_packet(_scan_report())

    assert packet["severity_summary"]["HIGH"] >= 1
    assert packet["contradiction_class_summary"][
        "RISK_FLAG_MISSING"
    ] == 1
    assert len(packet["open_finding_ids"]) >= 1


def test_packet_is_safety_locked() -> None:
    packet = build_contradiction_review_packet(_scan_report())

    assert packet["human_review_required"] is True
    assert packet["operator_review_bypass_allowed"] is False
    assert packet["automatic_resolution_allowed"] is False
    assert packet["archive_required"] is True
    assert packet["execution_allowed"] is False
    assert packet["source_mutation_allowed"] is False
    assert packet["risk_flag_deletion_allowed"] is False
    assert packet["risk_flag_downgrade_allowed"] is False


def test_packet_identifier_is_deterministic() -> None:
    first = build_contradiction_review_packet(_scan_report())
    second = build_contradiction_review_packet(_scan_report())

    assert first["packet_id"] == second["packet_id"]
    assert first["packet_hash"] == second["packet_hash"]


def test_invalid_packet_status_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="unsupported_packet_status",
    ):
        build_contradiction_review_packet(
            _scan_report(),
            packet_status="AUTO_RESOLVED",
        )


def test_finding_count_mismatch_is_rejected() -> None:
    report = _scan_report()
    report["finding_count"] = 999

    with pytest.raises(
        ValueError,
        match="finding_count_mismatch",
    ):
        build_contradiction_review_packet(report)


def test_review_bypass_is_detected() -> None:
    packet = build_contradiction_review_packet(_scan_report())
    packet["operator_review_bypass_allowed"] = True

    assert "operator_review_bypass_not_blocked" in (
        validate_contradiction_review_packet(packet)
    )
