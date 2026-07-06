from backtest_review_app.contract import (
    APP_ID,
    STAGE_ID,
    build_backtest_review_contract,
)


def test_backtest_review_contract_identity():
    contract = build_backtest_review_contract()
    assert contract.app_id == APP_ID
    assert contract.stage_id == STAGE_ID
    assert contract.purpose == "paper_only_local_historical_backtest_review_layer"


def test_backtest_review_contract_required_safety_flags():
    contract = build_backtest_review_contract()
    assert contract.required_safety_flags == {
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
    }
    assert contract.operator_review_required is True


def test_backtest_review_contract_allowed_inputs_and_outputs():
    contract = build_backtest_review_contract()
    assert "report_archive_outputs" in contract.allowed_input_sources
    assert "market_scenario_outputs" in contract.allowed_input_sources
    assert "operator_review_outputs" in contract.allowed_input_sources
    assert "data_quality_ops_outputs" in contract.allowed_input_sources
    assert "backtest_result_packet" in contract.allowed_outputs
    assert "paper_only_backtest_review_packet" in contract.allowed_outputs


def test_backtest_review_contract_forbids_real_execution_and_connections():
    contract = build_backtest_review_contract()
    forbidden = contract.forbidden_capabilities
    assert forbidden["real_trading_allowed"] is False
    assert forbidden["real_execution_allowed"] is False
    assert forbidden["broker_connection_allowed"] is False
    assert forbidden["exchange_connection_allowed"] is False
    assert forbidden["api_key_storage_allowed"] is False
    assert forbidden["wallet_private_key_access_allowed"] is False
    assert forbidden["real_account_access_allowed"] is False
    assert forbidden["real_position_access_allowed"] is False


def test_backtest_review_contract_forbids_trade_ui_and_release_actions():
    contract = build_backtest_review_contract()
    forbidden = contract.forbidden_capabilities
    assert forbidden["buy_button_enabled"] is False
    assert forbidden["sell_button_enabled"] is False
    assert forbidden["order_button_enabled"] is False
    assert forbidden["tag_allowed"] is False
    assert forbidden["release_allowed"] is False
    assert forbidden["deploy_allowed"] is False


def test_backtest_specific_forbidden_scope():
    contract = build_backtest_review_contract()
    scope = contract.backtest_forbidden_scope
    assert scope["backtest_result_as_profit_guarantee"] is False
    assert scope["backtest_metric_as_trade_instruction"] is False
    assert scope["backtest_review_status_bypass_operator_review"] is False
    assert scope["backtest_packet_as_order_ticket"] is False
    assert scope["automatic_position_sizing_allowed"] is False
    assert scope["automatic_portfolio_action_allowed"] is False
    assert scope["live_market_order_allowed"] is False
    assert scope["real_account_state_allowed"] is False
    assert scope["future_return_prediction_allowed"] is False
    assert scope["guaranteed_performance_claim_allowed"] is False


def test_backtest_review_contract_serializable_dict():
    contract_dict = build_backtest_review_contract().to_dict()
    assert contract_dict["app_id"] == "BACKTEST-REVIEW-APP-1"
    assert "market_scenario_outputs" in contract_dict["allowed_input_sources"]
    assert "paper_only_backtest_review_packet" in contract_dict["allowed_outputs"]
