from copy import deepcopy

from apps.decision_audit_app_1.contract import get_decision_audit_contract, validate_decision_audit_contract
from apps.decision_audit_app_1.audit_schema import create_decision_audit_event, validate_decision_audit_event
from apps.decision_audit_app_1.audit_model import build_decision_audit_review, validate_decision_audit_review
from apps.decision_audit_app_1.audit_packet import build_decision_audit_packet, validate_decision_audit_packet
from apps.decision_audit_app_1.final_handoff import (
    COMPLETED_STAGES,
    build_decision_audit_final_handoff,
    validate_decision_audit_final_handoff,
)
from apps.decision_audit_app_1.source_loader import (
    build_decision_audit_source_manifest,
    validate_decision_audit_source_manifest,
)


def _source_manifest():
    return build_decision_audit_source_manifest(root_path=".")


def _candidates():
    return [
        {
            "candidate_id": "candidate-001",
            "symbol": "BTCUSDT",
            "source_app_id": "RISK-EXPOSURE-APP-1",
            "audit_event_type": "RISK_REVIEWED",
            "observed_status": "REVIEW_REQUIRED",
        },
        {
            "candidate_id": "candidate-002",
            "symbol": "AAPL",
            "source_app_id": "PORTFOLIO-REVIEW-APP-1",
            "audit_event_type": "PORTFOLIO_REVIEWED",
            "observed_status": "PAPER_REVIEW_ONLY",
        },
    ]


def test_decision_audit_contract_preserves_safety_boundary():
    contract = get_decision_audit_contract()
    validation = validate_decision_audit_contract(contract)

    assert validation["valid"] is True
    assert validation["issues"] == []

    flags = contract["boundary_flags"]
    assert flags["paper_only"] is True
    assert flags["operator_review_required"] is True
    assert flags["decision_auto_approval_allowed"] is False
    assert flags["decision_override_allowed"] is False
    assert flags["trade_action_allowed"] is False
    assert flags["real_execution_allowed"] is False
    assert flags["future_return_prediction_allowed"] is False


def test_decision_audit_source_manifest_is_metadata_only():
    manifest = _source_manifest()
    validation = validate_decision_audit_source_manifest(manifest)

    assert validation["valid"] is True
    assert manifest["source_record_count"] == 14
    assert manifest["read_only"] is True
    assert manifest["content_loaded"] is False
    assert manifest["decision_auto_approval_allowed"] is False
    assert manifest["trade_action_allowed"] is False
    assert manifest["real_execution_allowed"] is False


def test_decision_audit_event_is_review_only():
    event = create_decision_audit_event(
        audit_event_id="audit-001",
        candidate_id="candidate-001",
        symbol="BTCUSDT",
        audit_event_type="RISK_REVIEWED",
        source_app_id="RISK-EXPOSURE-APP-1",
        audit_reason="review only",
        observed_status="REVIEW_REQUIRED",
        created_at_utc="2026-07-06T00:00:00+00:00",
    )

    validation = validate_decision_audit_event(event)

    assert validation["valid"] is True
    assert event["operator_review_required"] is True
    assert event["decision_auto_approval_allowed"] is False
    assert event["decision_override_allowed"] is False
    assert event["trade_action_allowed"] is False
    assert event["order_ticket_allowed"] is False


def test_decision_audit_event_validator_rejects_auto_approval_or_execution():
    event = create_decision_audit_event(
        audit_event_id="audit-002",
        candidate_id="candidate-002",
        symbol="AAPL",
        audit_event_type="PORTFOLIO_REVIEWED",
        source_app_id="PORTFOLIO-REVIEW-APP-1",
        audit_reason="review only",
        observed_status="PAPER_REVIEW_ONLY",
        created_at_utc="2026-07-06T00:00:00+00:00",
    )

    mutated = deepcopy(event)
    mutated["decision_auto_approval_allowed"] = True
    mutated["real_execution_allowed"] = True

    validation = validate_decision_audit_event(mutated)

    assert validation["valid"] is False
    assert "decision_auto_approval_allowed must be false" in validation["issues"]
    assert "real_execution_allowed must be false" in validation["issues"]


def test_decision_audit_review_builds_valid_audit_trail():
    review = build_decision_audit_review(candidates=_candidates(), source_manifest=_source_manifest())
    validation = validate_decision_audit_review(review)

    assert validation["valid"] is True
    assert review["candidate_count"] == 2
    assert review["audit_event_count"] == 2
    assert review["invalid_audit_event_count"] == 0
    assert review["operator_review_required"] is True
    assert review["decision_auto_approval_allowed"] is False
    assert review["trade_action_allowed"] is False


def test_decision_audit_packet_is_archive_ready_and_not_actionable():
    packet = build_decision_audit_packet(
        packet_id="decision-audit-packet-001",
        candidates=_candidates(),
        source_manifest=_source_manifest(),
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    validation = validate_decision_audit_packet(packet)

    assert validation["valid"] is True
    assert packet["archive_ready"] is True
    assert packet["operator_review_required"] is True
    assert packet["decision_auto_approval_allowed"] is False
    assert packet["trade_action_allowed"] is False
    assert packet["real_execution_allowed"] is False


def test_decision_audit_final_handoff_is_merge_review_only():
    packet = build_decision_audit_packet(
        packet_id="decision-audit-packet-002",
        candidates=_candidates(),
        source_manifest=_source_manifest(),
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    handoff = build_decision_audit_final_handoff(
        packet=packet,
        handoff_id="decision-audit-handoff-001",
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    validation = validate_decision_audit_final_handoff(handoff)

    assert validation["valid"] is True
    assert handoff["completed_stages"] == COMPLETED_STAGES
    assert handoff["branch_ready_for_merge_review"] is True
    assert handoff["tag_allowed"] is False
    assert handoff["release_allowed"] is False
    assert handoff["deploy_allowed"] is False


def test_decision_audit_final_handoff_rejects_release_or_execution_mutation():
    packet = build_decision_audit_packet(
        packet_id="decision-audit-packet-003",
        candidates=_candidates(),
        source_manifest=_source_manifest(),
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    handoff = build_decision_audit_final_handoff(
        packet=packet,
        handoff_id="decision-audit-handoff-002",
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    mutated = deepcopy(handoff)
    mutated["decision_auto_approval_allowed"] = True
    mutated["real_execution_allowed"] = True
    mutated["release_allowed"] = True
    mutated["deploy_allowed"] = True

    validation = validate_decision_audit_final_handoff(mutated)

    assert validation["valid"] is False
    assert "decision_auto_approval_allowed must be false" in validation["issues"]
    assert "real_execution_allowed must be false" in validation["issues"]
    assert "release_allowed must be false" in validation["issues"]
    assert "deploy_allowed must be false" in validation["issues"]
