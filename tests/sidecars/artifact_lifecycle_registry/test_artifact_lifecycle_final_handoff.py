import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fcf.sidecars.artifact_lifecycle_registry import (
    build_artifact_state_snapshot_index,
    build_lifecycle_final_handoff,
    build_lifecycle_registry_packet,
    build_lifecycle_registry_summary,
    build_transition_index,
    classify_lifecycle_final_handoff,
)


def _record(status="REGISTERED", artifact_id="artifact-1"):
    return {
        "artifact_id": artifact_id,
        "artifact_type": "archive_packet",
        "artifact_path": f"runtime/archive/{artifact_id}.json",
        "lifecycle_status": status,
    }


def _transition():
    return {
        "artifact_id": "artifact-1",
        "from_status": "REGISTERED",
        "to_status": "OBSERVED",
        "reason_code": "SOURCE_OBSERVED",
    }


def _packet(status="REGISTERED"):
    snapshot_index = build_artifact_state_snapshot_index(
        [_record(status=status)]
    )
    transition_index = build_transition_index((_transition(),))
    summary = build_lifecycle_registry_summary(
        snapshot_index=snapshot_index,
        transition_index=transition_index,
    )
    return build_lifecycle_registry_packet(registry_summary=summary)


def test_final_handoff_observed_goes_to_operator_review_only():
    handoff = build_lifecycle_final_handoff(
        registry_packet=_packet(status="REGISTERED")
    )
    result = classify_lifecycle_final_handoff(handoff)

    assert handoff["stage"] == "D6"
    assert handoff["handoff_type"] == "artifact_lifecycle_registry_final_handoff"
    assert handoff["registry_handoff_status"] == "OBSERVED"
    assert handoff["final_gate"] == "OPERATOR_REVIEW_REQUIRED"
    assert handoff["operator_review_required"] is True
    assert handoff["auto_pass_allowed"] is False
    assert result["final_action"] == "HANDOFF_TO_OPERATOR_REVIEW"
    assert result["auto_pass_allowed"] is False


def test_final_handoff_preserves_read_only_boundaries():
    handoff = build_lifecycle_final_handoff(
        registry_packet=_packet(status="REGISTERED")
    )

    assert handoff["paper_only"] is True
    assert handoff["local_only"] is True
    assert handoff["read_only"] is True
    assert handoff["sidecar_only"] is True
    assert handoff["index_only"] is True
    assert handoff["handoff_only"] is True
    assert handoff["source_artifact_mutation_allowed"] is False
    assert handoff["artifact_status_auto_repair_allowed"] is False
    assert handoff["transition_applied"] is False
    assert handoff["evidence_backfill_allowed"] is False
    assert handoff["correlation_id_auto_fill_allowed"] is False
    assert handoff["placeholder_review_allowed"] is False
    assert handoff["ui_dashboard_panel_allowed"] is False
    assert handoff["core_mutation_allowed"] is False
    assert handoff["p48_core_expansion_allowed"] is False


def test_final_handoff_forbids_release_execution_and_credentials():
    handoff = build_lifecycle_final_handoff(
        registry_packet=_packet(status="REGISTERED")
    )

    assert handoff["tag_allowed"] is False
    assert handoff["release_allowed"] is False
    assert handoff["deploy_allowed"] is False
    assert handoff["real_trade_allowed"] is False
    assert handoff["real_execution_allowed"] is False
    assert handoff["broker_connection_allowed"] is False
    assert handoff["exchange_connection_allowed"] is False
    assert handoff["api_key_allowed"] is False
    assert handoff["wallet_private_key_allowed"] is False
    assert handoff["real_account_allowed"] is False
    assert handoff["real_position_allowed"] is False
    assert handoff["buy_sell_order_allowed"] is False
    assert handoff["auto_position_allowed"] is False
    assert handoff["auto_portfolio_action_allowed"] is False


def test_final_handoff_marks_incomplete_without_repair():
    packet = _packet(status="INCOMPLETE")
    handoff = build_lifecycle_final_handoff(registry_packet=packet)
    result = classify_lifecycle_final_handoff(handoff)

    assert handoff["registry_handoff_status"] == "INCOMPLETE"
    assert result["final_action"] == "FINAL_MARK_INCOMPLETE"
    assert result["auto_repair_allowed"] is False
    assert result["evidence_backfill_allowed"] is False


def test_final_handoff_marks_stale_without_mutation():
    packet = _packet(status="STALE")
    handoff = build_lifecycle_final_handoff(registry_packet=packet)
    result = classify_lifecycle_final_handoff(handoff)

    assert handoff["registry_handoff_status"] == "STALE"
    assert result["final_action"] == "FINAL_MARK_STALE"
    assert result["source_artifact_mutation_allowed"] is False


def test_final_handoff_marks_unresolved_without_auto_pass():
    packet = _packet(status="REGISTERED")
    packet["registry_packet_status"] = "UNRESOLVED"

    handoff = build_lifecycle_final_handoff(registry_packet=packet)
    result = classify_lifecycle_final_handoff(handoff)

    assert handoff["registry_handoff_status"] == "UNRESOLVED"
    assert result["final_action"] == "FINAL_MARK_UNRESOLVED"
    assert result["auto_pass_allowed"] is False


def test_final_handoff_requires_packet():
    try:
        build_lifecycle_final_handoff(registry_packet=None)
    except ValueError as exc:
        assert "registry_packet is required" in str(exc)
    else:
        raise AssertionError("missing registry_packet should fail")
