"""Tests for dashboard contradiction scanner final handoff."""

from copy import deepcopy

import pytest

from fcf.sidecars.dashboard_contradiction_scanner import (
    build_contradiction_review_packet,
    build_final_handoff,
    scan_dashboard_contradictions,
    validate_final_handoff,
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
        "summary": "Paper-only governed summary.",
    }


def _packet(
    *,
    contradiction: bool = True,
) -> dict[str, object]:
    dashboard_flags = [] if contradiction else ["HIGH_VOLATILITY"]

    dashboard = _record(
        artifact_id="dashboard-001",
        artifact_type="DASHBOARD_STATUS_PACKET",
        risk_flags=dashboard_flags,
        source_artifact_ids=["governance-001"],
    )
    reference = _record(
        artifact_id="governance-001",
        artifact_type="MODEL_GOVERNANCE_PACKET",
        risk_flags=["HIGH_VOLATILITY"],
        source_artifact_ids=["source-001"],
    )

    report = scan_dashboard_contradictions(
        [dashboard, reference]
    )
    return build_contradiction_review_packet(report)


def test_build_final_handoff_is_valid() -> None:
    handoff = build_final_handoff(_packet())

    assert validate_final_handoff(handoff) == []
    assert handoff["handoff_id"].startswith(
        "contradiction-handoff-"
    )
    assert handoff["handoff_status"] == (
        "WAITING_FOR_OPERATOR_REVIEW"
    )
    assert len(str(handoff["handoff_hash"])) == 64


def test_handoff_preserves_review_packet() -> None:
    packet = _packet()
    handoff = build_final_handoff(packet)

    assert handoff["review_packet_snapshot"] == packet
    assert handoff["source_packet_id"] == packet["packet_id"]
    assert handoff["source_packet_hash"] == packet[
        "packet_hash"
    ]


def test_handoff_does_not_mutate_packet() -> None:
    packet = _packet()
    before = deepcopy(packet)

    build_final_handoff(packet)

    assert packet == before


def test_handoff_identifier_is_deterministic() -> None:
    first = build_final_handoff(_packet())
    second = build_final_handoff(_packet())

    assert first["handoff_id"] == second["handoff_id"]
    assert first["handoff_hash"] == second["handoff_hash"]


def test_handoff_is_safety_locked() -> None:
    handoff = build_final_handoff(_packet())

    assert handoff["human_review_required"] is True
    assert handoff["operator_review_bypass_allowed"] is False
    assert handoff["automatic_resolution_allowed"] is False
    assert handoff["archive_required"] is True
    assert handoff["execution_allowed"] is False
    assert handoff["source_mutation_allowed"] is False
    assert handoff["risk_flag_deletion_allowed"] is False
    assert handoff["risk_flag_downgrade_allowed"] is False
    assert handoff["core_mutation_allowed"] is False
    assert handoff["p48_core_expansion_allowed"] is False
    assert handoff["real_trading_allowed"] is False
    assert handoff["real_execution_allowed"] is False


def test_no_contradiction_still_requires_review() -> None:
    handoff = build_final_handoff(
        _packet(contradiction=False)
    )

    assert handoff["finding_count"] == 0
    assert handoff["human_review_required"] is True
    assert handoff["handoff_status"] == (
        "WAITING_FOR_OPERATOR_REVIEW"
    )


def test_invalid_review_packet_is_rejected() -> None:
    packet = _packet()
    packet["operator_review_bypass_allowed"] = True

    with pytest.raises(
        ValueError,
        match="invalid_review_packet",
    ):
        build_final_handoff(packet)


def test_review_bypass_is_detected() -> None:
    handoff = build_final_handoff(_packet())
    handoff["operator_review_bypass_allowed"] = True

    assert "operator_review_bypass_not_blocked" in (
        validate_final_handoff(handoff)
    )


def test_forbidden_action_field_is_detected() -> None:
    handoff = build_final_handoff(_packet())
    handoff["order"] = True

    assert "forbidden_action_field:order" in (
        validate_final_handoff(handoff)
    )
