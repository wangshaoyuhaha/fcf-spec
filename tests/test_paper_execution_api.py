from pathlib import Path

from fcf.api.paper_execution_api import (
    describe_paper_execution_api,
    handle_paper_execution,
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
        "source": "unit_test_paper_execution_api",
        "correlation_id": "p5-d5-paper-execution-api",
        "metadata": {
            "note": "paper only",
        },
    }


def test_describe_paper_execution_api_declares_stable_contract_and_boundary():
    contract = describe_paper_execution_api()

    assert contract["api"] == "paper_execution_api"
    assert contract["api_version"] == "0.1.0"
    assert "handle_paper_execution" in contract["supported_handlers"]
    assert "simulated_fill" in contract["supported_simulation_modes"]
    assert "simulated_reject" in contract["supported_simulation_modes"]
    assert contract["stable_response_fields"] == [
        "ok",
        "api",
        "api_version",
        "error",
        "data",
    ]
    assert contract["safe_boundary"]["execution_mode"] == "paper"
    assert contract["safe_boundary"]["real_order"] is False
    assert contract["safe_boundary"]["real_execution"] is False
    assert contract["safe_boundary"]["no_real_exchange_api"] is True
    assert contract["safe_boundary"]["only_calls_sandbox_execution_engine"] is True


def test_handle_paper_execution_simulated_fill_returns_stable_success():
    response = handle_paper_execution(
        raw_order=_sample_paper_order(),
        simulation_mode="simulated_fill",
    )

    assert response["ok"] is True
    assert response["api"] == "paper_execution_api"
    assert response["api_version"] == "0.1.0"
    assert response["error"] is None

    data = response["data"]

    assert data["status"] == "completed"
    assert data["execution_status"] == "filled"
    assert data["event_name"] == "fcf.sandbox.execution.filled"
    assert data["event_count"] == 1
    assert data["replay"]["status"] == "completed"
    assert data["execution_mode"] == "paper"
    assert data["real_order"] is False
    assert data["real_execution"] is False
    assert data["real_exchange_api"] is False
    assert data["real_money_impact"] is False


def test_handle_paper_execution_simulated_partial_fill_returns_success():
    response = handle_paper_execution(
        raw_order=_sample_paper_order(),
        simulation_mode="simulated_fill",
        filled_quantity=0.10,
        fill_price=60051.0,
    )

    assert response["ok"] is True

    data = response["data"]

    assert data["execution_status"] == "partial_filled"
    assert data["event_name"] == "fcf.sandbox.execution.partial_filled"
    assert data["filled_quantity"] == 0.10
    assert data["remaining_quantity"] == 0.15
    assert data["fill_price"] == 60051.0
    assert data["real_execution"] is False


def test_handle_paper_execution_simulated_reject_returns_stable_success():
    response = handle_paper_execution(
        raw_order=_sample_paper_order(),
        simulation_mode="simulated_reject",
        reject_reason="policy denied in wrapper test",
    )

    assert response["ok"] is True
    assert response["error"] is None

    data = response["data"]

    assert data["execution_status"] == "rejected"
    assert data["event_name"] == "fcf.sandbox.execution.rejected"
    assert data["reject_reason"] == "policy denied in wrapper test"
    assert data["filled_quantity"] == 0.0
    assert data["real_order"] is False
    assert data["real_execution"] is False


def test_handle_paper_execution_bad_order_returns_stable_error():
    raw_order = _sample_paper_order()
    raw_order["quantity"] = "-1"

    response = handle_paper_execution(
        raw_order=raw_order,
        simulation_mode="simulated_fill",
    )

    assert response["ok"] is False
    assert response["api"] == "paper_execution_api"
    assert response["api_version"] == "0.1.0"
    assert response["data"] is None
    assert response["error"]["type"] == "ValueError"
    assert "quantity" in response["error"]["message"]


def test_handle_paper_execution_bad_simulation_mode_returns_stable_error():
    response = handle_paper_execution(
        raw_order=_sample_paper_order(),
        simulation_mode="real_execution",
    )

    assert response["ok"] is False
    assert response["data"] is None
    assert response["error"]["type"] == "ValueError"
    assert "simulation_mode" in response["error"]["message"]


def test_handle_paper_execution_can_persist_jsonl(tmp_path):
    output_path = tmp_path / "paper_execution_api.jsonl"

    response = handle_paper_execution(
        raw_order=_sample_paper_order(),
        simulation_mode="simulated_fill",
        output_path=str(output_path),
    )

    assert response["ok"] is True
    assert response["data"]["persisted"] is True
    assert response["data"]["output_path"] == str(output_path)
    assert Path(output_path).exists()
    assert output_path.read_text(encoding="utf-8").strip()
