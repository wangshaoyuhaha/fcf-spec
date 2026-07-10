import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fcf.sidecars.validation_baseline_registry import (
    build_validation_baseline_packet,
    build_validation_baseline_snapshot_index,
    build_validation_baseline_summary,
    build_validation_run_index,
    build_validation_run_record,
    classify_validation_baseline_packet,
)


def _record(result="PASS", pass_count=2068, baseline_status="REGISTERED"):
    return build_validation_run_record(
        validation_id="validation-1",
        command="python -m pytest -q",
        result=result,
        pass_count=pass_count,
        git_branch="main",
        git_head="90f27b7",
        git_status="clean",
        origin_status="synced",
        output_summary="2068 passed",
        baseline_status=baseline_status,
    )


def _summary(result="PASS", pass_count=2068, baseline_status="REGISTERED"):
    record = _record(
        result=result,
        pass_count=pass_count,
        baseline_status=baseline_status,
    )
    snapshot_index = build_validation_baseline_snapshot_index([record])
    run_index = build_validation_run_index([record])
    return build_validation_baseline_summary(
        snapshot_index=snapshot_index,
        run_index=run_index,
    )


def test_packet_verified_still_requires_operator_review():
    packet = build_validation_baseline_packet(
        baseline_summary=_summary()
    )
    result = classify_validation_baseline_packet(packet)

    assert packet["stage"] == "D5"
    assert packet["packet_type"] == "validation_baseline_registry_packet"
    assert packet["baseline_packet_status"] == "VERIFIED"
    assert packet["review_gate"] == "OPERATOR_REVIEW_REQUIRED"
    assert packet["operator_review_required"] is True
    assert packet["auto_pass_allowed"] is False
    assert result["packet_action"] == "QUEUE_OPERATOR_REVIEW"
    assert result["auto_pass_allowed"] is False


def test_packet_preserves_read_only_boundaries():
    packet = build_validation_baseline_packet(
        baseline_summary=_summary()
    )

    assert packet["paper_only"] is True
    assert packet["local_only"] is True
    assert packet["read_only"] is True
    assert packet["sidecar_only"] is True
    assert packet["index_only"] is True
    assert packet["packet_only"] is True
    assert packet["validation_result_fabrication_allowed"] is False
    assert packet["pass_count_fabrication_allowed"] is False
    assert packet["source_artifact_mutation_allowed"] is False
    assert packet["evidence_backfill_allowed"] is False
    assert packet["correlation_id_auto_fill_allowed"] is False
    assert packet["placeholder_review_allowed"] is False
    assert packet["ui_dashboard_panel_allowed"] is False
    assert packet["core_mutation_allowed"] is False
    assert packet["p48_core_expansion_allowed"] is False


def test_packet_forbids_release_execution_and_credentials():
    packet = build_validation_baseline_packet(
        baseline_summary=_summary()
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


def test_packet_marks_incomplete_without_repair():
    packet = build_validation_baseline_packet(
        baseline_summary=_summary(
            result="INCOMPLETE",
            pass_count=0,
            baseline_status="INCOMPLETE",
        )
    )
    result = classify_validation_baseline_packet(packet)

    assert packet["baseline_packet_status"] == "INCOMPLETE"
    assert result["packet_action"] == "MARK_INCOMPLETE"
    assert result["auto_repair_allowed"] is False
    assert result["evidence_backfill_allowed"] is False


def test_packet_marks_stale_without_fabrication():
    packet = build_validation_baseline_packet(
        baseline_summary=_summary(
            result="FAIL",
            pass_count=0,
            baseline_status="STALE",
        )
    )
    result = classify_validation_baseline_packet(packet)

    assert packet["baseline_packet_status"] == "STALE"
    assert result["packet_action"] == "MARK_STALE"
    assert result["validation_result_fabrication_allowed"] is False
    assert result["pass_count_fabrication_allowed"] is False


def test_packet_marks_unresolved_without_auto_pass():
    summary = _summary()
    summary["summary_status"] = "UNRESOLVED"

    packet = build_validation_baseline_packet(baseline_summary=summary)
    result = classify_validation_baseline_packet(packet)

    assert packet["baseline_packet_status"] == "UNRESOLVED"
    assert result["packet_action"] == "MARK_UNRESOLVED"
    assert result["auto_pass_allowed"] is False


def test_packet_requires_summary():
    try:
        build_validation_baseline_packet(baseline_summary=None)
    except ValueError as exc:
        assert "baseline_summary is required" in str(exc)
    else:
        raise AssertionError("missing baseline_summary should fail")
