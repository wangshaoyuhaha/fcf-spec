from fcf.api.dify_paper_execution_adapter import (
    ROUTE_EXECUTE,
    route_dify_paper_execution_request,
)
from fcf.api.paper_execution_api import handle_paper_execution


def _sample_paper_order():
    return {
        "asset_class": "Crypto",
        "symbol": "btcusdt",
        "venue": "BINANCE",
        "market_type": "PERP",
        "side": "BUY",
        "order_type": "LIMIT",
        "quantity": "0.25",
        "price": "60050.5",
        "time_in_force": "gtc",
        "source": "unit_test_risk_integration",
        "correlation_id": "p6-d8-risk-integration",
        "metadata": {
            "note": "paper only",
        },
    }


def _safe_risk_context():
    return {
        "max_quantity": 1.0,
        "max_notional": 100000.0,
        "allow_leverage": False,
        "allow_margin": False,
        "duplicate_order_keys": [],
        "blocked_symbols": [],
        "blocked_asset_classes": [],
        "high_risk_flags": [],
    }


def test_handle_paper_execution_allows_safe_order_after_risk_guardian():
    response = handle_paper_execution(
        raw_order=_sample_paper_order(),
        simulation_mode="simulated_fill",
        risk_context=_safe_risk_context(),
    )

    assert response["ok"] is True
    assert response["api"] == "paper_execution_api"
    assert response["error"] is None
    assert response["data"]["execution_status"] == "filled"
    assert response["data"]["event_count"] == 1
    assert response["data"]["real_order"] is False
    assert response["data"]["real_execution"] is False


def test_handle_paper_execution_risk_denies_max_quantity_before_sandbox_execution():
    risk_context = _safe_risk_context()
    risk_context["max_quantity"] = 0.1

    response = handle_paper_execution(
        raw_order=_sample_paper_order(),
        simulation_mode="simulated_fill",
        risk_context=risk_context,
    )

    assert response["ok"] is False
    assert response["api"] == "paper_execution_api"
    assert response["api_version"] == "0.1.0"
    assert response["data"] is None
    assert response["error"]["type"] == "RiskDeny"
    assert "max_quantity" in response["error"]["message"]


def test_handle_paper_execution_risk_denies_max_notional_before_sandbox_execution():
    risk_context = _safe_risk_context()
    risk_context["max_notional"] = 1000.0

    response = handle_paper_execution(
        raw_order=_sample_paper_order(),
        simulation_mode="simulated_fill",
        risk_context=risk_context,
    )

    assert response["ok"] is False
    assert response["data"] is None
    assert response["error"]["type"] == "RiskDeny"
    assert "max_notional" in response["error"]["message"]


def test_dify_adapter_passes_risk_context_and_returns_422_for_risk_deny():
    risk_context = _safe_risk_context()
    risk_context["blocked_symbols"] = ["BTCUSDT"]

    response = route_dify_paper_execution_request(
        "POST",
        ROUTE_EXECUTE,
        {
            "raw_order": _sample_paper_order(),
            "simulation_mode": "simulated_fill",
            "risk_context": risk_context,
        },
    )

    assert response["http_status"] == 422
    assert response["body"]["ok"] is False
    assert response["body"]["api"] == "paper_execution_api"
    assert response["body"]["data"] is None
    assert response["body"]["error"]["type"] == "RiskDeny"
    assert "blocked" in response["body"]["error"]["message"]


def test_dify_adapter_safe_risk_context_still_returns_200():
    response = route_dify_paper_execution_request(
        "POST",
        ROUTE_EXECUTE,
        {
            "raw_order": _sample_paper_order(),
            "simulation_mode": "simulated_reject",
            "reject_reason": "risk allowed then sandbox reject",
            "risk_context": _safe_risk_context(),
        },
    )

    assert response["http_status"] == 200
    assert response["body"]["ok"] is True
    assert response["body"]["data"]["execution_status"] == "rejected"
    assert response["body"]["data"]["real_execution"] is False
