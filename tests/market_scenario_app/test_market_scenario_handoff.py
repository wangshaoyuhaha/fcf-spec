from market_scenario_app.handoff import (
    APP_ID,
    COMPLETED_STAGES,
    STAGE_ID,
    build_market_scenario_closeout_summary,
    build_market_scenario_workflow_handoff,
    is_valid_market_scenario_closeout_summary,
    is_valid_market_scenario_workflow_handoff,
    validate_market_scenario_closeout_summary,
    validate_market_scenario_workflow_handoff,
)


def test_workflow_handoff_identity_and_completed_stages():
    handoff = build_market_scenario_workflow_handoff(generated_at_utc="2026-01-01T00:00:00+00:00")

    assert handoff.app_id == APP_ID
    assert handoff.stage_id == STAGE_ID
    assert handoff.completed_stages == COMPLETED_STAGES
    assert handoff.branch_name == "sidecar-market-scenario-app-1"


def test_workflow_handoff_safety_flags_forbid_execution_and_connections():
    handoff = build_market_scenario_workflow_handoff(generated_at_utc="2026-01-01T00:00:00+00:00")
    flags = handoff.safety_flags

    assert flags["paper_only"] is True
    assert flags["local_only"] is True
    assert flags["read_only"] is True
    assert flags["sidecar_only"] is True
    assert flags["operator_review_required"] is True
    assert flags["real_trading_allowed"] is False
    assert flags["real_execution_allowed"] is False
    assert flags["broker_connection_allowed"] is False
    assert flags["exchange_connection_allowed"] is False


def test_workflow_handoff_forbids_trade_release_and_deploy_downstream_uses():
    handoff = build_market_scenario_workflow_handoff(generated_at_utc="2026-01-01T00:00:00+00:00")

    assert "trade_instruction" in handoff.downstream_forbidden_uses
    assert "order_ticket" in handoff.downstream_forbidden_uses
    assert "automatic_position_sizing" in handoff.downstream_forbidden_uses
    assert "real_execution" in handoff.downstream_forbidden_uses
    assert "tag" in handoff.downstream_forbidden_uses
    assert "release" in handoff.downstream_forbidden_uses
    assert "deploy" in handoff.downstream_forbidden_uses
    assert handoff.safety_flags["tag_allowed"] is False
    assert handoff.safety_flags["release_allowed"] is False
    assert handoff.safety_flags["deploy_allowed"] is False


def test_valid_workflow_handoff_passes_validation():
    handoff = build_market_scenario_workflow_handoff(generated_at_utc="2026-01-01T00:00:00+00:00")

    assert validate_market_scenario_workflow_handoff(handoff) == []
    assert is_valid_market_scenario_workflow_handoff(handoff) is True
    assert handoff.to_dict()["merge_review_required"] is True


def test_closeout_summary_requires_operator_merge_review():
    summary = build_market_scenario_closeout_summary(final_pytest_expected="1293 passed")

    assert summary.closeout_status == "READY_FOR_OPERATOR_MERGE_REVIEW"
    assert summary.main_merge_allowed_without_operator_confirmation is False
    assert summary.operator_review_required is True
    assert summary.tag_allowed is False
    assert summary.release_allowed is False
    assert summary.deploy_allowed is False


def test_valid_closeout_summary_passes_validation():
    summary = build_market_scenario_closeout_summary(final_pytest_expected="1293 passed")

    assert validate_market_scenario_closeout_summary(summary) == []
    assert is_valid_market_scenario_closeout_summary(summary) is True
    assert summary.to_dict()["final_validation_expected"] == "ALL CHECKS PASSED"


def test_closeout_summary_no_execution_receipt_forbids_actions():
    summary = build_market_scenario_closeout_summary(final_pytest_expected="1293 passed")
    receipt = summary.no_execution_receipt

    assert receipt["trade_action_enabled"] is False
    assert receipt["buy_button_enabled"] is False
    assert receipt["sell_button_enabled"] is False
    assert receipt["order_button_enabled"] is False
    assert receipt["real_execution_allowed"] is False
    assert receipt["automatic_position_sizing_allowed"] is False
    assert receipt["automatic_portfolio_action_allowed"] is False
