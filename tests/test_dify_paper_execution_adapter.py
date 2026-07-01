from pathlib import Path

from fcf.api.dify_paper_execution_adapter import (
    ROUTE_CONTRACT,
    ROUTE_EXECUTE,
    describe_routes,
    route_dify_paper_execution_request,
)


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
        "source": "unit_test_dify_paper_execution_adapter",
        "correlation_id": "p5-d7-dify-paper-execution",
        "metadata": {
            "note": "paper only",
        },
        "real_order": True,
        "real_exchange_api": True,
        "real_money_impact": True,
    }


def test_describe_routes_declares_contract_and_safe_boundary():
    routes = describe_routes()

    assert routes["api"] == "dify_paper_execution_adapter"
    assert routes["api_version"] == "0.1.0"
    assert "GET /api/v1/paper-execution/contract" in routes["routes"]
    assert "POST /api/v1/paper-execution/execute" in routes["routes"]
    assert routes["paper_execution_contract"]["api"] == "paper_execution_api"
    assert routes["safe_boundary"]["execution_mode"] == "paper"
    assert routes["safe_boundary"]["real_order"] is False
    assert routes["safe_boundary"]["real_execution"] is False
    assert routes["safe_boundary"]["only_calls_paper_execution_api"] is True


def test_contract_route_returns_200_and_contract_data():
    response = route_dify_paper_execution_request("GET", ROUTE_CONTRACT)

    assert response["http_status"] == 200
    assert response["headers"]["content-type"] == "application/json"
    assert response["body"]["ok"] is True
    assert response["body"]["api"] == "dify_paper_execution_adapter"
    assert response["body"]["data"]["paper_execution_contract"]["api"] == "paper_execution_api"
    assert response["body"]["data"]["safe_boundary"]["no_real_exchange_api"] is True


def test_execute_route_simulated_fill_returns_200_and_paper_success():
    response = route_dify_paper_execution_request(
        "POST",
        ROUTE_EXECUTE,
        {
            "raw_order": _sample_paper_order(),
            "simulation_mode": "simulated_fill",
        },
    )

    assert response["http_status"] == 200
    assert response["body"]["ok"] is True
    assert response["body"]["api"] == "paper_execution_api"

    data = response["body"]["data"]

    assert data["execution_status"] == "filled"
    assert data["event_name"] == "fcf.sandbox.execution.filled"
    assert data["event_count"] == 1
    assert data["replay"]["status"] == "completed"
    assert data["execution_mode"] == "paper"
    assert data["real_order"] is False
    assert data["real_execution"] is False
    assert data["real_exchange_api"] is False
    assert data["real_money_impact"] is False


def test_execute_route_simulated_reject_returns_200_and_rejected_status():
    response = route_dify_paper_execution_request(
        "POST",
        ROUTE_EXECUTE,
        {
            "raw_order": _sample_paper_order(),
            "simulation_mode": "simulated_reject",
            "reject_reason": "policy denied in Dify adapter test",
        },
    )

    assert response["http_status"] == 200
    assert response["body"]["ok"] is True

    data = response["body"]["data"]

    assert data["execution_status"] == "rejected"
    assert data["event_name"] == "fcf.sandbox.execution.rejected"
    assert data["reject_reason"] == "policy denied in Dify adapter test"
    assert data["real_execution"] is False


def test_execute_route_partial_fill_accepts_string_numbers():
    response = route_dify_paper_execution_request(
        "POST",
        ROUTE_EXECUTE,
        {
            "raw_order": _sample_paper_order(),
            "simulation_mode": "simulated_fill",
            "filled_quantity": "0.10",
            "fill_price": "60051.0",
        },
    )

    assert response["http_status"] == 200
    assert response["body"]["ok"] is True

    data = response["body"]["data"]

    assert data["execution_status"] == "partial_filled"
    assert data["filled_quantity"] == 0.10
    assert data["remaining_quantity"] == 0.15
    assert data["fill_price"] == 60051.0


def test_execute_route_bad_order_returns_422_stable_error():
    raw_order = _sample_paper_order()
    raw_order["quantity"] = "-1"

    response = route_dify_paper_execution_request(
        "POST",
        ROUTE_EXECUTE,
        {
            "raw_order": raw_order,
            "simulation_mode": "simulated_fill",
        },
    )

    assert response["http_status"] == 422
    assert response["body"]["ok"] is False
    assert response["body"]["api"] == "paper_execution_api"
    assert response["body"]["data"] is None
    assert response["body"]["error"]["type"] == "ValueError"
    assert "quantity" in response["body"]["error"]["message"]


def test_execute_route_bad_simulation_mode_returns_422_stable_error():
    response = route_dify_paper_execution_request(
        "POST",
        ROUTE_EXECUTE,
        {
            "raw_order": _sample_paper_order(),
            "simulation_mode": "real_execution",
        },
    )

    assert response["http_status"] == 422
    assert response["body"]["ok"] is False
    assert response["body"]["api"] == "paper_execution_api"
    assert response["body"]["error"]["type"] == "ValueError"
    assert "simulation_mode" in response["body"]["error"]["message"]


def test_adapter_rejects_unknown_route_wrong_method_and_missing_body():
    unknown = route_dify_paper_execution_request("POST", "/api/v1/not-real", {})
    wrong_method = route_dify_paper_execution_request("GET", ROUTE_EXECUTE, {})
    missing_body = route_dify_paper_execution_request("POST", ROUTE_EXECUTE)
    missing_raw_order = route_dify_paper_execution_request(
        "POST",
        ROUTE_EXECUTE,
        {
            "simulation_mode": "simulated_fill",
        },
    )

    assert unknown["http_status"] == 404
    assert unknown["body"]["error"]["type"] == "NotFound"

    assert wrong_method["http_status"] == 405
    assert wrong_method["body"]["error"]["type"] == "MethodNotAllowed"

    assert missing_body["http_status"] == 400
    assert missing_body["body"]["error"]["type"] == "BadRequest"
    assert "body" in missing_body["body"]["error"]["message"]

    assert missing_raw_order["http_status"] == 400
    assert missing_raw_order["body"]["error"]["type"] == "BadRequest"
    assert "raw_order" in missing_raw_order["body"]["error"]["message"]


def test_execute_route_can_persist_jsonl(tmp_path):
    output_path = tmp_path / "dify_paper_execution.jsonl"

    response = route_dify_paper_execution_request(
        "POST",
        ROUTE_EXECUTE,
        {
            "raw_order": _sample_paper_order(),
            "simulation_mode": "simulated_fill",
            "output_path": str(output_path),
        },
    )

    assert response["http_status"] == 200
    assert response["body"]["ok"] is True
    assert response["body"]["data"]["persisted"] is True
    assert response["body"]["data"]["output_path"] == str(output_path)
    assert Path(output_path).exists()
    assert output_path.read_text(encoding="utf-8").strip()
