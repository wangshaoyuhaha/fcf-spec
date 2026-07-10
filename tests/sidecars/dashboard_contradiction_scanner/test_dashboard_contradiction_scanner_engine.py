"""Tests for the dashboard contradiction scanner engine."""

from copy import deepcopy

from fcf.sidecars.dashboard_contradiction_scanner import (
    scan_dashboard_contradictions,
)


def _source(
    *,
    artifact_id: str,
    artifact_type: str,
    risk_flags: list[str],
    source_artifact_ids: list[str],
    validation_state: str = "PASS",
    review_state: str = "REVIEW_REQUIRED",
    lifecycle_state: str = "ACTIVE",
    archive_state: str = "PENDING",
    validation_baseline_id: str = "baseline-001",
    risk_flag_levels: dict[str, str] | None = None,
    summary_state: str | None = None,
    raw_state: str | None = None,
) -> dict[str, object]:
    record: dict[str, object] = {
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "correlation_id": "corr-001",
        "research_run_id": "run-001",
        "validation_baseline_id": validation_baseline_id,
        "source_artifact_ids": source_artifact_ids,
        "risk_flags": risk_flags,
        "reason_codes": ["REASON-001"],
        "validation_state": validation_state,
        "review_state": review_state,
        "lifecycle_state": lifecycle_state,
        "archive_state": archive_state,
        "summary": "Paper-only governed summary.",
    }

    if risk_flag_levels is not None:
        record["risk_flag_levels"] = risk_flag_levels

    if summary_state is not None:
        record["summary_state"] = summary_state

    if raw_state is not None:
        record["raw_state"] = raw_state

    return record


def _dashboard(**overrides: object) -> dict[str, object]:
    values: dict[str, object] = {
        "artifact_id": "dashboard-001",
        "artifact_type": "DASHBOARD_STATUS_PACKET",
        "risk_flags": ["HIGH_VOLATILITY"],
        "source_artifact_ids": ["governance-001"],
        "risk_flag_levels": {"HIGH_VOLATILITY": "HIGH"},
        "summary_state": "REVIEW_REQUIRED",
    }
    values.update(overrides)
    return _source(**values)


def _reference(**overrides: object) -> dict[str, object]:
    values: dict[str, object] = {
        "artifact_id": "governance-001",
        "artifact_type": "MODEL_GOVERNANCE_PACKET",
        "risk_flags": ["HIGH_VOLATILITY"],
        "source_artifact_ids": ["source-001"],
        "risk_flag_levels": {"HIGH_VOLATILITY": "HIGH"},
        "raw_state": "REVIEW_REQUIRED",
    }
    values.update(overrides)
    return _source(**values)


def _classes(report: dict[str, object]) -> set[str]:
    findings = report["findings"]
    assert isinstance(findings, list)
    return {
        str(finding["contradiction_class"])
        for finding in findings
    }


def test_consistent_sources_have_no_contradictions() -> None:
    report = scan_dashboard_contradictions(
        [_dashboard(), _reference()]
    )

    assert report["scan_status"] == "NO_CONTRADICTIONS"
    assert report["finding_count"] == 0
    assert report["findings"] == []


def test_missing_risk_flag_is_detected() -> None:
    report = scan_dashboard_contradictions(
        [
            _dashboard(risk_flags=[]),
            _reference(),
        ]
    )

    assert "RISK_FLAG_MISSING" in _classes(report)


def test_risk_flag_downgrade_is_detected() -> None:
    report = scan_dashboard_contradictions(
        [
            _dashboard(
                risk_flag_levels={"HIGH_VOLATILITY": "LOW"}
            ),
            _reference(
                risk_flag_levels={"HIGH_VOLATILITY": "CRITICAL"}
            ),
        ]
    )

    assert "RISK_FLAG_DOWNGRADED" in _classes(report)


def test_summary_raw_conflict_is_detected() -> None:
    report = scan_dashboard_contradictions(
        [
            _dashboard(summary_state="CLEAR"),
            _reference(raw_state="REVIEW_REQUIRED"),
        ]
    )

    assert "SUMMARY_RAW_CONFLICT" in _classes(report)


def test_governance_state_mismatches_are_detected() -> None:
    report = scan_dashboard_contradictions(
        [
            _dashboard(
                validation_state="PASS",
                review_state="APPROVED",
                lifecycle_state="ARCHIVED",
                archive_state="COMPLETE",
            ),
            _reference(
                validation_state="FAIL",
                review_state="REVIEW_REQUIRED",
                lifecycle_state="ACTIVE",
                archive_state="PENDING",
            ),
        ]
    )

    classes = _classes(report)

    assert "VALIDATION_STATE_MISMATCH" in classes
    assert "REVIEW_STATE_MISMATCH" in classes
    assert "LIFECYCLE_STATE_MISMATCH" in classes
    assert "ARCHIVE_STATE_MISMATCH" in classes


def test_source_lineage_mismatch_is_detected() -> None:
    report = scan_dashboard_contradictions(
        [
            _dashboard(source_artifact_ids=["other-source"]),
            _reference(),
        ]
    )

    assert "SOURCE_LINEAGE_MISMATCH" in _classes(report)


def test_scanner_does_not_mutate_sources() -> None:
    sources = [_dashboard(), _reference()]
    before = deepcopy(sources)

    scan_dashboard_contradictions(sources)

    assert sources == before


def test_scan_output_is_safety_locked() -> None:
    report = scan_dashboard_contradictions(
        [_dashboard(), _reference()]
    )

    assert report["human_review_required"] is True
    assert report["archive_required"] is True
    assert report["execution_allowed"] is False
    assert report["source_mutation_allowed"] is False
    assert report["risk_flag_deletion_allowed"] is False
    assert report["risk_flag_downgrade_allowed"] is False
    assert len(str(report["scan_report_hash"])) == 64
