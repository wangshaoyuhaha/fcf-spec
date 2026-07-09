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
    build_final_handoff,
    build_rollup_packet,
    build_trace_summary,
    classify_final_handoff,
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


def _complete_packet():
    references = []
    for link_type in CORRELATION_ROLLUP_REQUIRED_LINKS:
        references.append(_present_reference(link_type))

    matrix = build_chain_coverage_matrix(
        correlation_id="corr-1",
        references=references,
    )
    summary = build_trace_summary(matrix)

    return build_rollup_packet(
        trace_summary=summary,
        artifact_references=references,
    )


def test_final_handoff_complete_goes_to_operator_review_only():
    packet = _complete_packet()
    handoff = build_final_handoff(rollup_packet=packet)
    result = classify_final_handoff(handoff)

    assert handoff["stage"] == "D6"
    assert handoff["rollup_status"] == "COMPLETE"
    assert handoff["final_gate"] == "OPERATOR_REVIEW_REQUIRED"
    assert handoff["operator_review_required"] is True
    assert handoff["auto_pass_allowed"] is False
    assert result["final_action"] == "HANDOFF_TO_OPERATOR_REVIEW"
    assert result["auto_pass_allowed"] is False


def test_final_handoff_preserves_safety_boundary():
    handoff = build_final_handoff(rollup_packet=_complete_packet())

    assert handoff["paper_only"] is True
    assert handoff["local_only"] is True
    assert handoff["read_only"] is True
    assert handoff["sidecar_only"] is True
    assert handoff["index_only"] is True
    assert handoff["source_mutation_allowed"] is False
    assert handoff["core_mutation_allowed"] is False
    assert handoff["p48_core_expansion_allowed"] is False
    assert handoff["evidence_backfill_allowed"] is False
    assert handoff["correlation_id_auto_fill_allowed"] is False
    assert handoff["placeholder_review_allowed"] is False
    assert handoff["ui_dashboard_panel_allowed"] is False


def test_final_handoff_forbids_execution_release_and_credentials():
    handoff = build_final_handoff(rollup_packet=_complete_packet())

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
    packet = _complete_packet()
    packet["rollup_status"] = "INCOMPLETE"

    handoff = build_final_handoff(rollup_packet=packet)
    result = classify_final_handoff(handoff)

    assert handoff["rollup_status"] == "INCOMPLETE"
    assert result["final_action"] == "FINAL_MARK_INCOMPLETE"
    assert result["auto_repair_allowed"] is False


def test_final_handoff_marks_stale_without_execution():
    packet = _complete_packet()
    packet["rollup_status"] = "STALE"

    handoff = build_final_handoff(rollup_packet=packet)
    result = classify_final_handoff(handoff)

    assert handoff["rollup_status"] == "STALE"
    assert result["final_action"] == "FINAL_MARK_STALE"
    assert result["real_execution_allowed"] is False


def test_final_handoff_marks_unresolved_without_auto_pass():
    packet = _complete_packet()
    packet["rollup_status"] = "UNRESOLVED"

    handoff = build_final_handoff(rollup_packet=packet)
    result = classify_final_handoff(handoff)

    assert handoff["rollup_status"] == "UNRESOLVED"
    assert result["final_action"] == "FINAL_MARK_UNRESOLVED"
    assert result["auto_pass_allowed"] is False


def test_final_handoff_requires_correlation_id():
    packet = _complete_packet()
    packet["correlation_id"] = ""

    try:
        build_final_handoff(rollup_packet=packet)
    except ValueError as exc:
        assert "correlation_id is required" in str(exc)
    else:
        raise AssertionError("missing correlation_id should fail")
