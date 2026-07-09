import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fcf.sidecars.archive_correlation_rollup import (
    CORRELATION_ROLLUP_REQUIRED_LINKS,
    build_artifact_reference,
    build_chain_coverage_matrix,
    build_rollup_packet,
    build_trace_summary,
    classify_rollup_packet,
)


def _present_reference(link_type, correlation_id="corr-1", status="PRESENT"):
    return build_artifact_reference(
        link_type=link_type,
        artifact_id=f"{link_type}-1",
        artifact_path=f"runtime/archive/{link_type}-1.json",
        correlation_id=correlation_id,
        status=status,
        source_stage="existing-sidecar",
    )


def _complete_references():
    return [
        _present_reference(link_type)
        for link_type in CORRELATION_ROLLUP_REQUIRED_LINKS
    ]


def _packet_from_references(references):
    matrix = build_chain_coverage_matrix(
        correlation_id="corr-1",
        references=references,
    )
    summary = build_trace_summary(matrix)
    return build_rollup_packet(
        trace_summary=summary,
        artifact_references=references,
    )


def test_rollup_packet_complete_requires_operator_review():
    packet = _packet_from_references(_complete_references())
    result = classify_rollup_packet(packet)

    assert packet["stage"] == "D5"
    assert packet["packet_type"] == "correlation_rollup_packet"
    assert packet["rollup_status"] == "COMPLETE"
    assert packet["review_gate"] == "OPERATOR_REVIEW_REQUIRED"
    assert packet["operator_review_required"] is True
    assert packet["auto_pass_allowed"] is False
    assert result["packet_action"] == "QUEUE_OPERATOR_REVIEW"
    assert result["auto_pass_allowed"] is False


def test_rollup_packet_keeps_all_safety_flags_false():
    packet = _packet_from_references(_complete_references())

    assert packet["paper_only"] is True
    assert packet["local_only"] is True
    assert packet["read_only"] is True
    assert packet["sidecar_only"] is True
    assert packet["index_only"] is True
    assert packet["source_mutation_allowed"] is False
    assert packet["evidence_backfill_allowed"] is False
    assert packet["correlation_id_auto_fill_allowed"] is False
    assert packet["placeholder_review_allowed"] is False
    assert packet["ui_dashboard_panel_allowed"] is False
    assert packet["core_mutation_allowed"] is False
    assert packet["p48_core_expansion_allowed"] is False
    assert packet["tag_allowed"] is False
    assert packet["release_allowed"] is False
    assert packet["deploy_allowed"] is False
    assert packet["real_trade_allowed"] is False
    assert packet["broker_connection_allowed"] is False
    assert packet["exchange_connection_allowed"] is False
    assert packet["api_key_allowed"] is False
    assert packet["wallet_private_key_allowed"] is False
    assert packet["real_account_allowed"] is False
    assert packet["real_position_allowed"] is False
    assert packet["buy_sell_order_allowed"] is False
    assert packet["auto_position_allowed"] is False
    assert packet["auto_portfolio_action_allowed"] is False


def test_rollup_packet_marks_incomplete_without_repair():
    packet = _packet_from_references([_present_reference("data_snapshot")])
    result = classify_rollup_packet(packet)

    assert packet["rollup_status"] == "INCOMPLETE"
    assert result["packet_action"] == "MARK_INCOMPLETE"
    assert result["auto_repair_allowed"] is False
    assert result["evidence_backfill_allowed"] is False


def test_rollup_packet_marks_stale_without_placeholder_review():
    references = _complete_references()
    references[4] = _present_reference("review_packet", status="STALE")

    packet = _packet_from_references(references)
    result = classify_rollup_packet(packet)

    assert packet["rollup_status"] == "STALE"
    assert result["packet_action"] == "MARK_STALE"
    assert packet["placeholder_review_allowed"] is False


def test_rollup_packet_marks_unresolved_without_auto_fill():
    references = _complete_references()
    references[2] = _present_reference(
        "ai_explanation",
        correlation_id="corr-2",
    )

    packet = _packet_from_references(references)
    result = classify_rollup_packet(packet)

    assert packet["rollup_status"] == "UNRESOLVED"
    assert result["packet_action"] == "MARK_UNRESOLVED"
    assert packet["correlation_id_auto_fill_allowed"] is False


def test_rollup_packet_requires_correlation_id():
    try:
        build_rollup_packet(
            trace_summary={"rollup_status": "UNRESOLVED"},
            artifact_references=[],
        )
    except ValueError as exc:
        assert "correlation_id is required" in str(exc)
    else:
        raise AssertionError("missing correlation_id should fail")
