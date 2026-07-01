from fcf.risk.paper_execution_risk_guardian import (
    describe_paper_execution_risk_guardian,
    evaluate_paper_execution_risk,
)


def _sample_raw_order():
    return {
        "asset_class": "crypto",
        "symbol": "BTCUSDT",
        "venue": "binance",
        "market_type": "perp",
        "side": "buy",
        "order_type": "limit",
        "quantity": "0.25",
        "price": "60050.5",
        "source": "unit_test_risk_guardian",
        "correlation_id": "p6-d7-risk",
        "metadata": {
            "note": "paper only",
        },
    }


def _sample_risk_context():
    return {
        "max_quantity": 1.0,
        "max_notional": 100000.0,
        "allow_missing_risk_context": False,
        "allow_leverage": False,
        "allow_margin": False,
        "duplicate_order_keys": [],
        "blocked_symbols": [],
        "blocked_asset_classes": [],
        "high_risk_flags": [],
    }


def _sample_request():
    return {
        "raw_order": _sample_raw_order(),
        "risk_context": _sample_risk_context(),
    }


def test_describe_paper_execution_risk_guardian_declares_contract_and_boundary():
    description = describe_paper_execution_risk_guardian()

    assert description["guardian"] == "paper_execution_risk_guardian"
    assert description["guardian_version"] == "0.1.0"
    assert "max_quantity" in description["risk_rules"]
    assert "max_notional" in description["risk_rules"]
    assert "duplicate_order_key" in description["risk_rules"]
    assert description["decision_values"] == ["allowed", "denied"]
    assert description["safe_boundary"]["execution_mode"] == "paper"
    assert description["safe_boundary"]["real_order"] is False
    assert description["safe_boundary"]["real_execution"] is False
    assert description["safe_boundary"]["no_real_exchange_api"] is True


def test_risk_guardian_allows_safe_paper_request():
    result = evaluate_paper_execution_risk(_sample_request())

    assert result["ok"] is True
    assert result["guardian"] == "paper_execution_risk_guardian"
    assert result["guardian_version"] == "0.1.0"
    assert result["decision"] == "allowed"
    assert result["error"] is None
    assert result["data"]["risk_allowed"] is True
    assert result["data"]["order_key"] == "crypto:BTCUSDT:buy:limit:p6-d7-risk"
    assert result["data"]["order_summary"]["quantity"] == 0.25
    assert result["data"]["order_summary"]["price"] == 60050.5
    assert result["data"]["safe_boundary"]["real_execution"] is False


def test_risk_guardian_rejects_non_dict_request():
    result = evaluate_paper_execution_risk(None)

    assert result["ok"] is False
    assert result["decision"] == "denied"
    assert result["error"]["type"] == "RiskDeny"
    assert result["risk_violation"]["rule"] == "request_must_be_dict"
    assert "dict" in result["error"]["message"]


def test_risk_guardian_rejects_missing_raw_order():
    result = evaluate_paper_execution_risk({"risk_context": _sample_risk_context()})

    assert result["ok"] is False
    assert result["decision"] == "denied"
    assert result["error"]["type"] == "RiskDeny"
    assert result["risk_violation"]["rule"] == "raw_order_must_be_dict"
    assert "raw_order" in result["error"]["message"]


def test_risk_guardian_rejects_missing_risk_context_by_default():
    result = evaluate_paper_execution_risk({"raw_order": _sample_raw_order()})

    assert result["ok"] is False
    assert result["decision"] == "denied"
    assert result["error"]["type"] == "RiskDeny"
    assert result["risk_violation"]["rule"] == "missing_risk_context"
    assert "risk_context" in result["error"]["message"]


def test_risk_guardian_can_allow_missing_risk_context_only_when_explicitly_allowed():
    result = evaluate_paper_execution_risk(
        {
            "raw_order": _sample_raw_order(),
            "allow_missing_risk_context": True,
        }
    )

    assert result["ok"] is True
    assert result["decision"] == "allowed"
    assert result["data"]["risk_allowed"] is True


def test_risk_guardian_rejects_quantity_above_max_quantity():
    request = _sample_request()
    request["raw_order"]["quantity"] = "2"

    result = evaluate_paper_execution_risk(request)

    assert result["ok"] is False
    assert result["decision"] == "denied"
    assert result["risk_violation"]["rule"] == "max_quantity"
    assert result["risk_violation"]["field"] == "quantity"
    assert "max_quantity" in result["error"]["message"]


def test_risk_guardian_rejects_notional_above_max_notional():
    request = _sample_request()
    request["risk_context"]["max_notional"] = 1000.0

    result = evaluate_paper_execution_risk(request)

    assert result["ok"] is False
    assert result["decision"] == "denied"
    assert result["risk_violation"]["rule"] == "max_notional"
    assert result["risk_violation"]["field"] == "notional"
    assert "max_notional" in result["error"]["message"]


def test_risk_guardian_rejects_duplicate_order_key():
    request = _sample_request()
    request["risk_context"]["duplicate_order_keys"] = [
        "crypto:BTCUSDT:buy:limit:p6-d7-risk",
    ]

    result = evaluate_paper_execution_risk(request)

    assert result["ok"] is False
    assert result["decision"] == "denied"
    assert result["risk_violation"]["rule"] == "duplicate_order_key"
    assert "duplicate" in result["error"]["message"]


def test_risk_guardian_rejects_blocked_symbol():
    request = _sample_request()
    request["risk_context"]["blocked_symbols"] = ["btcusdt"]

    result = evaluate_paper_execution_risk(request)

    assert result["ok"] is False
    assert result["risk_violation"]["rule"] == "blocked_symbol"
    assert result["risk_violation"]["field"] == "symbol"
    assert "BTCUSDT" in result["error"]["message"]


def test_risk_guardian_rejects_blocked_asset_class():
    request = _sample_request()
    request["risk_context"]["blocked_asset_classes"] = ["crypto"]

    result = evaluate_paper_execution_risk(request)

    assert result["ok"] is False
    assert result["risk_violation"]["rule"] == "blocked_asset_class"
    assert result["risk_violation"]["field"] == "asset_class"
    assert "crypto" in result["error"]["message"]


def test_risk_guardian_rejects_leverage_request():
    request = _sample_request()
    request["raw_order"]["metadata"]["leverage"] = 3

    result = evaluate_paper_execution_risk(request)

    assert result["ok"] is False
    assert result["risk_violation"]["rule"] == "leverage_requested"
    assert result["risk_violation"]["field"] == "leverage"
    assert "leverage" in result["error"]["message"]


def test_risk_guardian_rejects_margin_request():
    request = _sample_request()
    request["metadata"] = {
        "margin_requested": True,
    }

    result = evaluate_paper_execution_risk(request)

    assert result["ok"] is False
    assert result["risk_violation"]["rule"] == "margin_requested"
    assert result["risk_violation"]["field"] == "margin_requested"
    assert "margin" in result["error"]["message"]


def test_risk_guardian_rejects_high_risk_flags():
    request = _sample_request()
    request["risk_context"]["high_risk_flags"] = [
        "high_uncertainty",
    ]

    result = evaluate_paper_execution_risk(request)

    assert result["ok"] is False
    assert result["risk_violation"]["rule"] == "high_risk_flags"
    assert result["risk_violation"]["field"] == "high_risk_flags"
    assert "high risk" in result["error"]["message"]
