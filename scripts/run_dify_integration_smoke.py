import json
from typing import Any, Dict, List, Optional

from fcf.api.dify_http_adapter import ROUTE_SINGLE, route_dify_http_request
from fcf.api.dify_response_templates import render_dify_user_response


def _sample_raw_market_data() -> Dict[str, Any]:
    return {
        "asset_class": "crypto",
        "symbol": "BTCUSDT",
        "venue": "binance",
        "market_type": "perp",
        "timestamp": "2026-06-30T00:00:00Z",
        "timeframe": "1m",
        "source": "dify_integration_smoke",
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


def _summarize_case(
    name: str,
    adapter_response: Optional[Dict[str, Any]],
    user_response: Dict[str, Any],
) -> Dict[str, Any]:
    body = {}
    if adapter_response is not None:
        body = adapter_response.get("body", {})

    return {
        "name": name,
        "adapter_http_status": None if adapter_response is None else adapter_response.get("http_status"),
        "adapter_ok": body.get("ok"),
        "user_response_type": user_response.get("response_type"),
        "user_title": user_response.get("title"),
    }


def run_integration_smoke() -> Dict[str, Any]:
    success_adapter_response = route_dify_http_request(
        "POST",
        ROUTE_SINGLE,
        {
            "correlation_id": "p3-d12-integration-success",
            "raw": _sample_raw_market_data(),
        },
    )
    success_user_response = render_dify_user_response(success_adapter_response)

    bad_raw = _sample_raw_market_data()
    bad_raw["last_price"] = "bad-number"

    error_adapter_response = route_dify_http_request(
        "POST",
        ROUTE_SINGLE,
        {
            "correlation_id": "p3-d12-integration-error",
            "raw": bad_raw,
        },
    )
    error_user_response = render_dify_user_response(error_adapter_response)

    refusal_user_response = render_dify_user_response(intent="place_real_order")

    cases: List[Dict[str, Any]] = [
        _summarize_case(
            "single_success_to_user_success",
            success_adapter_response,
            success_user_response,
        ),
        _summarize_case(
            "single_bad_input_to_user_error",
            error_adapter_response,
            error_user_response,
        ),
        _summarize_case(
            "forbidden_intent_to_safety_refusal",
            None,
            refusal_user_response,
        ),
    ]

    return {
        "status": "completed",
        "runner": "dify_adapter_response_integration_smoke",
        "case_count": len(cases),
        "cases": cases,
        "safe_boundary": {
            "no_real_exchange_api": True,
            "no_real_order_placement": True,
            "no_exchange_api_key_storage": True,
            "only_calls_controlled_wrappers": True,
            "does_not_claim_real_trade_success": True,
        },
    }


def main() -> None:
    print(json.dumps(run_integration_smoke(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
