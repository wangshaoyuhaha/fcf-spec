import copy
import json
from pathlib import Path

from fcf.policy.portfolio_risk_guardian import evaluate_portfolio_risk_guardian


FIXTURE_PATH = Path("fixtures/paper_order_portfolios_multi_asset.json")


def _load_case(case_id):
    with FIXTURE_PATH.open("r", encoding="utf-8") as file:
        cases = json.load(file)

    return {
        case["case_id"]: case
        for case in cases
    }[case_id]


def _all_fill_request():
    return copy.deepcopy(_load_case("portfolio_all_fill")["request"])


def _evaluate(request):
    return evaluate_portfolio_risk_guardian(
        orders=request["orders"],
        risk_context=request["portfolio_risk_context"],
    )


def test_portfolio_risk_guardian_all_fill_passes():
    request = _all_fill_request()
    result = _evaluate(request)

    assert result["ok"] is True
    assert result["guardian"] == "portfolio_risk_guardian"
    assert result["guardian_version"] == "0.1.0"
    assert result["deny_reasons"] == []

    exposure = result["exposure"]

    assert exposure["order_count"] == 4
    assert exposure["order_count_by_asset_class"] == {
        "commodities": 1,
        "crypto": 1,
        "equities": 1,
        "fx": 1,
    }
    assert exposure["total_notional"] > 0
    assert set(exposure["notional_by_asset_class"].keys()) == {
        "commodities",
        "crypto",
        "equities",
        "fx",
    }


def test_portfolio_risk_guardian_denies_max_order_count():
    request = _all_fill_request()
    request["portfolio_risk_context"]["max_order_count"] = 1

    result = _evaluate(request)

    assert result["ok"] is False
    assert "max_order_count_exceeded" in result["deny_reasons"]
    assert result["checks"]["max_order_count"]["passed"] is False


def test_portfolio_risk_guardian_denies_max_total_notional():
    request = _all_fill_request()
    request["portfolio_risk_context"]["max_total_notional"] = 1.0

    result = _evaluate(request)

    assert result["ok"] is False
    assert "max_total_notional_exceeded" in result["deny_reasons"]
    assert result["checks"]["max_total_notional"]["passed"] is False


def test_portfolio_risk_guardian_denies_max_asset_class_notional():
    request = _all_fill_request()
    request["portfolio_risk_context"]["max_asset_class_notional"]["crypto"] = 1.0

    result = _evaluate(request)

    assert result["ok"] is False
    assert "max_asset_class_notional_exceeded" in result["deny_reasons"]
    assert result["checks"]["max_asset_class_notional"]["passed"] is False
    assert result["checks"]["max_asset_class_notional"]["hits"] == ["crypto"]


def test_portfolio_risk_guardian_denies_blocked_asset_class():
    request = _all_fill_request()
    request["portfolio_risk_context"]["blocked_asset_classes"] = ["commodities"]

    result = _evaluate(request)

    assert result["ok"] is False
    assert "blocked_asset_class" in result["deny_reasons"]
    assert result["checks"]["blocked_asset_classes"]["passed"] is False
    assert result["exposure"]["blocked_asset_classes_hit"] == ["commodities"]


def test_portfolio_risk_guardian_denies_blocked_symbol():
    request = _all_fill_request()
    request["portfolio_risk_context"]["blocked_symbols"] = ["btcusdt"]

    result = _evaluate(request)

    assert result["ok"] is False
    assert "blocked_symbol" in result["deny_reasons"]
    assert result["checks"]["blocked_symbols"]["passed"] is False
    assert result["exposure"]["blocked_symbols_hit"] == ["btcusdt"]


def test_portfolio_risk_guardian_denies_duplicate_order_key_from_context():
    request = _all_fill_request()
    request["portfolio_risk_context"]["duplicate_order_keys"] = ["p8-all-fill-crypto"]

    result = _evaluate(request)

    assert result["ok"] is False
    assert "duplicate_order_key" in result["deny_reasons"]
    assert result["checks"]["duplicate_order_keys"]["passed"] is False
    assert "p8-all-fill-crypto" in result["checks"]["duplicate_order_keys"]["hits"]


def test_portfolio_risk_guardian_denies_actual_duplicate_order_key():
    request = _all_fill_request()
    request["orders"][1]["order_id"] = request["orders"][0]["order_id"]

    result = _evaluate(request)

    assert result["ok"] is False
    assert "duplicate_order_key" in result["deny_reasons"]
    assert result["checks"]["duplicate_order_keys"]["passed"] is False
    assert "p8-all-fill-crypto" in result["exposure"]["duplicated_order_keys"]


def test_portfolio_risk_guardian_denies_max_same_side_count():
    request = _all_fill_request()
    request["portfolio_risk_context"]["max_same_side_count"] = 1

    result = _evaluate(request)

    assert result["ok"] is False
    assert "max_same_side_count_exceeded" in result["deny_reasons"]
    assert result["checks"]["max_same_side_count"]["passed"] is False


def test_portfolio_risk_guardian_denies_max_single_order_notional():
    request = _all_fill_request()
    request["portfolio_risk_context"]["max_single_order_notional"] = 1.0

    result = _evaluate(request)

    assert result["ok"] is False
    assert "max_single_order_notional_exceeded" in result["deny_reasons"]
    assert result["checks"]["max_single_order_notional"]["passed"] is False


def test_portfolio_risk_guardian_safe_boundary():
    request = _all_fill_request()
    result = _evaluate(request)
    boundary = result["safe_boundary"]

    assert boundary["execution_mode"] == "paper"
    assert boundary["real_order"] is False
    assert boundary["real_execution"] is False
    assert boundary["real_exchange_api"] is False
    assert boundary["real_money_impact"] is False
    assert boundary["no_real_exchange_api"] is True
    assert boundary["no_real_order_placement"] is True
    assert boundary["no_exchange_api_key_storage"] is True
    assert boundary["no_wallet_private_key_access"] is True
    assert boundary["policy_risk_cannot_be_bypassed"] is True
    assert boundary["portfolio_risk_deny_is_not_exchange_reject"] is True


def test_portfolio_paper_execution_api_uses_portfolio_risk_guardian():
    source = Path("fcf/api/portfolio_paper_execution_api.py").read_text(encoding="utf-8")

    assert "evaluate_portfolio_risk_guardian" in source
    assert "from fcf.policy.portfolio_risk_guardian import evaluate_portfolio_risk_guardian" in source
