import pytest

from fcf.schemas.raw_market_input_schema import normalize_raw_market_input


def _sample_raw_market_data():
    return {
        "asset_class": "Crypto",
        "symbol": "btcusdt",
        "venue": "BINANCE",
        "market_type": "PERP",
        "timestamp": "2026-06-30T00:00:00Z",
        "timeframe": "1m",
        "source": "unit_test_schema_catalog_integration",
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


def test_missing_required_field_uses_catalog_message():
    raw = _sample_raw_market_data()
    del raw["last_price"]

    with pytest.raises(ValueError, match="missing required fields: last_price"):
        normalize_raw_market_input(raw)


def test_bad_asset_class_uses_catalog_message():
    raw = _sample_raw_market_data()
    raw["asset_class"] = "not-real"

    with pytest.raises(ValueError, match="asset_class is not supported: not-real"):
        normalize_raw_market_input(raw)


def test_bad_market_type_uses_catalog_message():
    raw = _sample_raw_market_data()
    raw["market_type"] = "not-real"

    with pytest.raises(ValueError, match="market_type is not supported: not-real"):
        normalize_raw_market_input(raw)


def test_bad_number_uses_catalog_message():
    raw = _sample_raw_market_data()
    raw["last_price"] = "bad-number"

    with pytest.raises(ValueError, match="last_price must be a valid number"):
        normalize_raw_market_input(raw)


def test_bad_positive_number_uses_catalog_message():
    raw = _sample_raw_market_data()
    raw["last_price"] = "-1"

    with pytest.raises(ValueError, match="last_price must be greater than 0"):
        normalize_raw_market_input(raw)


def test_bad_non_negative_number_uses_catalog_message():
    raw = _sample_raw_market_data()
    raw["volume"] = "-1"

    with pytest.raises(ValueError, match="volume must be greater than or equal to 0"):
        normalize_raw_market_input(raw)


def test_bad_spread_uses_catalog_message():
    raw = _sample_raw_market_data()
    raw["best_bid"] = "60060"
    raw["best_ask"] = "60050"

    with pytest.raises(ValueError, match="best_bid must be less than or equal to best_ask"):
        normalize_raw_market_input(raw)


def test_bad_payload_type_uses_catalog_message():
    with pytest.raises(ValueError, match="raw market input must be a dict"):
        normalize_raw_market_input(None)
