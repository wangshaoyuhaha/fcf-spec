import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fcf.sidecars.validation_baseline_registry import (
    build_validation_baseline_final_handoff,
    build_validation_baseline_packet,
    build_validation_baseline_snapshot_index,
    build_validation_baseline_summary,
    build_validation_run_index,
    build_validation_run_record,
    classify_validation_baseline_final_handoff,
)


def _record(result="PASS", pass_count=2075, baseline_status="REGISTERED"):
    return build_validation_run_record(
        validation_id="validation-1",
        command="python -m pytest -q",
        result=result,
        pass_count=pass_count,
        git_branch="main",
        git_head="bce988c",
        git_status="clean",
        origin_status="synced",
        output_summary="2075 passed",
        baseline_status=baseline_status,
    )


def _packet(result="PASS", pass_count=2075, baseline_status="REGISTERED"):
    record = _record(
        result=result,
        pass_count=pass_count,
        baseline_status=baseline_status,
    )
    snapshot_index = build_validation_baseline_snapshot_index([record])
    run_index = build_validation_run_index([record])
    summary = build_validation_baseline_summary(
        snapshot_index=snapshot_index,
        run_index=run_index,
    )
    return build_validation_baseline_packet(baseline_summary=summary)


def test_final_handoff_verified_goes_to_operator_review_only():
    handoff = build_validation_baseline_final_handoff(
        baseline_packet=_packet()
    )
    result = classify_validation_baseline_final_handoff(handoff)

    assert handoff["stage"] == "D6"
    assert handoff["handoff_type"] == "validation_baseline_registry_final_handoff"
    assert handoff["baseline_handoff_status"] == "VERIFIED"
    assert handoff["final_gate"] == "OPERATOR_REVIEW_REQUIRED"
    assert handoff["operator_review_required"] is True
    assert handoff["auto_pass_allowed"] is False
    assert result["final_action"] == "HANDOFF_TO_OPERATOR_REVIEW"
    assert result["auto_pass_allowed"] is False


def test_final_handoff_preserves_read_only_boundaries():
    handoff = build_validation_baseline_final_handoff(
        baseline_packet=_packet()
    )

    assert handoff["paper_only"] is True
    assert handoff["local_only"] is True
    assert handoff["read_only"] is True
    assert handoff["sidecar_only"] is True
    assert handoff["index_only"] is True
    assert handoff["handoff_only"] is True
    assert handoff["validation_result_fabrication_allowed"] is False
    assert handoff["pass_count_fabrication_allowed"] is False
    assert handoff["source_artifact_mutation_allowed"] is False
    assert handoff["evidence_backfill_allowed"] is False
    assert handoff["correlation_id_auto_fill_allowed"] is False
    assert handoff["placeholder_review_allowed"] is False
    assert handoff["ui_dashboard_panel_allowed"] is False
    assert handoff["core_mutation_allowed"] is False
    assert handoff["p48_core_expansion_allowed"] is False


def test_final_handoff_forbids_release_execution_and_credentials():
    handoff = build_validation_baseline_final_handoff(
        baseline_packet=_packet()
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
    packet = _packet(
        result="INCOMPLETE",
        pass_count=0,
        baseline_status="INCOMPLETE",
    )
    handoff = build_validation_baseline_final_handoff(baseline_packet=packet)
    result = classify_validation_baseline_final_handoff(handoff)

    assert handoff["baseline_handoff_status"] == "INCOMPLETE"
    assert result["final_action"] == "FINAL_MARK_INCOMPLETE"
    assert result["auto_repair_allowed"] is False
    assert result["evidence_backfill_allowed"] is False


def test_final_handoff_marks_stale_without_fabrication():
    packet = _packet(
        result="FAIL",
        pass_count=0,
        baseline_status="STALE",
    )
    handoff = build_validation_baseline_final_handoff(baseline_packet=packet)
    result = classify_validation_baseline_final_handoff(handoff)

    assert handoff["baseline_handoff_status"] == "STALE"
    assert result["final_action"] == "FINAL_MARK_STALE"
    assert result["validation_result_fabrication_allowed"] is False
    assert result["pass_count_fabrication_allowed"] is False


def test_final_handoff_marks_unresolved_without_auto_pass():
    packet = _packet()
    packet["baseline_packet_status"] = "UNRESOLVED"

    handoff = build_validation_baseline_final_handoff(baseline_packet=packet)
    result = classify_validation_baseline_final_handoff(handoff)

    assert handoff["baseline_handoff_status"] == "UNRESOLVED"
    assert result["final_action"] == "FINAL_MARK_UNRESOLVED"
    assert result["auto_pass_allowed"] is False


def test_final_handoff_requires_packet():
    try:
        build_validation_baseline_final_handoff(baseline_packet=None)
    except ValueError as exc:
        assert "baseline_packet is required" in str(exc)
    else:
        raise AssertionError("missing baseline_packet should fail")
