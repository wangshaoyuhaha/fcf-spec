from copy import deepcopy

from apps.watchlist_lifecycle_app_1.contract import (
    APP_ID,
    STAGE_ID,
    UPSTREAM_READ_SOURCES,
    get_watchlist_lifecycle_contract,
    validate_watchlist_lifecycle_contract,
)


def test_watchlist_lifecycle_contract_identity_and_upstream_coverage():
    contract = get_watchlist_lifecycle_contract()

    assert contract["app_id"] == APP_ID
    assert contract["stage_id"] == STAGE_ID

    expected_sources = {
        "DATA-APP-1",
        "STOCK-APP-1",
        "AI-CONTEXT-1",
        "UI-APP-1",
        "OPERATOR-REVIEW-APP-1",
        "REPORT-ARCHIVE-APP-1",
        "DATA-QUALITY-OPS-APP-1",
        "MARKET-SCENARIO-APP-1",
        "BACKTEST-REVIEW-APP-1",
        "SIGNAL-VALIDATION-APP-1",
        "MODEL-GOVERNANCE-APP-1",
    }

    assert expected_sources.issubset(set(contract["upstream_read_sources"]))
    assert set(UPSTREAM_READ_SOURCES) == set(contract["upstream_read_sources"])


def test_watchlist_lifecycle_states_are_review_only():
    contract = get_watchlist_lifecycle_contract()
    state_ids = {item["state_id"] for item in contract["lifecycle_state_catalog"]}

    assert {
        "ENTRY_REVIEW",
        "ACTIVE_WATCH",
        "REVIEW_REQUIRED",
        "STALE_REVIEW",
        "DROP_REVIEW",
    }.issubset(state_ids)

    for state in contract["lifecycle_state_catalog"]:
        assert state["operator_review_required"] is True
        assert state["trade_action_allowed"] is False


def test_watchlist_lifecycle_safety_boundary_disables_trade_and_mutation_surfaces():
    contract = get_watchlist_lifecycle_contract()
    flags = contract["boundary_flags"]

    for key in [
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
        "operator_review_required",
    ]:
        assert flags[key] is True

    for key in [
        "operator_review_bypass_allowed",
        "p48_core_expansion_allowed",
        "p1_p47_core_mutation_allowed",
        "source_content_mutation_allowed",
        "source_deletion_allowed",
        "source_overwrite_allowed",
        "score_mutation_allowed",
        "reason_code_mutation_allowed",
        "risk_flag_deletion_allowed",
        "real_trading_allowed",
        "real_execution_allowed",
        "broker_connection_allowed",
        "exchange_connection_allowed",
        "api_key_storage_allowed",
        "wallet_private_key_access_allowed",
        "real_account_access_allowed",
        "real_position_access_allowed",
        "buy_button_enabled",
        "sell_button_enabled",
        "order_button_enabled",
        "automatic_position_sizing_allowed",
        "automatic_portfolio_action_allowed",
        "future_return_prediction_allowed",
        "guaranteed_performance_claim_allowed",
        "tag_allowed",
        "release_allowed",
        "deploy_allowed",
    ]:
        assert flags[key] is False


def test_watchlist_lifecycle_validator_accepts_contract_and_rejects_mutation():
    contract = get_watchlist_lifecycle_contract()
    result = validate_watchlist_lifecycle_contract(contract)

    assert result["valid"] is True
    assert result["issues"] == []

    mutated = deepcopy(contract)
    mutated["boundary_flags"]["real_trading_allowed"] = True
    mutated["boundary_flags"]["score_mutation_allowed"] = True

    failed = validate_watchlist_lifecycle_contract(mutated)

    assert failed["valid"] is False
    assert "real_trading_allowed must be false" in failed["issues"]
    assert "score_mutation_allowed must be false" in failed["issues"]
