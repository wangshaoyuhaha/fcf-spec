from fcf.paper.sandbox_execution_engine import (
    EVENT_SANDBOX_FILLED,
    EVENT_SANDBOX_PARTIAL_FILLED,
    EVENT_SANDBOX_REJECTED,
    MODE_SIMULATED_FILL,
    MODE_SIMULATED_REJECT,
    describe_sandbox_execution_engine,
    execute_sandbox_order,
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
        "source": "unit_test_sandbox_execution",
        "correlation_id": "p5-d3-sandbox-execution",
        "metadata": {
            "note": "paper only",
        },
        "real_order": True,
        "real_exchange_api": True,
        "real_money_impact": True,
    }


def test_describe_sandbox_execution_engine_declares_safe_boundary():
    description = describe_sandbox_execution_engine()

    assert description["engine"] == "sandbox_execution_engine"
    assert description["engine_version"] == "0.1.0"
    assert MODE_SIMULATED_FILL in description["supported_simulation_modes"]
    assert MODE_SIMULATED_REJECT in description["supported_simulation_modes"]
    assert EVENT_SANDBOX_FILLED in description["event_names"]
    assert EVENT_SANDBOX_REJECTED in description["event_names"]
    assert description["safe_boundary"]["execution_mode"] == "paper"
    assert description["safe_boundary"]["real_order"] is False
    assert description["safe_boundary"]["real_execution"] is False
    assert description["safe_boundary"]["no_real_exchange_api"] is True


def test_execute_sandbox_order_simulated_fill_full_order():
    response = execute_sandbox_order(
        raw_order=_sample_paper_order(),
        simulation_mode="simulated_fill",
    )

    assert response["ok"] is True
    assert response["engine"] == "sandbox_execution_engine"
    assert response["error"] is None

    data = response["data"]

    assert data["status"] == "completed"
    assert data["simulation_mode"] == "simulated_fill"
    assert data["execution_status"] == "filled"
    assert data["event_name"] == EVENT_SANDBOX_FILLED
    assert data["filled_quantity"] == 0.25
    assert data["remaining_quantity"] == 0.0
    assert data["fill_price"] == 60050.5
    assert data["notional"] == 0.25 * 60050.5
    assert data["execution_mode"] == "paper"
    assert data["real_order"] is False
    assert data["real_execution"] is False
    assert data["real_exchange_api"] is False
    assert data["real_money_impact"] is False
    assert data["paper_order"]["real_order"] is False


def test_execute_sandbox_order_simulated_fill_partial_order():
    response = execute_sandbox_order(
        raw_order=_sample_paper_order(),
        simulation_mode="simulated_fill",
        filled_quantity=0.10,
        fill_price=60051.0,
    )

    assert response["ok"] is True

    data = response["data"]

    assert data["execution_status"] == "partial_filled"
    assert data["event_name"] == EVENT_SANDBOX_PARTIAL_FILLED
    assert data["filled_quantity"] == 0.10
    assert data["remaining_quantity"] == 0.15
    assert data["fill_price"] == 60051.0
    assert data["notional"] == 0.10 * 60051.0
    assert data["real_execution"] is False


def test_execute_sandbox_order_simulated_reject():
    response = execute_sandbox_order(
        raw_order=_sample_paper_order(),
        simulation_mode="simulated_reject",
        reject_reason="policy denied in sandbox",
    )

    assert response["ok"] is True

    data = response["data"]

    assert data["simulation_mode"] == "simulated_reject"
    assert data["execution_status"] == "rejected"
    assert data["event_name"] == EVENT_SANDBOX_REJECTED
    assert data["filled_quantity"] == 0.0
    assert data["remaining_quantity"] == 0.25
    assert data["fill_price"] is None
    assert data["notional"] == 0.0
    assert data["reject_reason"] == "policy denied in sandbox"
    assert data["real_order"] is False
    assert data["real_execution"] is False


def test_execute_sandbox_order_rejects_bad_simulation_mode():
    response = execute_sandbox_order(
        raw_order=_sample_paper_order(),
        simulation_mode="real_execution",
    )

    assert response["ok"] is False
    assert response["data"] is None
    assert response["error"]["type"] == "ValueError"
    assert "simulation_mode" in response["error"]["message"]


def test_execute_sandbox_order_rejects_bad_paper_order():
    bad_order = _sample_paper_order()
    bad_order["quantity"] = "-1"

    response = execute_sandbox_order(
        raw_order=bad_order,
        simulation_mode="simulated_fill",
    )

    assert response["ok"] is False
    assert response["data"] is None
    assert response["error"]["type"] == "ValueError"
    assert "quantity" in response["error"]["message"]


def test_execute_sandbox_order_rejects_overfill():
    response = execute_sandbox_order(
        raw_order=_sample_paper_order(),
        simulation_mode="simulated_fill",
        filled_quantity=1.0,
    )

    assert response["ok"] is False
    assert response["data"] is None
    assert response["error"]["type"] == "ValueError"
    assert "filled_quantity" in response["error"]["message"]


def test_execute_sandbox_order_requires_fill_price_without_order_price():
    order = _sample_paper_order()
    del order["price"]
    order["order_type"] = "market"

    response = execute_sandbox_order(
        raw_order=order,
        simulation_mode="simulated_fill",
    )

    assert response["ok"] is False
    assert response["data"] is None
    assert response["error"]["type"] == "ValueError"
    assert "fill_price" in response["error"]["message"]


def test_execute_sandbox_order_allows_market_order_with_explicit_fill_price():
    order = _sample_paper_order()
    del order["price"]
    order["order_type"] = "market"

    response = execute_sandbox_order(
        raw_order=order,
        simulation_mode="simulated_fill",
        fill_price=60049.0,
    )

    assert response["ok"] is True
    assert response["data"]["execution_status"] == "filled"
    assert response["data"]["fill_price"] == 60049.0
    assert response["data"]["real_execution"] is False


def test_execute_sandbox_order_rejects_bad_fill_price():
    response = execute_sandbox_order(
        raw_order=_sample_paper_order(),
        simulation_mode="simulated_fill",
        fill_price=-1,
    )

    assert response["ok"] is False
    assert response["error"]["type"] == "ValueError"
    assert "fill_price" in response["error"]["message"]
