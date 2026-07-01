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
        "source": "unit_test_policy_integration",
        "correlation_id": "p6-d3-policy-integration",
        "metadata": {
            "note": "paper only",
        },
    }


def test_handle_paper_execution_allows_safe_order_after_policy_gate():
    response = handle_paper_execution(
        raw_order=_sample_paper_order(),
        simulation_mode="simulated_fill",
    )

    assert response["ok"] is True
    assert response["api"] == "paper_execution_api"
    assert response["error"] is None
    assert response["data"]["execution_status"] == "filled"
    assert response["data"]["event_count"] == 1
    assert response["data"]["real_order"] is False
    assert response["data"]["real_execution"] is False


def test_handle_paper_execution_policy_denies_raw_order_real_order():
    raw_order = _sample_paper_order()
    raw_order["real_order"] = True

    response = handle_paper_execution(
        raw_order=raw_order,
        simulation_mode="simulated_fill",
    )

    assert response["ok"] is False
    assert response["api"] == "paper_execution_api"
    assert response["api_version"] == "0.1.0"
    assert response["data"] is None
    assert response["error"]["type"] == "PolicyDeny"
    assert "real order" in response["error"]["message"]


def test_handle_paper_execution_policy_denies_policy_context_save_api_key():
    response = handle_paper_execution(
        raw_order=_sample_paper_order(),
        simulation_mode="simulated_fill",
        policy_context={
            "metadata": {
                "save_api_key_requested": True,
            }
        },
    )

    assert response["ok"] is False
    assert response["data"] is None
    assert response["error"]["type"] == "PolicyDeny"
    assert "API keys" in response["error"]["message"]


def test_dify_paper_execution_adapter_passes_top_level_policy_context():
    response = route_dify_paper_execution_request(
        "POST",
        ROUTE_EXECUTE,
        {
            "raw_order": _sample_paper_order(),
            "simulation_mode": "simulated_fill",
            "bypass_risk_requested": True,
        },
    )

    assert response["http_status"] == 422
    assert response["body"]["ok"] is False
    assert response["body"]["api"] == "paper_execution_api"
    assert response["body"]["data"] is None
    assert response["body"]["error"]["type"] == "PolicyDeny"
    assert "risk" in response["body"]["error"]["message"]


def test_dify_paper_execution_adapter_safe_request_still_succeeds():
    response = route_dify_paper_execution_request(
        "POST",
        ROUTE_EXECUTE,
        {
            "raw_order": _sample_paper_order(),
            "simulation_mode": "simulated_reject",
            "reject_reason": "policy allowed then sandbox reject",
        },
    )

    assert response["http_status"] == 200
    assert response["body"]["ok"] is True
    assert response["body"]["data"]["execution_status"] == "rejected"
    assert response["body"]["data"]["real_execution"] is False
