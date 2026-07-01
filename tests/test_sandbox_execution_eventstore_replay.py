from pathlib import Path

from fcf.paper.sandbox_execution_engine import (
    EVENT_SANDBOX_FILLED,
    EVENT_SANDBOX_PARTIAL_FILLED,
    EVENT_SANDBOX_REJECTED,
    execute_sandbox_order_with_eventstore,
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
        "source": "unit_test_sandbox_eventstore",
        "correlation_id": "p5-d4-sandbox-eventstore",
        "metadata": {
            "note": "paper only",
        },
        "real_order": True,
        "real_exchange_api": True,
        "real_money_impact": True,
    }


def test_sandbox_execution_full_fill_writes_eventstore_and_replay():
    response = execute_sandbox_order_with_eventstore(
        raw_order=_sample_paper_order(),
        simulation_mode="simulated_fill",
    )

    assert response["ok"] is True
    assert response["engine"] == "sandbox_execution_engine"
    assert response["error"] is None

    data = response["data"]

    assert data["execution_status"] == "filled"
    assert data["event_name"] == EVENT_SANDBOX_FILLED
    assert data["event_count"] == 1
    assert data["event_names"] == [EVENT_SANDBOX_FILLED]
    assert data["persisted"] is False
    assert data["output_path"] is None
    assert data["replay"]["status"] == "completed"
    assert data["replay"]["event_count"] == 1
    assert data["replay"]["event_names"] == [EVENT_SANDBOX_FILLED]
    assert data["execution_mode"] == "paper"
    assert data["real_order"] is False
    assert data["real_execution"] is False
    assert data["real_exchange_api"] is False
    assert data["real_money_impact"] is False


def test_sandbox_execution_partial_fill_writes_eventstore_and_replay():
    response = execute_sandbox_order_with_eventstore(
        raw_order=_sample_paper_order(),
        simulation_mode="simulated_fill",
        filled_quantity=0.10,
        fill_price=60051.0,
    )

    assert response["ok"] is True

    data = response["data"]

    assert data["execution_status"] == "partial_filled"
    assert data["event_name"] == EVENT_SANDBOX_PARTIAL_FILLED
    assert data["event_count"] == 1
    assert data["event_names"] == [EVENT_SANDBOX_PARTIAL_FILLED]
    assert data["replay"]["event_count"] == 1
    assert data["replay"]["event_names"] == [EVENT_SANDBOX_PARTIAL_FILLED]
    assert data["real_execution"] is False


def test_sandbox_execution_reject_writes_eventstore_and_replay():
    response = execute_sandbox_order_with_eventstore(
        raw_order=_sample_paper_order(),
        simulation_mode="simulated_reject",
        reject_reason="policy denied in sandbox",
    )

    assert response["ok"] is True

    data = response["data"]

    assert data["execution_status"] == "rejected"
    assert data["event_name"] == EVENT_SANDBOX_REJECTED
    assert data["event_count"] == 1
    assert data["event_names"] == [EVENT_SANDBOX_REJECTED]
    assert data["replay"]["event_names"] == [EVENT_SANDBOX_REJECTED]
    assert data["reject_reason"] == "policy denied in sandbox"
    assert data["real_order"] is False
    assert data["real_execution"] is False


def test_sandbox_execution_can_persist_jsonl(tmp_path):
    output_path = tmp_path / "sandbox_execution.jsonl"

    response = execute_sandbox_order_with_eventstore(
        raw_order=_sample_paper_order(),
        simulation_mode="simulated_fill",
        output_path=str(output_path),
    )

    assert response["ok"] is True

    data = response["data"]

    assert data["persisted"] is True
    assert data["output_path"] == str(output_path)
    assert Path(output_path).exists()
    assert output_path.read_text(encoding="utf-8").strip()


def test_bad_paper_order_returns_error_without_eventstore_summary():
    bad_order = _sample_paper_order()
    bad_order["quantity"] = "-1"

    response = execute_sandbox_order_with_eventstore(
        raw_order=bad_order,
        simulation_mode="simulated_fill",
    )

    assert response["ok"] is False
    assert response["data"] is None
    assert response["error"]["type"] == "ValueError"
    assert "quantity" in response["error"]["message"]
