from typing import Optional


ASSET_CLASS_CRYPTO = "crypto"
ASSET_CLASS_FX = "fx"
ASSET_CLASS_EQUITY = "equity"
ASSET_CLASS_FUTURES = "futures"
ASSET_CLASS_COMMODITY = "commodity"
ASSET_CLASS_RATES = "rates"
ASSET_CLASS_BOND = "bond"
ASSET_CLASS_INDEX = "index"
ASSET_CLASS_UNKNOWN = "unknown"

SUPPORTED_ASSET_CLASSES = {
    ASSET_CLASS_CRYPTO,
    ASSET_CLASS_FX,
    ASSET_CLASS_EQUITY,
    ASSET_CLASS_FUTURES,
    ASSET_CLASS_COMMODITY,
    ASSET_CLASS_RATES,
    ASSET_CLASS_BOND,
    ASSET_CLASS_INDEX,
    ASSET_CLASS_UNKNOWN,
}

ASSET_CLASS_ALIASES = {
    "crypto": ASSET_CLASS_CRYPTO,
    "cryptocurrency": ASSET_CLASS_CRYPTO,
    "digital_asset": ASSET_CLASS_CRYPTO,
    "coin": ASSET_CLASS_CRYPTO,
    "fx": ASSET_CLASS_FX,
    "forex": ASSET_CLASS_FX,
    "currency": ASSET_CLASS_FX,
    "equity": ASSET_CLASS_EQUITY,
    "stock": ASSET_CLASS_EQUITY,
    "share": ASSET_CLASS_EQUITY,
    "futures": ASSET_CLASS_FUTURES,
    "future": ASSET_CLASS_FUTURES,
    "commodity": ASSET_CLASS_COMMODITY,
    "commodities": ASSET_CLASS_COMMODITY,
    "rates": ASSET_CLASS_RATES,
    "rate": ASSET_CLASS_RATES,
    "bond": ASSET_CLASS_BOND,
    "bonds": ASSET_CLASS_BOND,
    "fixed_income": ASSET_CLASS_BOND,
    "index": ASSET_CLASS_INDEX,
    "indices": ASSET_CLASS_INDEX,
    "unknown": ASSET_CLASS_UNKNOWN,
}

MARKET_TYPE_SPOT = "spot"
MARKET_TYPE_PERPETUAL = "perpetual"
MARKET_TYPE_FUTURE = "future"
MARKET_TYPE_OPTION = "option"
MARKET_TYPE_CASH = "cash"
MARKET_TYPE_FORWARD = "forward"
MARKET_TYPE_SWAP = "swap"
MARKET_TYPE_CFD = "cfd"
MARKET_TYPE_UNKNOWN = "unknown"

SUPPORTED_MARKET_TYPES = {
    MARKET_TYPE_SPOT,
    MARKET_TYPE_PERPETUAL,
    MARKET_TYPE_FUTURE,
    MARKET_TYPE_OPTION,
    MARKET_TYPE_CASH,
    MARKET_TYPE_FORWARD,
    MARKET_TYPE_SWAP,
    MARKET_TYPE_CFD,
    MARKET_TYPE_UNKNOWN,
}

MARKET_TYPE_ALIASES = {
    "spot": MARKET_TYPE_SPOT,
    "perp": MARKET_TYPE_PERPETUAL,
    "perpetual": MARKET_TYPE_PERPETUAL,
    "perpetual_swap": MARKET_TYPE_PERPETUAL,
    "future": MARKET_TYPE_FUTURE,
    "futures": MARKET_TYPE_FUTURE,
    "option": MARKET_TYPE_OPTION,
    "options": MARKET_TYPE_OPTION,
    "cash": MARKET_TYPE_CASH,
    "forward": MARKET_TYPE_FORWARD,
    "swap": MARKET_TYPE_SWAP,
    "cfd": MARKET_TYPE_CFD,
    "unknown": MARKET_TYPE_UNKNOWN,
}


def _normalize_string(value: Optional[str]) -> str:
    if value is None:
        return ""

    return str(value).strip().lower().replace("-", "_").replace(" ", "_")


def normalize_asset_class(value: Optional[str]) -> str:
    normalized = _normalize_string(value)

    if not normalized:
        return ASSET_CLASS_UNKNOWN

    return ASSET_CLASS_ALIASES.get(normalized, ASSET_CLASS_UNKNOWN)


def normalize_market_type(value: Optional[str]) -> str:
    normalized = _normalize_string(value)

    if not normalized:
        return MARKET_TYPE_UNKNOWN

    return MARKET_TYPE_ALIASES.get(normalized, MARKET_TYPE_UNKNOWN)


def is_supported_asset_class(value: Optional[str]) -> bool:
    return normalize_asset_class(value) != ASSET_CLASS_UNKNOWN


def is_supported_market_type(value: Optional[str]) -> bool:
    return normalize_market_type(value) != MARKET_TYPE_UNKNOWN


def validate_asset_class(value: Optional[str]) -> str:
    normalized = normalize_asset_class(value)

    if normalized == ASSET_CLASS_UNKNOWN:
        raise ValueError(f"unsupported asset_class: {value}")

    return normalized


def validate_market_type(value: Optional[str]) -> str:
    normalized = normalize_market_type(value)

    if normalized == MARKET_TYPE_UNKNOWN:
        raise ValueError(f"unsupported market_type: {value}")

    return normalized
