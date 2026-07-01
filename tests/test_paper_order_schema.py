import pytest

from fcf.paper.paper_order_schema import (
    describe_paper_order_schema,
    normalize_order_type,
    normalize_paper_order,
    normalize_side,
    normalize_time_in_force,
    validate_paper_order,
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
        "source": "unit_test_paper_order",
        "correlation_id": "p5-d2-paper-order",
        "metadata": {
            "note": "paper only",
        },
    }


def test_describe_paper_order_schema_declares_boundary():
    schema = describe_paper_order_schema()

    assert schema["schema"] == "paper_order_schema"
    assert schema["schema_version"] == "0.1.0"
    assert "asset_class" in schema["required_fields"]
    assert "quantity" in schema["required_fields"]
    assert schema["forced_safety_fields"]["execution_mode"] == "paper"
    assert schema["forced_safety_fields"]["real_order"] is False
    assert schema["safe_boundary"]["no_real_exchange_api"] is True
    assert schema["safe_boundary"]["no_real_order_placement"] is True


def test_normalize_side_aliases():
    assert normalize_side("buy") == "buy"
    assert normalize_side("BUY") == "buy"
    assert normalize_side("long") == "buy"
    assert normalize_side("sell") == "sell"
    assert normalize_side("SHORT") == "sell"

    with pytest.raises(ValueError, match="side"):
        normalize_side("not-real")


def test_normalize_order_type_aliases():
    assert normalize_order_type("market") == "market"
    assert normalize_order_type("LIMIT") == "limit"
    assert normalize_order_type("stop") == "stop"
    assert normalize_order_type("stop-limit") == "stop_limit"
    assert normalize_order_type("stop_limit") == "stop_limit"

    with pytest.raises(ValueError, match="order_type"):
        normalize_order_type("not-real")


def test_normalize_time_in_force_aliases():
    assert normalize_time_in_force(None) == "GTC"
    assert normalize_time_in_force("") == "GTC"
    assert normalize_time_in_force("gtc") == "GTC"
    assert normalize_time_in_force("IOC") == "IOC"
    assert normalize_time_in_force("fok") == "FOK"
    assert normalize_time_in_force("day") == "DAY"

    with pytest.raises(ValueError, match="time_in_force"):
        normalize_time_in_force("not-real")


def test_normalize_paper_order_success_and_forces_safety_fields():
    normalized = normalize_paper_order(_sample_paper_order())

    assert normalized["asset_class"] == "crypto"
    assert normalized["symbol"] == "BTCUSDT"
    assert normalized["venue"] == "binance"
    assert normalized["market_type"] == "perpetual"
    assert normalized["side"] == "buy"
    assert normalized["order_type"] == "limit"
    assert normalized["quantity"] == 0.25
    assert normalized["price"] == 60050.5
    assert normalized["time_in_force"] == "GTC"
    assert normalized["execution_mode"] == "paper"
    assert normalized["real_order"] is False
    assert normalized["real_exchange_api"] is False
    assert normalized["real_money_impact"] is False


def test_validate_paper_order_returns_stable_dict():
    result = validate_paper_order(_sample_paper_order())

    assert result["ok"] is True
    assert result["schema"] == "paper_order_schema"
    assert result["schema_version"] == "0.1.0"
    assert result["error"] is None
    assert result["data"]["symbol"] == "BTCUSDT"
    assert result["data"]["execution_mode"] == "paper"
    assert result["data"]["real_order"] is False


def test_missing_required_field_raises_value_error():
    raw = _sample_paper_order()
    del raw["quantity"]

    with pytest.raises(ValueError, match="missing required fields: quantity"):
        normalize_paper_order(raw)


def test_bad_payload_type_raises_value_error():
    with pytest.raises(ValueError, match="paper order must be a dict"):
        normalize_paper_order(None)


def test_bad_quantity_raises_value_error():
    raw = _sample_paper_order()
    raw["quantity"] = "bad-number"

    with pytest.raises(ValueError, match="quantity must be a valid number"):
        normalize_paper_order(raw)


def test_non_positive_quantity_raises_value_error():
    raw = _sample_paper_order()
    raw["quantity"] = "0"

    with pytest.raises(ValueError, match="quantity must be greater than 0"):
        normalize_paper_order(raw)


def test_bad_price_raises_value_error():
    raw = _sample_paper_order()
    raw["price"] = "bad-number"

    with pytest.raises(ValueError, match="price must be a valid number"):
        normalize_paper_order(raw)


def test_non_positive_price_raises_value_error():
    raw = _sample_paper_order()
    raw["price"] = "-1"

    with pytest.raises(ValueError, match="price must be greater than 0"):
        normalize_paper_order(raw)


def test_price_can_be_omitted():
    raw = _sample_paper_order()
    del raw["price"]

    normalized = normalize_paper_order(raw)

    assert "price" not in normalized
    assert normalized["quantity"] == 0.25
    assert normalized["execution_mode"] == "paper"


def test_metadata_must_be_dict():
    raw = _sample_paper_order()
    raw["metadata"] = "not-dict"

    with pytest.raises(ValueError, match="metadata"):
        normalize_paper_order(raw)
