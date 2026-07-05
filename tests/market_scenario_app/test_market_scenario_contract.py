from market_scenario_app.contract import (
    APP_ID,
    STAGE_ID,
    build_market_scenario_contract,
)


def test_market_scenario_contract_identity():
    contract = build_market_scenario_contract()
    assert contract.app_id == APP_ID
    assert contract.stage_id == STAGE_ID
    assert contract.purpose == "paper_only_local_market_scenario_review_layer"


def test_market_scenario_contract_required_safety_flags():
    contract = build_market_scenario_contract()
    assert contract.required_safety_flags == {
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
    }
    assert contract.operator_review_required is True


def test_market_scenario_contract_forbids_real_execution_and_trading():
    contract = build_market_scenario_contract()
    forbidden = contract.forbidden_capabilities
    assert forbidden["real_trading_allowed"] is False
    assert forbidden["real_execution_allowed"] is False
    assert forbidden["broker_connection_allowed"] is False
    assert forbidden["exchange_connection_allowed"] is False
    assert forbidden["api_key_storage_allowed"] is False
    assert forbidden["wallet_private_key_access_allowed"] is False
    assert forbidden["real_account_access_allowed"] is False
    assert forbidden["real_position_access_allowed"] is False


def test_market_scenario_contract_forbids_trade_ui_and_release_actions():
    contract = build_market_scenario_contract()
    forbidden = contract.forbidden_capabilities
    assert forbidden["buy_button_enabled"] is False
    assert forbidden["sell_button_enabled"] is False
    assert forbidden["order_button_enabled"] is False
    assert forbidden["tag_allowed"] is False
    assert forbidden["release_allowed"] is False
    assert forbidden["deploy_allowed"] is False


def test_market_scenario_specific_forbidden_scope():
    contract = build_market_scenario_contract()
    scope = contract.scenario_forbidden_scope
    assert scope["scenario_label_as_trade_instruction"] is False
    assert scope["scenario_score_as_trade_instruction"] is False
    assert scope["scenario_review_status_bypass_operator_review"] is False
    assert scope["scenario_packet_as_order_ticket"] is False
    assert scope["automatic_position_sizing_allowed"] is False
    assert scope["automatic_portfolio_action_allowed"] is False
    assert scope["live_market_order_allowed"] is False
    assert scope["real_account_state_allowed"] is False


def test_market_scenario_contract_serializable_dict():
    contract_dict = build_market_scenario_contract().to_dict()
    assert contract_dict["app_id"] == "MARKET-SCENARIO-APP-1"
    assert "report_archive_outputs" in contract_dict["allowed_input_sources"]
    assert "paper_only_scenario_review_packet" in contract_dict["allowed_outputs"]
