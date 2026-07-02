from typing import Any


PAPER_ONLY_FLAGS = {
    "paper_only": True,
    "real_exchange_api": False,
    "real_brokerage_api": False,
    "real_api_key_required": False,
    "wallet_private_key_required": False,
    "real_order": False,
    "real_execution": False,
    "real_balance": False,
    "real_position": False,
    "real_money_impact": False,
    "operator_review_required": True,
}


ASSET_CLASS_TAXONOMY = {
    "crypto": {
        "label": "Crypto Asset",
        "example_symbols": ["BTCUSDT", "ETHUSDT"],
        "adapter_type": "paper_crypto_adapter",
    },
    "stock": {
        "label": "Stock",
        "example_symbols": ["AAPL", "MSFT"],
        "adapter_type": "paper_stock_adapter",
    },
    "etf": {
        "label": "ETF",
        "example_symbols": ["SPY", "QQQ"],
        "adapter_type": "paper_etf_adapter",
    },
    "fx": {
        "label": "Foreign Exchange",
        "example_symbols": ["EURUSD", "USDJPY"],
        "adapter_type": "paper_fx_adapter",
    },
    "commodity": {
        "label": "Commodity",
        "example_symbols": ["XAUUSD", "WTI"],
        "adapter_type": "paper_commodity_adapter",
    },
}


def paper_flags() -> dict[str, Any]:
    return dict(PAPER_ONLY_FLAGS)


def get_asset_class_taxonomy() -> dict[str, Any]:
    return {
        "ok": True,
        "type": "asset_class_taxonomy",
        "supported_asset_classes": sorted(ASSET_CLASS_TAXONOMY.keys()),
        "taxonomy": ASSET_CLASS_TAXONOMY,
        "current_role": "multi_market_paper_contract_only",
        "decision": "taxonomy_only_no_real_market_connection",
        **paper_flags(),
    }


def validate_asset_class(asset_class: str) -> str:
    value = str(asset_class).strip().lower()
    if value not in ASSET_CLASS_TAXONOMY:
        raise ValueError("unsupported asset_class")
    return value


def normalize_market_name(market: str) -> str:
    value = str(market).strip().lower().replace(" ", "_")
    if not value:
        raise ValueError("market is required")
    return value


def normalize_symbol_for_asset_class(symbol: str, asset_class: str) -> dict[str, Any]:
    asset = validate_asset_class(asset_class)
    raw = str(symbol).strip().upper()

    if not raw:
        raise ValueError("symbol is required")

    if asset in {"crypto", "fx"}:
        normalized = raw.replace("/", "").replace("-", "").replace("_", "")
    else:
        normalized = raw.replace(" ", "")

    if not normalized:
        raise ValueError("symbol is required")

    return {
        "ok": True,
        "type": "multi_market_symbol_normalization",
        "raw_symbol": str(symbol),
        "symbol": normalized,
        "asset_class": asset,
        "decision": "symbol_normalized_for_paper_only_contract",
        **paper_flags(),
    }


def positive_float(value: Any, field_name: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(field_name + " must be a positive number") from exc

    if number <= 0:
        raise ValueError(field_name + " must be a positive number")

    return number


def build_paper_market_adapter_contract(asset_class: str, market: str) -> dict[str, Any]:
    asset = validate_asset_class(asset_class)
    normalized_market = normalize_market_name(market)
    taxonomy = ASSET_CLASS_TAXONOMY[asset]

    return {
        "ok": True,
        "type": "paper_market_adapter_contract",
        "asset_class": asset,
        "market": normalized_market,
        "adapter_type": taxonomy["adapter_type"],
        "adapter_status": "paper_contract_only",
        "required_input_fields": ["symbol", "asset_class", "market", "price", "reference_price"],
        "blocked_real_world_integrations": [
            "real_exchange_api",
            "real_brokerage_api",
            "real_api_key",
            "wallet_private_key",
            "real_order",
            "real_execution",
            "real_balance",
            "real_position",
            "real_money_impact",
        ],
        "decision": "adapter_contract_only_no_real_connection",
        **paper_flags(),
    }


def build_multi_market_paper_input(
    symbol: str,
    asset_class: str,
    market: str,
    price: Any,
    reference_price: Any,
) -> dict[str, Any]:
    normalized = normalize_symbol_for_asset_class(symbol, asset_class)
    adapter = build_paper_market_adapter_contract(asset_class, market)

    return {
        "ok": True,
        "type": "multi_market_paper_input",
        "symbol": normalized["symbol"],
        "raw_symbol": str(symbol),
        "asset_class": normalized["asset_class"],
        "market": adapter["market"],
        "price": positive_float(price, "price"),
        "reference_price": positive_float(reference_price, "reference_price"),
        "symbol_normalization": normalized,
        "adapter_contract": adapter,
        "decision": "multi_market_input_paper_only",
        **paper_flags(),
    }


def build_multi_market_batch_contract(items: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    if not items:
        raise ValueError("items must not be empty")

    normalized_items = []
    for item in items:
        normalized_items.append(build_multi_market_paper_input(
            item.get("symbol", ""),
            item.get("asset_class", ""),
            item.get("market", ""),
            item.get("price"),
            item.get("reference_price"),
        ))

    asset_class_counts: dict[str, int] = {}
    market_counts: dict[str, int] = {}

    for item in normalized_items:
        asset = item["asset_class"]
        market = item["market"]
        asset_class_counts[asset] = asset_class_counts.get(asset, 0) + 1
        market_counts[market] = market_counts.get(market, 0) + 1

    return {
        "ok": True,
        "type": "multi_market_batch_contract",
        "count": len(normalized_items),
        "symbols": [item["symbol"] for item in normalized_items],
        "asset_classes": sorted(asset_class_counts.keys()),
        "asset_class_counts": asset_class_counts,
        "market_counts": market_counts,
        "items": normalized_items,
        "decision": "multi_market_batch_paper_only",
        **paper_flags(),
    }


def extract_analysis_compatible_items(batch_contract: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(batch_contract, dict):
        raise ValueError("batch_contract must be a dict")
    if batch_contract.get("type") != "multi_market_batch_contract":
        raise ValueError("batch_contract type is invalid")
    if batch_contract.get("ok") is not True:
        raise ValueError("batch_contract must be ok")

    return [
        {
            "symbol": item["symbol"],
            "price": item["price"],
            "reference_price": item["reference_price"],
        }
        for item in batch_contract["items"]
    ]
