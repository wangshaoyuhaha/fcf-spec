from copy import deepcopy

from apps.dashboard_status_app_1.contract import get_dashboard_status_contract, validate_dashboard_status_contract
from apps.dashboard_status_app_1.final_handoff import (
    COMPLETED_STAGES,
    build_dashboard_status_final_handoff,
    validate_dashboard_status_final_handoff,
)
from apps.dashboard_status_app_1.source_loader import (
    build_dashboard_status_source_manifest,
    validate_dashboard_status_source_manifest,
)
from apps.dashboard_status_app_1.status_model import build_dashboard_status_review, validate_dashboard_status_review
from apps.dashboard_status_app_1.status_packet import build_dashboard_status_packet, validate_dashboard_status_packet
from apps.dashboard_status_app_1.status_schema import create_dashboard_status_item, validate_dashboard_status_item


def _source_manifest():
    return build_dashboard_status_source_manifest(root_path=".")


def test_dashboard_status_contract_preserves_no_execution_ui_boundary():
    contract = get_dashboard_status_contract()
    validation = validate_dashboard_status_contract(contract)

    assert validation["valid"] is True
    assert validation["issues"] == []

    flags = contract["boundary_flags"]
    assert flags["paper_only"] is True
    assert flags["operator_review_required"] is True
    assert flags["live_trading_dashboard_allowed"] is False
    assert flags["execution_ui_allowed"] is False
    assert flags["buy_button_enabled"] is False
    assert flags["sell_button_enabled"] is False
    assert flags["order_button_enabled"] is False
    assert flags["trade_action_allowed"] is False
    assert flags["real_execution_allowed"] is False


def test_dashboard_status_source_manifest_is_metadata_only():
    manifest = _source_manifest()
    validation = validate_dashboard_status_source_manifest(manifest)

    assert validation["valid"] is True
    assert manifest["source_record_count"] == 16
    assert manifest["read_only"] is True
    assert manifest["content_loaded"] is False
    assert manifest["live_trading_dashboard_allowed"] is False
    assert manifest["execution_ui_allowed"] is False
    assert manifest["buy_button_enabled"] is False
    assert manifest["trade_action_allowed"] is False


def test_dashboard_status_item_is_review_only():
    item = create_dashboard_status_item(
        status_item_id="dashboard-status-001",
        source_app_id="RESEARCH-WORKFLOW-APP-1",
        status_level="PRESENT",
        status_reason="summary only",
        observed_status="PRESENT",
        created_at_utc="2026-07-06T00:00:00+00:00",
    )

    validation = validate_dashboard_status_item(item)

    assert validation["valid"] is True
    assert item["operator_review_required"] is True
    assert item["execution_ui_allowed"] is False
    assert item["buy_button_enabled"] is False
    assert item["sell_button_enabled"] is False
    assert item["order_button_enabled"] is False


def test_dashboard_status_item_validator_rejects_execution_or_button_mutation():
    item = create_dashboard_status_item(
        status_item_id="dashboard-status-002",
        source_app_id="RISK-EXPOSURE-APP-1",
        status_level="PRESENT",
        status_reason="summary only",
        observed_status="PRESENT",
        created_at_utc="2026-07-06T00:00:00+00:00",
    )

    mutated = deepcopy(item)
    mutated["execution_ui_allowed"] = True
    mutated["buy_button_enabled"] = True
    mutated["order_button_enabled"] = True

    validation = validate_dashboard_status_item(mutated)

    assert validation["valid"] is False
    assert "execution_ui_allowed must be false" in validation["issues"]
    assert "buy_button_enabled must be false" in validation["issues"]
    assert "order_button_enabled must be false" in validation["issues"]


def test_dashboard_status_review_builds_full_source_status_summary():
    review = build_dashboard_status_review(source_manifest=_source_manifest())
    validation = validate_dashboard_status_review(review)

    assert validation["valid"] is True
    assert review["status_item_count"] == 16
    assert review["invalid_status_item_count"] == 0
    assert review["operator_review_required"] is True
    assert review["execution_ui_allowed"] is False
    assert review["trade_action_allowed"] is False
    assert review["real_execution_allowed"] is False


def test_dashboard_status_packet_is_archive_ready_and_not_actionable():
    packet = build_dashboard_status_packet(
        packet_id="dashboard-status-packet-001",
        source_manifest=_source_manifest(),
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    validation = validate_dashboard_status_packet(packet)

    assert validation["valid"] is True
    assert packet["archive_ready"] is True
    assert packet["operator_review_required"] is True
    assert packet["execution_ui_allowed"] is False
    assert packet["buy_button_enabled"] is False
    assert packet["trade_action_allowed"] is False


def test_dashboard_status_final_handoff_is_completion_review_only():
    packet = build_dashboard_status_packet(
        packet_id="dashboard-status-packet-002",
        source_manifest=_source_manifest(),
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    handoff = build_dashboard_status_final_handoff(
        packet=packet,
        handoff_id="dashboard-status-handoff-001",
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    validation = validate_dashboard_status_final_handoff(handoff)

    assert validation["valid"] is True
    assert handoff["completed_stages"] == COMPLETED_STAGES
    assert handoff["branch_ready_for_merge_review"] is True
    assert handoff["tag_allowed"] is False
    assert handoff["release_allowed"] is False
    assert handoff["deploy_allowed"] is False


def test_dashboard_status_final_handoff_rejects_release_execution_or_button_mutation():
    packet = build_dashboard_status_packet(
        packet_id="dashboard-status-packet-003",
        source_manifest=_source_manifest(),
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    handoff = build_dashboard_status_final_handoff(
        packet=packet,
        handoff_id="dashboard-status-handoff-002",
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    mutated = deepcopy(handoff)
    mutated["execution_ui_allowed"] = True
    mutated["buy_button_enabled"] = True
    mutated["release_allowed"] = True
    mutated["deploy_allowed"] = True

    validation = validate_dashboard_status_final_handoff(mutated)

    assert validation["valid"] is False
    assert "execution_ui_allowed must be false" in validation["issues"]
    assert "buy_button_enabled must be false" in validation["issues"]
    assert "release_allowed must be false" in validation["issues"]
    assert "deploy_allowed must be false" in validation["issues"]
