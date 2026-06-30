import json
from typing import Any, Dict, List

from fcf.api.dify_http_adapter import (
    ROUTE_BATCH,
    ROUTE_CONTRACT,
    ROUTE_SINGLE,
    route_dify_http_request,
)


def _sample_raw_market_data() -> Dict[str, Any]:
    return {
        "asset_class": "crypto",
        "symbol": "BTCUSDT",
        "venue": "binance",
        "market_type": "perp",
        "timestamp": "2026-06-30T00:00:00Z",
        "timeframe": "1m",
        "source": "dify_http_adapter_smoke",
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


def _sample_batch_rows() -> List[Dict[str, Any]]:
    btc = _sample_raw_market_data()
    eth = _sample_raw_market_data()

    eth["symbol"] = "ETHUSDT"
    eth["market_type"] = "spot"
    eth["open"] = "3300"
    eth["high"] = "3310"
    eth["low"] = "3290"
    eth["close"] = "3305"
    eth["last_price"] = "3305"
    eth["volume"] = "900.25"
    eth["quote_volume"] = "2975626.25"
    eth["best_bid"] = "3304.9"
    eth["best_ask"] = "3305.1"
    eth["bid_depth"] = "500"
    eth["ask_depth"] = "450"

    return [btc, eth]


def _case_summary(name: str, response: Dict[str, Any]) -> Dict[str, Any]:
    body = response.get("body", {})
    error = body.get("error")

    return {
        "name": name,
        "http_status": response.get("http_status"),
        "ok": body.get("ok"),
        "api": body.get("api"),
        "error_type": None if error is None else error.get("type"),
    }


def run_smoke() -> Dict[str, Any]:
    bad_raw = _sample_raw_market_data()
    bad_raw["last_price"] = "bad-number"

    responses = [
        (
            "contract",
            route_dify_http_request("GET", ROUTE_CONTRACT),
        ),
        (
            "single_success",
            route_dify_http_request(
                "POST",
                ROUTE_SINGLE,
                {
                    "correlation_id": "p3-d10-smoke-single",
                    "raw": _sample_raw_market_data(),
                },
            ),
        ),
        (
            "batch_success",
            route_dify_http_request(
                "POST",
                ROUTE_BATCH,
                {
                    "correlation_id": "p3-d10-smoke-batch",
                    "rows": _sample_batch_rows(),
                },
            ),
        ),
        (
            "single_bad_input",
            route_dify_http_request(
                "POST",
                ROUTE_SINGLE,
                {
                    "correlation_id": "p3-d10-smoke-bad-input",
                    "raw": bad_raw,
                },
            ),
        ),
        (
            "unknown_route",
            route_dify_http_request("GET", "/api/v1/not-real"),
        ),
    ]

    cases = [_case_summary(name, response) for name, response in responses]

    return {
        "status": "completed",
        "runner": "dify_http_adapter_smoke",
        "case_count": len(cases),
        "cases": cases,
        "safe_boundary": {
            "no_real_exchange_api": True,
            "no_real_order_placement": True,
            "no_exchange_api_key_storage": True,
            "only_calls_controlled_wrappers": True,
        },
    }


def main() -> None:
    print(json.dumps(run_smoke(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
