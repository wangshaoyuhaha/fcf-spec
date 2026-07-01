import pytest

from fcf.schemas.raw_market_input_schema import (
    describe_schema,
    normalize_asset_class,
    normalize_market_type,
    normalize_raw_market_input,
    validate_raw_market_input,
)


def _sample_raw_market_data():
    return {
        "asset_class": "Crypto",
        "symbol": "btcusdt",
        "venue": "BINANCE",
        "market_type": "perp",
        "timestamp": "2026-06-30T00:00:00Z",
        "timeframe": "1m",
        "source": "unit_test_schema",
        "source_type": "mock",
        "open": "60000",
        "high": "60100",
        "low": "59900",
        "close": "60050",
        "last_price": "60050",
        "volume": "120.5",
        "quote_volume": "7230000",
        "best_bid": "60049.5",
        "best_ask": "60050.5",
        "bid_depth": "100",
        "ask_depth": "80",
    }


def test_describe_schema_declares_boundary():
    schema = describe_schema()

    assert schema["schema"] == "raw_market_input_schema"
    assert "asset_class" in schema["required_fields"]
    assert "last_price" in schema["required_fields"]
    assert "best_bid" in schema["optional_number_fields"]
    assert schema["safe_boundary"]["no_real_exchange_api"] is True
    assert schema["safe_boundary"]["no_real_order_placement"] is True


def test_normalize_asset_class():
    assert normalize_asset_class("Crypto") == "crypto"
    assert normalize_asset_class("FX") == "fx"
    assert normalize_asset_class("Equities") == "equities"

    with pytest.raises(ValueError, match="asset_class"):
        normalize_asset_class("not-real")


def test_normalize_market_type():
    assert normalize_market_type("spot") == "spot"
    assert normalize_market_type("PERP") == "perpetual"
    assert normalize_market_type("perpetual") == "perpetual"
    assert normalize_market_type("futures") == "futures"
    assert normalize_market_type("options") == "option"

    with pytest.raises(ValueError, match="market_type"):
        normalize_market_type("not-real")


def test_normalize_raw_market_input_converts_strings_and_numbers():
    normalized = normalize_raw_market_input(_sample_raw_market_data())

    assert normalized["asset_class"] == "crypto"
    assert normalized["symbol"] == "BTCUSDT"
    assert normalized["venue"] == "binance"
    assert normalized["market_type"] == "perpetual"
    assert normalized["last_price"] == 60050.0
    assert normalized["volume"] == 120.5
    assert normalized["best_bid"] == 60049.5
    assert normalized["best_ask"] == 60050.5


def test_missing_required_field_raises_value_error():
    raw = _sample_raw_market_data()
    del raw["last_price"]

    with pytest.raises(ValueError, match="missing required fields"):
        normalize_raw_market_input(raw)


def test_empty_required_string_raises_value_error():
    raw = _sample_raw_market_data()
    raw["symbol"] = "   "

    with pytest.raises(ValueError, match="missing required fields"):
        normalize_raw_market_input(raw)


def test_bad_number_raises_value_error():
    raw = _sample_raw_market_data()
    raw["last_price"] = "bad-number"

    with pytest.raises(ValueError, match="last_price"):
        normalize_raw_market_input(raw)


def test_negative_last_price_raises_value_error():
    raw = _sample_raw_market_data()
    raw["last_price"] = "-1"

    with pytest.raises(ValueError, match="greater than 0"):
        normalize_raw_market_input(raw)


def test_negative_volume_raises_value_error():
    raw = _sample_raw_market_data()
    raw["volume"] = "-10"

    with pytest.raises(ValueError, match="volume"):
        normalize_raw_market_input(raw)


def test_invalid_spread_raises_value_error():
    raw = _sample_raw_market_data()
    raw["best_bid"] = "60051"
    raw["best_ask"] = "60050"

    with pytest.raises(ValueError, match="best_bid"):
        normalize_raw_market_input(raw)


def test_validate_raw_market_input_returns_stable_dict():
    result = validate_raw_market_input(_sample_raw_market_data())

    assert result["ok"] is True
    assert result["schema"] == "raw_market_input_schema"
    assert result["schema_version"] == "0.1.0"
    assert result["error"] is None
    assert result["data"]["symbol"] == "BTCUSDT"
    assert result["data"]["market_type"] == "perpetual"
