import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fcf.sidecars.artifact_lifecycle_registry import (
    build_artifact_state_snapshot_index,
    build_lifecycle_registry_packet,
    build_lifecycle_registry_summary,
    build_transition_index,
    classify_lifecycle_registry_packet,
)


def _record(status="REGISTERED", artifact_id="artifact-1"):
    return {
        "artifact_id": artifact_id,
        "artifact_type": "archive_packet",
        "artifact_path": f"runtime/archive/{artifact_id}.json",
        "lifecycle_status": status,
    }


def _transition(
    artifact_id="artifact-1",
    from_status="REGISTERED",
    to_status="OBSERVED",
    reason_code="SOURCE_OBSERVED",
):
    return {
        "artifact_id": artifact_id,
        "from_status": from_status,
        "to_status": to_status,
        "reason_code": reason_code,
    }


def _summary(status="REGISTERED"):
    snapshot_index = build_artifact_state_snapshot_index(
        [_record(status=status)]
    )
    transition_index = build_transition_index((_transition(),))
    return build_lifecycle_registry_summary(
        snapshot_index=snapshot_index,
        transition_index=transition_index,
    )


def test_registry_packet_observed_still_requires_operator_review():
    packet = build_lifecycle_registry_packet(
        registry_summary=_summary(status="REGISTERED")
    )
    result = classify_lifecycle_registry_packet(packet)

    assert packet["stage"] == "D5"
    assert packet["packet_type"] == "artifact_lifecycle_registry_packet"
    assert packet["registry_packet_status"] == "OBSERVED"
    assert packet["review_gate"] == "OPERATOR_REVIEW_REQUIRED"
    assert packet["operator_review_required"] is True
    assert packet["auto_pass_allowed"] is False
    assert result["packet_action"] == "QUEUE_OPERATOR_REVIEW"
    assert result["auto_pass_allowed"] is False


def test_registry_packet_preserves_read_only_boundaries():
    packet = build_lifecycle_registry_packet(
        registry_summary=_summary(status="REGISTERED")
    )

    assert packet["paper_only"] is True
    assert packet["local_only"] is True
    assert packet["read_only"] is True
    assert packet["sidecar_only"] is True
    assert packet["index_only"] is True
    assert packet["packet_only"] is True
    assert packet["source_artifact_mutation_allowed"] is False
    assert packet["artifact_status_auto_repair_allowed"] is False
    assert packet["transition_applied"] is False
    assert packet["evidence_backfill_allowed"] is False
    assert packet["correlation_id_auto_fill_allowed"] is False
    assert packet["placeholder_review_allowed"] is False
    assert packet["ui_dashboard_panel_allowed"] is False
    assert packet["core_mutation_allowed"] is False
    assert packet["p48_core_expansion_allowed"] is False


def test_registry_packet_forbids_release_execution_and_credentials():
    packet = build_lifecycle_registry_packet(
        registry_summary=_summary(status="REGISTERED")
    )

    assert packet["tag_allowed"] is False
    assert packet["release_allowed"] is False
    assert packet["deploy_allowed"] is False
    assert packet["real_trade_allowed"] is False
    assert packet["real_execution_allowed"] is False
    assert packet["broker_connection_allowed"] is False
    assert packet["exchange_connection_allowed"] is False
    assert packet["api_key_allowed"] is False
    assert packet["wallet_private_key_allowed"] is False
    assert packet["real_account_allowed"] is False
    assert packet["real_position_allowed"] is False
    assert packet["buy_sell_order_allowed"] is False
    assert packet["auto_position_allowed"] is False
    assert packet["auto_portfolio_action_allowed"] is False


def test_registry_packet_marks_incomplete_without_repair():
    packet = build_lifecycle_registry_packet(
        registry_summary=_summary(status="INCOMPLETE")
    )
    result = classify_lifecycle_registry_packet(packet)

    assert packet["registry_packet_status"] == "INCOMPLETE"
    assert result["packet_action"] == "MARK_INCOMPLETE"
    assert result["auto_repair_allowed"] is False
    assert result["evidence_backfill_allowed"] is False


def test_registry_packet_marks_stale_without_mutation():
    packet = build_lifecycle_registry_packet(
        registry_summary=_summary(status="STALE")
    )
    result = classify_lifecycle_registry_packet(packet)

    assert packet["registry_packet_status"] == "STALE"
    assert result["packet_action"] == "MARK_STALE"
    assert result["source_artifact_mutation_allowed"] is False


def test_registry_packet_marks_unresolved_without_auto_pass():
    summary = _summary(status="REGISTERED")
    summary["registry_summary_status"] = "UNRESOLVED"

    packet = build_lifecycle_registry_packet(registry_summary=summary)
    result = classify_lifecycle_registry_packet(packet)

    assert packet["registry_packet_status"] == "UNRESOLVED"
    assert result["packet_action"] == "MARK_UNRESOLVED"
    assert result["auto_pass_allowed"] is False


def test_registry_packet_requires_summary():
    try:
        build_lifecycle_registry_packet(registry_summary=None)
    except ValueError as exc:
        assert "registry_summary is required" in str(exc)
    else:
        raise AssertionError("missing registry_summary should fail")
