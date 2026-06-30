import pytest

from fcf.contracts.market_constants import (
    ASSET_CLASS_CRYPTO,
    ASSET_CLASS_EQUITY,
    ASSET_CLASS_FX,
    ASSET_CLASS_FUTURES,
    ASSET_CLASS_UNKNOWN,
    MARKET_TYPE_CASH,
    MARKET_TYPE_FUTURE,
    MARKET_TYPE_PERPETUAL,
    MARKET_TYPE_SPOT,
    MARKET_TYPE_UNKNOWN,
    is_supported_asset_class,
    is_supported_market_type,
    normalize_asset_class,
    normalize_market_type,
    validate_asset_class,
    validate_market_type,
)


def test_normalize_asset_class_supported_values():
    assert normalize_asset_class("crypto") == ASSET_CLASS_CRYPTO
    assert normalize_asset_class("CryptoCurrency") == ASSET_CLASS_CRYPTO
    assert normalize_asset_class("digital asset") == ASSET_CLASS_CRYPTO
    assert normalize_asset_class("FX") == ASSET_CLASS_FX
    assert normalize_asset_class("forex") == ASSET_CLASS_FX
    assert normalize_asset_class("stock") == ASSET_CLASS_EQUITY
    assert normalize_asset_class("share") == ASSET_CLASS_EQUITY
    assert normalize_asset_class("future") == ASSET_CLASS_FUTURES
    assert normalize_asset_class("futures") == ASSET_CLASS_FUTURES


def test_normalize_asset_class_unknown_values():
    assert normalize_asset_class(None) == ASSET_CLASS_UNKNOWN
    assert normalize_asset_class("") == ASSET_CLASS_UNKNOWN
    assert normalize_asset_class("not-a-real-asset") == ASSET_CLASS_UNKNOWN


def test_normalize_market_type_supported_values():
    assert normalize_market_type("spot") == MARKET_TYPE_SPOT
    assert normalize_market_type("perp") == MARKET_TYPE_PERPETUAL
    assert normalize_market_type("perpetual") == MARKET_TYPE_PERPETUAL
    assert normalize_market_type("perpetual swap") == MARKET_TYPE_PERPETUAL
    assert normalize_market_type("future") == MARKET_TYPE_FUTURE
    assert normalize_market_type("futures") == MARKET_TYPE_FUTURE
    assert normalize_market_type("cash") == MARKET_TYPE_CASH


def test_normalize_market_type_unknown_values():
    assert normalize_market_type(None) == MARKET_TYPE_UNKNOWN
    assert normalize_market_type("") == MARKET_TYPE_UNKNOWN
    assert normalize_market_type("not-a-real-market-type") == MARKET_TYPE_UNKNOWN


def test_supported_helpers():
    assert is_supported_asset_class("crypto") is True
    assert is_supported_asset_class("forex") is True
    assert is_supported_asset_class("not-real") is False

    assert is_supported_market_type("spot") is True
    assert is_supported_market_type("perp") is True
    assert is_supported_market_type("not-real") is False


def test_validate_asset_class_success_and_failure():
    assert validate_asset_class("crypto") == "crypto"
    assert validate_asset_class("forex") == "fx"

    with pytest.raises(ValueError):
        validate_asset_class("not-real")


def test_validate_market_type_success_and_failure():
    assert validate_market_type("spot") == "spot"
    assert validate_market_type("perp") == "perpetual"

    with pytest.raises(ValueError):
        validate_market_type("not-real")
