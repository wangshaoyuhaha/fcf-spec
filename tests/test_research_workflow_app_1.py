from copy import deepcopy

from apps.research_workflow_app_1.contract import get_research_workflow_contract, validate_research_workflow_contract
from apps.research_workflow_app_1.final_handoff import (
    COMPLETED_STAGES,
    build_research_workflow_final_handoff,
    validate_research_workflow_final_handoff,
)
from apps.research_workflow_app_1.source_loader import (
    build_research_workflow_source_manifest,
    validate_research_workflow_source_manifest,
)
from apps.research_workflow_app_1.workflow_model import build_research_workflow_review, validate_research_workflow_review
from apps.research_workflow_app_1.workflow_packet import build_research_workflow_packet, validate_research_workflow_packet
from apps.research_workflow_app_1.workflow_schema import create_research_workflow_step, validate_research_workflow_step


def _source_manifest():
    return build_research_workflow_source_manifest(root_path=".")


def test_research_workflow_contract_preserves_safety_boundary():
    contract = get_research_workflow_contract()
    validation = validate_research_workflow_contract(contract)

    assert validation["valid"] is True
    assert validation["issues"] == []

    flags = contract["boundary_flags"]
    assert flags["paper_only"] is True
    assert flags["operator_review_required"] is True
    assert flags["workflow_auto_approval_allowed"] is False
    assert flags["workflow_execution_allowed"] is False
    assert flags["trade_action_allowed"] is False
    assert flags["real_execution_allowed"] is False
    assert flags["future_return_prediction_allowed"] is False


def test_research_workflow_source_manifest_is_metadata_only():
    manifest = _source_manifest()
    validation = validate_research_workflow_source_manifest(manifest)

    assert validation["valid"] is True
    assert manifest["source_record_count"] == 15
    assert manifest["read_only"] is True
    assert manifest["content_loaded"] is False
    assert manifest["workflow_auto_approval_allowed"] is False
    assert manifest["workflow_execution_allowed"] is False
    assert manifest["trade_action_allowed"] is False


def test_research_workflow_step_is_review_only():
    step = create_research_workflow_step(
        workflow_step_id="workflow-step-001",
        source_app_id="RISK-EXPOSURE-APP-1",
        workflow_state="RISK_REVIEW",
        workflow_reason="review only",
        observed_status="PRESENT",
        created_at_utc="2026-07-06T00:00:00+00:00",
    )

    validation = validate_research_workflow_step(step)

    assert validation["valid"] is True
    assert step["operator_review_required"] is True
    assert step["workflow_auto_approval_allowed"] is False
    assert step["workflow_execution_allowed"] is False
    assert step["trade_action_allowed"] is False


def test_research_workflow_step_validator_rejects_execution_or_trade_mutation():
    step = create_research_workflow_step(
        workflow_step_id="workflow-step-002",
        source_app_id="DECISION-AUDIT-APP-1",
        workflow_state="DECISION_AUDIT_REVIEW",
        workflow_reason="review only",
        observed_status="PRESENT",
        created_at_utc="2026-07-06T00:00:00+00:00",
    )

    mutated = deepcopy(step)
    mutated["workflow_execution_allowed"] = True
    mutated["trade_action_allowed"] = True
    mutated["real_execution_allowed"] = True

    validation = validate_research_workflow_step(mutated)

    assert validation["valid"] is False
    assert "workflow_execution_allowed must be false" in validation["issues"]
    assert "trade_action_allowed must be false" in validation["issues"]
    assert "real_execution_allowed must be false" in validation["issues"]


def test_research_workflow_review_builds_full_source_workflow():
    review = build_research_workflow_review(source_manifest=_source_manifest())
    validation = validate_research_workflow_review(review)

    assert validation["valid"] is True
    assert review["workflow_step_count"] == 15
    assert review["invalid_workflow_step_count"] == 0
    assert review["operator_review_required"] is True
    assert review["workflow_auto_approval_allowed"] is False
    assert review["workflow_execution_allowed"] is False
    assert review["trade_action_allowed"] is False


def test_research_workflow_packet_is_archive_ready_and_not_actionable():
    packet = build_research_workflow_packet(
        packet_id="research-workflow-packet-001",
        source_manifest=_source_manifest(),
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    validation = validate_research_workflow_packet(packet)

    assert validation["valid"] is True
    assert packet["archive_ready"] is True
    assert packet["operator_review_required"] is True
    assert packet["workflow_auto_approval_allowed"] is False
    assert packet["workflow_execution_allowed"] is False
    assert packet["trade_action_allowed"] is False


def test_research_workflow_final_handoff_is_merge_review_only():
    packet = build_research_workflow_packet(
        packet_id="research-workflow-packet-002",
        source_manifest=_source_manifest(),
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    handoff = build_research_workflow_final_handoff(
        packet=packet,
        handoff_id="research-workflow-handoff-001",
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    validation = validate_research_workflow_final_handoff(handoff)

    assert validation["valid"] is True
    assert handoff["completed_stages"] == COMPLETED_STAGES
    assert handoff["branch_ready_for_merge_review"] is True
    assert handoff["tag_allowed"] is False
    assert handoff["release_allowed"] is False
    assert handoff["deploy_allowed"] is False


def test_research_workflow_final_handoff_rejects_release_execution_or_trade_mutation():
    packet = build_research_workflow_packet(
        packet_id="research-workflow-packet-003",
        source_manifest=_source_manifest(),
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    handoff = build_research_workflow_final_handoff(
        packet=packet,
        handoff_id="research-workflow-handoff-002",
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    mutated = deepcopy(handoff)
    mutated["workflow_execution_allowed"] = True
    mutated["real_execution_allowed"] = True
    mutated["release_allowed"] = True
    mutated["deploy_allowed"] = True

    validation = validate_research_workflow_final_handoff(mutated)

    assert validation["valid"] is False
    assert "workflow_execution_allowed must be false" in validation["issues"]
    assert "real_execution_allowed must be false" in validation["issues"]
    assert "release_allowed must be false" in validation["issues"]
    assert "deploy_allowed must be false" in validation["issues"]
