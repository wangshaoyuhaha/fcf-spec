from copy import deepcopy

from apps.final_completion_review_app_1.contract import (
    get_final_completion_contract,
    validate_final_completion_contract,
)
from apps.final_completion_review_app_1.source_loader import (
    build_final_completion_source_manifest,
    validate_final_completion_source_manifest,
)
from apps.final_completion_review_app_1.completion_schema import (
    create_completion_review_item,
    validate_completion_review_item,
)
from apps.final_completion_review_app_1.completion_model import (
    build_final_completion_review,
    validate_final_completion_review,
)
from apps.final_completion_review_app_1.completion_packet import (
    build_final_completion_packet,
    validate_final_completion_packet,
)
from apps.final_completion_review_app_1.final_handoff import (
    COMPLETED_STAGES,
    build_final_completion_handoff,
    validate_final_completion_handoff,
)


def _source_manifest():
    return build_final_completion_source_manifest(root_path=".")


def test_final_completion_contract_preserves_safety_boundary():
    contract = get_final_completion_contract()
    validation = validate_final_completion_contract(contract)

    assert validation["valid"] is True
    assert validation["issues"] == []

    flags = contract["boundary_flags"]
    assert flags["paper_only"] is True
    assert flags["operator_review_required"] is True
    assert flags["auto_completion_approval_allowed"] is False
    assert flags["workflow_execution_allowed"] is False
    assert flags["trade_action_allowed"] is False
    assert flags["real_execution_allowed"] is False
    assert flags["tag_allowed"] is False
    assert flags["release_allowed"] is False
    assert flags["deploy_allowed"] is False


def test_final_completion_source_manifest_is_metadata_only():
    manifest = _source_manifest()
    validation = validate_final_completion_source_manifest(manifest)

    assert validation["valid"] is True
    assert manifest["source_record_count"] == 17
    assert manifest["read_only"] is True
    assert manifest["content_loaded"] is False
    assert manifest["auto_completion_approval_allowed"] is False
    assert manifest["trade_action_allowed"] is False
    assert manifest["release_allowed"] is False
    assert manifest["deploy_allowed"] is False


def test_completion_review_item_is_review_only():
    item = create_completion_review_item(
        completion_item_id="completion-review-001",
        source_app_id="DASHBOARD-STATUS-APP-1",
        completion_state="COMPLETED_PRESENT",
        completion_reason="review only",
        observed_status="PRESENT",
        created_at_utc="2026-07-06T00:00:00+00:00",
    )

    validation = validate_completion_review_item(item)

    assert validation["valid"] is True
    assert item["operator_review_required"] is True
    assert item["auto_completion_approval_allowed"] is False
    assert item["workflow_execution_allowed"] is False
    assert item["release_allowed"] is False
    assert item["deploy_allowed"] is False


def test_completion_review_item_rejects_release_or_execution_mutation():
    item = create_completion_review_item(
        completion_item_id="completion-review-002",
        source_app_id="RESEARCH-WORKFLOW-APP-1",
        completion_state="COMPLETED_PRESENT",
        completion_reason="review only",
        observed_status="PRESENT",
        created_at_utc="2026-07-06T00:00:00+00:00",
    )

    mutated = deepcopy(item)
    mutated["auto_completion_approval_allowed"] = True
    mutated["workflow_execution_allowed"] = True
    mutated["release_allowed"] = True
    mutated["deploy_allowed"] = True

    validation = validate_completion_review_item(mutated)

    assert validation["valid"] is False
    assert "auto_completion_approval_allowed must be false" in validation["issues"]
    assert "workflow_execution_allowed must be false" in validation["issues"]
    assert "release_allowed must be false" in validation["issues"]
    assert "deploy_allowed must be false" in validation["issues"]


def test_final_completion_review_builds_all_sidecar_items():
    review = build_final_completion_review(source_manifest=_source_manifest())
    validation = validate_final_completion_review(review)

    assert validation["valid"] is True
    assert review["completion_item_count"] == 17
    assert review["invalid_completion_item_count"] == 0
    assert review["operator_review_required"] is True
    assert review["auto_completion_approval_allowed"] is False
    assert review["trade_action_allowed"] is False
    assert review["release_allowed"] is False
    assert review["deploy_allowed"] is False


def test_final_completion_packet_is_archive_ready_and_not_release_action():
    packet = build_final_completion_packet(
        packet_id="final-completion-packet-001",
        source_manifest=_source_manifest(),
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    validation = validate_final_completion_packet(packet)

    assert validation["valid"] is True
    assert packet["archive_ready"] is True
    assert packet["operator_review_required"] is True
    assert packet["auto_completion_approval_allowed"] is False
    assert packet["trade_action_allowed"] is False
    assert packet["release_allowed"] is False
    assert packet["deploy_allowed"] is False


def test_final_completion_handoff_is_merge_review_only():
    packet = build_final_completion_packet(
        packet_id="final-completion-packet-002",
        source_manifest=_source_manifest(),
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    handoff = build_final_completion_handoff(
        packet=packet,
        handoff_id="final-completion-handoff-001",
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    validation = validate_final_completion_handoff(handoff)

    assert validation["valid"] is True
    assert handoff["completed_stages"] == COMPLETED_STAGES
    assert handoff["branch_ready_for_merge_review"] is True
    assert handoff["tag_allowed"] is False
    assert handoff["release_allowed"] is False
    assert handoff["deploy_allowed"] is False


def test_final_completion_handoff_rejects_release_deploy_or_execution_mutation():
    packet = build_final_completion_packet(
        packet_id="final-completion-packet-003",
        source_manifest=_source_manifest(),
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    handoff = build_final_completion_handoff(
        packet=packet,
        handoff_id="final-completion-handoff-002",
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    mutated = deepcopy(handoff)
    mutated["workflow_execution_allowed"] = True
    mutated["real_execution_allowed"] = True
    mutated["release_allowed"] = True
    mutated["deploy_allowed"] = True

    validation = validate_final_completion_handoff(mutated)

    assert validation["valid"] is False
    assert "workflow_execution_allowed must be false" in validation["issues"]
    assert "real_execution_allowed must be false" in validation["issues"]
    assert "release_allowed must be false" in validation["issues"]
    assert "deploy_allowed must be false" in validation["issues"]
